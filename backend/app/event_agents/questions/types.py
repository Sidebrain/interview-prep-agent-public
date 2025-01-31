import random
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from app.types.interview_concept_types import QuestionAndAnswer
from app.types.websocket_types import WebsocketFrame


class Questions(BaseModel):
    questions: list[QuestionAndAnswer]


class ProbeDirection(str, Enum):
    """Direction in which the conversation can grow."""

    DEEPER = "depth"  # Vertical growth
    BROADER = "breadth"  # Horizontal growth


def normalize_probabilities(
    depth_probability: Optional[float] = None,
    breadth_probability: Optional[float] = None,
) -> tuple[float, float]:
    """Normalize depth and breadth probabilities to sum to 1.0.

    If neither is provided, defaults to equal 0.5 probabilities.
    If only one is provided, sets the other to the complement.
    if both are provided normalizes them to sum to 1.0
    """
    if not depth_probability and not breadth_probability:
        # Default to equal probability
        depth_probability = 0.5
        breadth_probability = 0.5

    elif depth_probability and not breadth_probability:
        breadth_probability = 1 - depth_probability

    elif breadth_probability and not depth_probability:
        depth_probability = 1 - breadth_probability

    elif depth_probability and breadth_probability:
        # Normalize to sum to 1.0
        total = depth_probability + breadth_probability
        depth_probability = depth_probability / total
        breadth_probability = breadth_probability / total

    else:
        raise ValueError("Invalid probabilities")

    return depth_probability, breadth_probability


def choose_probe_direction(
    depth_probability: Optional[float] = None,
    breadth_probability: Optional[float] = None,
) -> ProbeDirection:
    """Sample a direction based on relative preference of depth vs breadth.

    Args:
        depth_probability: Probability of choosing depth.
        breadth_probability: Probability of choosing breadth.
    """

    depth_probability, breadth_probability = normalize_probabilities(
        depth_probability, breadth_probability
    )

    return random.choices(
        list(ProbeDirection),
        weights=[depth_probability, breadth_probability],
    )[0]


class ConversationalTurn(BaseModel):
    """A single turn in a conversation, representing one exchange."""

    question: Optional[QuestionAndAnswer] = None
    answer: WebsocketFrame
    parent: Optional["ConversationalTurn"] = None
    children: list["ConversationalTurn"] = []
    _depth: int = 0
    _breadth: int = 0

    @property
    def depth(self) -> int:
        """How deep this turn lies in the conversation."""
        return self._depth

    @property
    def breadth(self) -> int:
        """How broad this turn spans in the conversation."""
        return self._breadth

    def place_in_tree(self, depth: int, breadth: int) -> None:
        """Position this turn within the conversation structure."""
        self._depth = depth
        self._breadth = breadth

    def has_room_to_grow_deeper(self, max_depth: int) -> bool:
        """Check if conversation can continue deeper from here."""
        return self.depth < max_depth

    def has_room_to_grow_broader(self, max_breadth: int) -> bool:
        """Check if conversation can expand broader from here."""
        return len(self.siblings) < max_breadth

    @property
    def siblings(self) -> list["ConversationalTurn"]:
        """Other turns at the same level of conversation."""
        if not self.parent:
            return []
        return [
            child
            for child in self.parent.children
            if child.depth == self.depth
        ]

    def get_full_historic_context(self) -> list[dict[str, str]]:
        """Get the full context of this turn."""
        context: list[dict[str, str]] = []
        parent = self.get_parent()
        if parent:
            context = parent.get_full_historic_context()
        context.extend(self.get_context())
        return context

    def get_parent(self) -> Optional["ConversationalTurn"]:
        if not self.parent:
            return None
        return self.parent

    def get_context(self) -> list[dict[str, str]]:
        """Get the context of this turn."""
        context: list[dict[str, str]] = []
        answer_content = self.answer.frame.content or None
        question_content = (
            self.question.question if self.question else None
        )

        if not answer_content and not question_content:
            return []

        if question_content:
            context.append(
                {
                    "role": "assistant",
                    "content": question_content,
                }
            )

        if answer_content:
            context.append(
                {
                    "role": "user",
                    "content": answer_content,
                }
            )

        return context

    def grow_conversation(
        self,
        new_turn: "ConversationalTurn",
        tree: "ConversationTree",
        direction: ProbeDirection,
    ) -> bool:
        """Grow the conversation by adding a new turn."""
        # Handle the case where this turn becomes the root
        if not tree.root:
            new_turn.place_in_tree(depth=0, breadth=0)
            tree.root = new_turn
            tree.current_position = new_turn
            tree.record_growth(new_turn)
            return True

        # Normal case - add as child
        new_turn.parent = self

        if direction == ProbeDirection.DEEPER:
            return self._grow_deeper(new_turn, tree)
        return self._grow_broader(new_turn, tree)

    def _grow_deeper(
        self,
        new_turn: "ConversationalTurn",
        tree: "ConversationTree",
    ) -> bool:
        """Continue the conversation in depth."""
        if not self.has_room_to_grow_deeper(tree.max_depth):
            return False

        new_turn.place_in_tree(
            depth=self.depth + 1, breadth=self.breadth
        )
        self.children.append(new_turn)
        tree.record_growth(new_turn)
        return True

    def _grow_broader(
        self,
        new_turn: "ConversationalTurn",
        tree: "ConversationTree",
    ) -> bool:
        """Expand the conversation in breadth."""
        if not self.has_room_to_grow_broader(tree.max_breadth):
            return False

        new_turn.place_in_tree(
            depth=self.depth, breadth=self.breadth + 1
        )
        self.children.append(new_turn)
        tree.record_growth(new_turn)
        return True


class ConversationTree(BaseModel):
    """A structured conversation with controlled growth."""

    root: ConversationalTurn | None = None
    max_depth: int
    max_breadth: int
    current_depth: int = 0
    current_breadth: int = 0
    current_position: Optional[ConversationalTurn] = None

    def __init__(self, **data) -> None:  # type: ignore
        super().__init__(**data)
        self.current_position = self.root  # Start at root

    def move_to(self, turn: ConversationalTurn) -> bool:
        """Move current position to specified turn if it exists in the tree."""
        if self._is_turn_in_tree(turn):
            self.current_position = turn
            return True
        return False

    def _is_turn_in_tree(self, turn: ConversationalTurn) -> bool:
        """Check if a turn exists in the tree."""

        def search(node: ConversationalTurn) -> bool:
            if node == turn:
                return True
            return any(search(child) for child in node.children)

        return search(self.root) if self.root else False

    def move_up(self) -> bool:
        """Move to parent of current position."""
        if self.current_position and self.current_position.parent:
            self.current_position = self.current_position.parent
            return True
        return False

    def move_to_child(self, index: int) -> bool:
        """Move to specific child of current position."""
        if self.current_position and 0 <= index < len(
            self.current_position.children
        ):
            self.current_position = self.current_position.children[
                index
            ]
            return True
        return False

    def record_growth(self, turn: ConversationalTurn) -> None:
        """Record the tree's growth after adding a new turn."""
        self.current_depth = max(self.current_depth, turn.depth)
        self.current_breadth = max(self.current_breadth, turn.breadth)

    def _print_tree(
        self,
        node: Optional[ConversationalTurn] = None,
        level: int = 0,
        prefix: str = "",
    ) -> None:
        """Generate a pretty-printed visualization of the tree."""
        if node is None:
            if not self.root:
                print("Empty tree")
                return
            node = self.root
            print("\nConversation Tree Structure:")

        # Print current node
        marker = "└── " if prefix else ""
        current_marker = "* " if node == self.current_position else "  "
        question_text = (
            node.question.question if node.question else "No question"
        )
        print(
            f"{prefix}{marker}{current_marker}[D:{node.depth},B:{node.breadth}] {question_text[:50]}..."
        )

        # Print children
        for i, child in enumerate(node.children):
            is_last = i == len(node.children) - 1
            new_prefix = prefix + (
                "    "
                if prefix.endswith("└── ") or not prefix
                else "│   "
            )
            self._print_tree(child, level + 1, new_prefix)

    def add_turn(
        self,
        new_turn: ConversationalTurn,
        direction: ProbeDirection,
    ) -> bool:
        """Add a new turn to the conversation."""
        if not self.current_position:
            # First turn becomes root
            success = new_turn.grow_conversation(
                new_turn, self, direction
            )
        else:
            success = self.current_position.grow_conversation(
                new_turn, self, direction
            )

        if success:
            self.current_position = (
                new_turn  # Update current position to the new turn
            )

        print("\033[93m" + "#" * 100 + "\033[0m")
        # Replace model_dump_json with a simpler debug print
        print(
            {
                "current_depth": self.current_depth,
                "current_breadth": self.current_breadth,
                "has_root": self.root is not None,
                "current_position_depth": self.current_position.depth
                if self.current_position
                else None,
            }
        )
        print(success)
        print("\033[93m" + "#" * 100 + "\033[0m")

        # Print tree structure after addition
        if success:
            self._print_tree()

        return success

    @property
    def is_within_bounds(self) -> bool:
        """Verify if the conversation remains within intended bounds."""
        return (
            self.current_depth <= self.max_depth
            and self.current_breadth <= self.max_breadth
        )
