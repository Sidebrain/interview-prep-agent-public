from typing import Optional

from pydantic import BaseModel

from app.event_agents.conversations.turn import Turn
from app.event_agents.conversations.types import ProbeDirection


class Tree(BaseModel):
    """A structured conversation with controlled growth."""

    root: Optional[Turn] = None
    max_depth: int
    max_breadth: int
    current_depth: int = 0
    current_breadth: int = 0
    current_position: Optional[Turn] = None

    def __init__(self, **data) -> None:  # type: ignore
        super().__init__(**data)
        self.current_position = self.root

    def grow_conversation(
        self,
        new_turn: Turn,
        direction: ProbeDirection,
    ) -> bool:
        """Grow the conversation by adding a new turn."""
        if not self.current_position:
            return self._add_root(new_turn)

        if not self._has_room_to_grow(direction):
            return False

        return self._add_child(new_turn, direction)

    def _add_root(self, new_turn: Turn) -> bool:
        """Add the first turn as root."""
        self._place_turn(new_turn, depth=0, breadth=0)
        self.root = new_turn
        self.current_position = new_turn
        self.record_growth(new_turn)
        return True

    def _add_child(
        self, new_turn: Turn, direction: ProbeDirection
    ) -> bool:
        """Add a new turn as child of current position."""
        if not self.current_position:
            return False

        new_turn.parent = self.current_position

        if direction == ProbeDirection.DEEPER:
            depth = self.current_position.depth + 1
            breadth = self.current_position.breadth
        else:
            depth = self.current_position.depth
            breadth = self.current_position.breadth + 1

        if not self._has_room_to_grow(direction):
            return False

        self._place_turn(new_turn, depth, breadth)
        self.current_position.children.append(new_turn)
        self.current_position = new_turn
        self.record_growth(new_turn)
        return True

    def _has_room_to_grow(self, direction: ProbeDirection) -> bool:
        """Check if there's room to grow in the specified direction."""
        if not self.current_position:
            return True

        if direction == ProbeDirection.DEEPER:
            return self.current_position.depth < self.max_depth
        return (
            len(self._get_siblings(self.current_position))
            < self.max_breadth
        )

    def _get_siblings(self, turn: Turn) -> list[Turn]:
        """Get all turns at the same depth level."""
        if not turn.parent:
            return []
        return [
            child
            for child in turn.parent.children
            if child.depth == turn.depth
        ]

    def _place_turn(self, turn: Turn, depth: int, breadth: int) -> None:
        """Position a turn within the tree structure."""
        turn._depth = depth
        turn._breadth = breadth

    def record_growth(self, turn: Turn) -> None:
        """Record the tree's growth after adding a new turn."""
        self.current_depth = max(self.current_depth, turn.depth)
        self.current_breadth = max(self.current_breadth, turn.breadth)

    def move_to(self, turn: Turn) -> bool:
        """Move current position to specified turn if it exists in the tree."""
        if self._is_turn_in_tree(turn):
            self.current_position = turn
            return True
        return False

    def _is_turn_in_tree(self, turn: Turn) -> bool:
        """Check if a turn exists in the tree."""

        def search(node: Turn) -> bool:
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

    def _print_tree(
        self,
        node: Optional[Turn] = None,
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
        new_turn: Turn,
        direction: ProbeDirection,
    ) -> bool:
        """Add a new turn to the conversation."""
        success = self.grow_conversation(new_turn, direction)

        print("\033[93m" + "#" * 100 + "\033[0m")
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
