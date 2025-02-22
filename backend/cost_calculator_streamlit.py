import random
from dataclasses import asdict, dataclass
from typing import Dict, List, Literal, Tuple

import altair as alt
import pandas as pd
import streamlit as st


# ----------------- #
# Cost Calculator Code
# ----------------- #
@dataclass
class PricePerToken:
    type: Literal["input", "output"]
    tokens: int
    price: float


@dataclass
class Model:
    model_name: str
    input_price: PricePerToken
    output_price: PricePerToken


# Example Model
GPT4o = Model(
    model_name="gpt-4o",
    input_price=PricePerToken(type="input", tokens=int(1e6), price=2.5),
    output_price=PricePerToken(
        type="output", tokens=int(1e6), price=1.25
    ),
)


@dataclass
class TokenCosts:
    """Represents costs associated with token usage."""

    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float

    @property
    def as_dict(self) -> Dict[str, float]:
        return asdict(self)


class CostCalculator:
    """
    A utility class to simulate and calculate costs for an AI-driven interview process.
    Now supports optional "accumulative" modes for evaluation and question context.
    """

    def __init__(self, model: Model) -> None:
        self.model = model

        # Running totals
        self.running_total_cost = 0.0

        # For breakdown reporting
        self.turn_details: List[Dict] = []

        # Accumulative conversation context (user Q&A)
        self.accumulated_conversation_tokens = 0

        # NEW: For accumulative modes
        # - If accumulate_eval is True, we track total evaluation outputs so far
        # - If accumulate_question is True, we track total question outputs so far
        self.accumulated_evaluation_output_tokens = 0
        self.accumulated_question_output_tokens = 0

        # Placeholder for init / post
        self.init_cost = 0.0
        self.post_cost = 0.0

    # ----------------- #
    # Helper Price Functions
    # ----------------- #
    def _price_for_input_tokens(self, token_count: int) -> float:
        if token_count <= 0:
            return 0.0
        return token_count * (
            self.model.input_price.price / self.model.input_price.tokens
        )

    def _price_for_output_tokens(self, token_count: int) -> float:
        if token_count <= 0:
            return 0.0
        return token_count * (
            self.model.output_price.price
            / self.model.output_price.tokens
        )

    # ----------------- #
    # Initialization & Post-Processing
    # ----------------- #
    def initialization_cost(
        self,
        initial_question_tokens: int = 500,
        system_tokens: int = 800,
        is_ai_generated: bool = True,
    ) -> float:
        """
        One-time cost for setting up the interview.
        """
        if not is_ai_generated:
            self.init_cost = 0.0
            return 0.0

        # system prompt => input, initial questions => output
        cost_input = self._price_for_input_tokens(system_tokens)
        cost_output = self._price_for_output_tokens(
            initial_question_tokens
        )
        self.init_cost = cost_input + cost_output
        return self.init_cost

    def post_processing_cost(
        self, input_tokens: int = 500, output_tokens: int = 500
    ) -> float:
        """
        One-time cost for final summarization or packaging results.
        """
        cost_input = self._price_for_input_tokens(input_tokens)
        cost_output = self._price_for_output_tokens(output_tokens)
        self.post_cost = cost_input + cost_output
        return self.post_cost

    # ----------------- #
    # Evaluation
    # ----------------- #
    def _agent_evaluation_cost(
        self,
        agent_index: int,
        num_context_tokens: int,
        agent_system_tokens: int,
        output_tokens_range: Tuple[int, int],
    ) -> Dict[str, float]:
        """
        Helper for a single agent's evaluation cost.
        input_tokens = user conversation context + agent system + possibly evaluation history
        output_tokens = random sample
        """
        input_tokens = num_context_tokens + agent_system_tokens
        output_tokens = random.randint(*output_tokens_range)
        cost_input = self._price_for_input_tokens(input_tokens)
        cost_output = self._price_for_output_tokens(output_tokens)

        return {
            "agent_index": agent_index,
            "agent_input_tokens": input_tokens,
            "agent_output_tokens": output_tokens,
            "agent_input_cost": cost_input,
            "agent_output_cost": cost_output,
            "agent_total_cost": cost_input + cost_output,
        }

    def evaluation_cost(
        self,
        num_evaluation_agents: int,
        agent_system_tokens: int,
        output_tokens_range: Tuple[int, int],
        accumulate_eval_context: bool,
    ) -> Dict[str, float]:
        """
        Calculates the total cost for all evaluation agents in a single turn.
        If accumulate_eval_context is True, each agent also sees the entire evaluation
        history so far in its input context.
        """
        all_agents = []
        total_input_tokens = 0
        total_output_tokens = 0
        total_cost = 0.0

        # Calculate context tokens for each evaluator
        # In accumulative mode, each evaluator sees:
        # 1. All previous conversation (Q&A)
        # 2. All previous evaluation outputs
        context_tokens_for_eval = (
            self.accumulated_conversation_tokens
            + (
                self.accumulated_evaluation_output_tokens
                if accumulate_eval_context
                else 0
            )
        )

        # Each agent processes this full context
        for i in range(num_evaluation_agents):
            info = self._agent_evaluation_cost(
                agent_index=i,
                num_context_tokens=context_tokens_for_eval,
                agent_system_tokens=agent_system_tokens,
                output_tokens_range=output_tokens_range,
            )
            all_agents.append(info)
            total_input_tokens += info["agent_input_tokens"]
            total_output_tokens += info["agent_output_tokens"]
            total_cost += info["agent_total_cost"]

        # Store this turn's evaluation output tokens for next turn's context
        if accumulate_eval_context:
            self.accumulated_evaluation_output_tokens += (
                total_output_tokens
            )

        return {
            "total_eval_input_tokens": total_input_tokens,
            "total_eval_output_tokens": total_output_tokens,
            "total_eval_cost": total_cost,
            "agent_breakdown": all_agents,
        }

    # ----------------- #
    # Question-Pool Agent
    # ----------------- #
    def question_pool_cost(
        self,
        this_turn_eval_output_tokens: int,
        question_pool_system_tokens: int,
        question_pool_output_tokens: int,
        accumulate_question_context: bool,
    ) -> Dict[str, float]:
        """
        Calculates cost for the question-pool agent (deciding next question).
        If accumulate_question_context is True, it also sees all previous question outputs.
        Otherwise, it only sees the new evaluation outputs from this turn + system prompt.
        """
        # If accumulate_question_context is True, include all previously generated Q tokens
        if accumulate_question_context:
            input_tokens = (
                this_turn_eval_output_tokens
                + question_pool_system_tokens
                + self.accumulated_question_output_tokens
            )
        else:
            input_tokens = (
                this_turn_eval_output_tokens
                + question_pool_system_tokens
            )

        output_tokens = question_pool_output_tokens
        cost_input = self._price_for_input_tokens(input_tokens)
        cost_output = self._price_for_output_tokens(output_tokens)
        total_cost = cost_input + cost_output

        return {
            "qp_input_tokens": input_tokens,
            "qp_output_tokens": output_tokens,
            "qp_input_cost": cost_input,
            "qp_output_cost": cost_output,
            "qp_total_cost": total_cost,
        }

    # ----------------- #
    # Question Generation
    # ----------------- #
    def _calculate_token_costs(
        self,
        input_tokens: int,
        output_tokens: int,
    ) -> TokenCosts:
        """Calculate costs for a given number of input and output tokens."""
        cost_input = self._price_for_input_tokens(input_tokens)
        cost_output = self._price_for_output_tokens(output_tokens)

        return TokenCosts(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=cost_input,
            output_cost=cost_output,
            total_cost=cost_input + cost_output,
        )

    def _calculate_ai_cost(
        self,
        is_ai_generated: bool,
        output_tokens_range: Tuple[int, int],
        base_input_tokens: int,
        additional_context_tokens: int = 0,
        prefix: str = "",
    ) -> Dict[str, float]:
        """Generic method for calculating AI-generated content costs."""
        if not is_ai_generated:
            return {
                f"{prefix}{k}": 0 for k in TokenCosts.__annotations__
            }

        input_tokens = base_input_tokens + additional_context_tokens
        output_tokens = random.randint(*output_tokens_range)
        costs = self._calculate_token_costs(input_tokens, output_tokens)

        return {f"{prefix}{k}": v for k, v in costs.as_dict.items()}

    def question_cost(
        self,
        is_ai_generated: bool,
        question_tokens_range: Tuple[int, int],
        accumulate_question_context: bool,
        system_tokens: int = 0,
    ) -> Dict[str, float]:
        """Calculate cost for generating a question."""
        additional_context = (
            self.accumulated_question_output_tokens
            if accumulate_question_context
            else 0
        )

        return self._calculate_ai_cost(
            is_ai_generated=is_ai_generated,
            output_tokens_range=question_tokens_range,
            base_input_tokens=self.accumulated_conversation_tokens
            + system_tokens,
            additional_context_tokens=additional_context,
            prefix="question_",
        )

    def answer_cost(
        self,
        is_ai_generated: bool,
        answer_tokens_range: Tuple[int, int],
        system_tokens: int = 0,
    ) -> Dict[str, float]:
        """Calculate cost for generating an answer."""
        return self._calculate_ai_cost(
            is_ai_generated=is_ai_generated,
            output_tokens_range=answer_tokens_range,
            base_input_tokens=self.accumulated_conversation_tokens
            + system_tokens,
            prefix="answer_",
        )

    # ----------------- #
    # Turn Orchestration
    # ----------------- #
    def turn_cost(
        self,
        turn_index: int,
        is_ai_question: bool,
        is_ai_answer: bool,
        num_evaluation_agents: int,
        agent_system_tokens: int,
        agent_output_tokens_range: Tuple[int, int],
        question_pool_system_tokens: int,
        question_pool_output_tokens: int,
        question_tokens_range: Tuple[int, int],
        answer_tokens_range: Tuple[int, int],
        accumulate_eval_context: bool,
        accumulate_question_context: bool,
    ) -> Dict[str, float]:
        # 1) Generate question (if AI)
        q_cost_info = self.question_cost(
            is_ai_generated=is_ai_question,
            question_tokens_range=question_tokens_range,
            accumulate_question_context=accumulate_question_context,
            system_tokens=0,
        )
        # Update conversation context with newly generated question tokens
        self.accumulated_conversation_tokens += q_cost_info[
            "question_output_tokens"
        ]

        # ALSO if accumulative for question, we keep track of question output
        if is_ai_question and accumulate_question_context:
            self.accumulated_question_output_tokens += q_cost_info[
                "question_output_tokens"
            ]

        # 2) Generate answer (if AI)
        a_cost_info = self.answer_cost(
            is_ai_generated=is_ai_answer,
            answer_tokens_range=answer_tokens_range,
            system_tokens=0,
        )
        self.accumulated_conversation_tokens += a_cost_info[
            "answer_output_tokens"
        ]
        # Answers do not have a separate "accumulated answer context" in this design

        # 3) Evaluation
        eval_info = self.evaluation_cost(
            num_evaluation_agents=num_evaluation_agents,
            agent_system_tokens=agent_system_tokens,
            output_tokens_range=agent_output_tokens_range,
            accumulate_eval_context=accumulate_eval_context,
        )

        # If accumulative, we keep track of newly generated evaluation tokens
        if accumulate_eval_context:
            self.accumulated_evaluation_output_tokens += eval_info[
                "total_eval_output_tokens"
            ]

        # 4) Question-Pool agent
        qp_info = self.question_pool_cost(
            this_turn_eval_output_tokens=eval_info[
                "total_eval_output_tokens"
            ],
            question_pool_system_tokens=question_pool_system_tokens,
            question_pool_output_tokens=question_pool_output_tokens,
            accumulate_question_context=accumulate_question_context,
        )

        # If we consider question-pool output to be an actual question text,
        # you may also update self.accumulated_question_output_tokens for next turn.
        # This depends on your design. We'll do it here for demonstration:
        if accumulate_question_context:
            self.accumulated_question_output_tokens += qp_info[
                "qp_output_tokens"
            ]

        turn_total_cost = (
            q_cost_info["question_total_cost"]
            + a_cost_info["answer_total_cost"]
            + eval_info["total_eval_cost"]
            + qp_info["qp_total_cost"]
        )

        turn_breakdown = {
            "turn_index": turn_index,
            "question_cost": q_cost_info["question_total_cost"],
            "answer_cost": a_cost_info["answer_total_cost"],
            "evaluation_cost": eval_info["total_eval_cost"],
            "question_pool_cost": qp_info["qp_total_cost"],
            "turn_total_cost": turn_total_cost,
        }

        self.running_total_cost += turn_total_cost
        self.turn_details.append(turn_breakdown)
        return turn_breakdown

    def interview_cost(
        self,
        num_of_turns: int = 10,
        is_ai_question: bool = True,
        is_ai_answer: bool = False,
        num_evaluation_agents: int = 3,
        agent_system_tokens: int = 300,
        agent_output_tokens_range: Tuple[int, int] = (250, 600),
        question_pool_system_tokens: int = 300,
        question_pool_output_tokens: int = 100,
        question_tokens_range: Tuple[int, int] = (100, 150),
        answer_tokens_range: Tuple[int, int] = (100, 200),
        accumulate_eval_context: bool = False,
        accumulate_question_context: bool = False,
    ) -> float:
        # Reset relevant variables
        self.running_total_cost = 0.0
        self.turn_details.clear()
        self.accumulated_conversation_tokens = 0
        self.accumulated_evaluation_output_tokens = 0
        self.accumulated_question_output_tokens = 0

        for turn_idx in range(1, num_of_turns + 1):
            self.turn_cost(
                turn_index=turn_idx,
                is_ai_question=is_ai_question,
                is_ai_answer=is_ai_answer,
                num_evaluation_agents=num_evaluation_agents,
                agent_system_tokens=agent_system_tokens,
                agent_output_tokens_range=agent_output_tokens_range,
                question_pool_system_tokens=question_pool_system_tokens,
                question_pool_output_tokens=question_pool_output_tokens,
                question_tokens_range=question_tokens_range,
                answer_tokens_range=answer_tokens_range,
                accumulate_eval_context=accumulate_eval_context,
                accumulate_question_context=accumulate_question_context,
            )

        return self.running_total_cost

    def calculate_cost(self) -> float:
        return self.running_total_cost

    def total_cost(self) -> float:
        return self.init_cost + self.running_total_cost + self.post_cost

    def get_turn_details(self) -> List[Dict]:
        return self.turn_details


# ----------------- #
# Streamlit App
# ----------------- #


def create_range_slider(
    name: str,
    min_val: int,
    max_val: int,
    default_min: int,
    default_max: int,
) -> Tuple[int, int]:
    """Create and validate a pair of min/max sliders."""
    min_tokens = st.sidebar.slider(
        f"{name} (Min Tokens)", min_val, max_val, default_min
    )
    max_tokens = st.sidebar.slider(
        f"{name} (Max Tokens)", min_val, max_val, default_max
    )

    if min_tokens > max_tokens:
        st.sidebar.warning(
            f"{name} min should be <= max, swapping values."
        )
        return max_tokens, min_tokens
    return min_tokens, max_tokens


def main() -> None:
    st.title("AI Interview Cost Calculator \U0001f916")
    st.write(
        "Use the controls in the sidebar to configure parameters and see how the cost evolves "
        "over multiple interview turns.\n\n"
        "**New Features**:\n"
        "- **Accumulate Evaluation Context**: If enabled, each evaluation sees all previous "
        "evaluation outputs.\n"
        "- **Accumulate Question Context**: If enabled, each question or question-pool agent sees "
        "all previously generated questions."
    )
    st.markdown("---")

    # Sidebar configuration
    st.sidebar.header("Interview Configuration")

    num_of_turns = st.sidebar.slider(
        "Number of Turns", min_value=1, max_value=50, value=10
    )
    is_ai_question = st.sidebar.checkbox(
        "AI Generates Questions?", value=True
    )
    is_ai_answer = st.sidebar.checkbox(
        "AI Generates Answers?", value=False
    )
    accumulate_eval_context = st.sidebar.checkbox(
        "Accumulate Evaluation Context?", value=False
    )
    accumulate_question_context = st.sidebar.checkbox(
        "Accumulate Question Context?", value=False
    )

    num_evaluation_agents = st.sidebar.slider(
        "Number of Evaluation Agents", 0, 100, 3
    )

    agent_system_tokens = st.sidebar.slider(
        "Agent System Prompt Tokens", 0, 2000, 300
    )
    agent_output_min, agent_output_max = create_range_slider(
        "Agent Output",
        min_val=0,
        max_val=2000,
        default_min=250,
        default_max=600,
    )

    qp_system_tokens = st.sidebar.slider(
        "Question-Pool System Tokens", 0, 2000, 300
    )
    qp_output_tokens = st.sidebar.slider(
        "Question-Pool Output Tokens", 0, 1000, 100
    )

    question_min, question_max = create_range_slider(
        "Question",
        min_val=0,
        max_val=1000,
        default_min=100,
        default_max=150,
    )

    answer_min, answer_max = create_range_slider(
        "Answer",
        min_val=0,
        max_val=1000,
        default_min=100,
        default_max=200,
    )

    st.sidebar.header("Initialization & Post-processing")
    init_system_tokens = st.sidebar.slider(
        "Initialization System Tokens", 0, 2000, 800
    )
    init_question_tokens = st.sidebar.slider(
        "Initialization Question Tokens", 0, 2000, 500
    )
    is_init_ai = st.sidebar.checkbox(
        "AI-based Initialization?", value=True
    )

    post_tokens = st.sidebar.slider(
        "Post-processing Tokens", 0, 2000, 500
    )

    st.markdown("### Simulation Results")

    # Create our calculator
    calculator = CostCalculator(GPT4o)

    # 1) Initialization
    init_cost = calculator.initialization_cost(
        initial_question_tokens=init_question_tokens,
        system_tokens=init_system_tokens,
        is_ai_generated=is_init_ai,
    )

    # 2) Interview cost
    interview_cost = calculator.interview_cost(
        num_of_turns=num_of_turns,
        is_ai_question=is_ai_question,
        is_ai_answer=is_ai_answer,
        num_evaluation_agents=num_evaluation_agents,
        agent_system_tokens=agent_system_tokens,
        agent_output_tokens_range=(agent_output_min, agent_output_max),
        question_pool_system_tokens=qp_system_tokens,
        question_pool_output_tokens=qp_output_tokens,
        question_tokens_range=(question_min, question_max),
        answer_tokens_range=(answer_min, answer_max),
        accumulate_eval_context=accumulate_eval_context,
        accumulate_question_context=accumulate_question_context,
    )

    # 3) Post-processing
    post_cost = calculator.post_processing_cost(
        input_tokens=post_tokens
    )

    total_cost = calculator.total_cost()

    # Display cost metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Initialization Cost", f"${init_cost:.4f}")
    col2.metric("Interview Cost", f"${interview_cost:.4f}")
    col3.metric("Post-processing Cost", f"${post_cost:.4f}")
    col4.metric("Total Cost", f"${total_cost:.4f}")

    st.markdown("---")
    st.subheader("Cost Breakdown per Turn")

    turn_details = calculator.get_turn_details()
    if not turn_details:
        st.info("No turns were processed or zero turns specified.")
        return

    # Convert turn details to DataFrame
    df = pd.DataFrame(turn_details)
    # Add a cumulative cost column (turn-by-turn)
    df["cumulative_cost"] = df["turn_total_cost"].cumsum()

    st.dataframe(df)

    # Create separate charts for different cost views
    st.subheader("Cost Visualization")
    view_type = st.radio(
        "Select View",
        ["All Costs", "Per-Turn Costs", "Cumulative Cost Only"],
        horizontal=True,
    )

    # Filter data based on view selection
    if view_type == "All Costs":
        cost_cols = [
            "question_cost",
            "answer_cost",
            "evaluation_cost",
            "question_pool_cost",
            "turn_total_cost",
            "cumulative_cost",
        ]
    elif view_type == "Per-Turn Costs":
        cost_cols = [
            "question_cost",
            "answer_cost",
            "evaluation_cost",
            "question_pool_cost",
        ]
    else:  # Cumulative Cost Only
        cost_cols = ["cumulative_cost"]

    df_melt = df.melt(
        id_vars="turn_index",
        value_vars=cost_cols,
        var_name="Cost Type",
        value_name="Cost",
    )

    # Add log scale option
    use_log_scale = st.checkbox("Use Logarithmic Scale", value=False)

    # Build an interactive line chart
    y_scale = (
        alt.Scale(type="log")
        if use_log_scale
        else alt.Scale(type="linear")
    )

    line_chart = (
        alt.Chart(df_melt)
        .mark_line(point=True)
        .encode(
            x=alt.X("turn_index:Q", title="Turn Index"),
            y=alt.Y(
                "Cost:Q",
                title="Cost (USD)",
                scale=y_scale,
            ),
            color=alt.Color(
                "Cost Type:N",
                legend=alt.Legend(
                    orient="top", title=None, labelFontSize=12
                ),
            ),
            tooltip=[
                alt.Tooltip("turn_index:Q", title="Turn"),
                alt.Tooltip("Cost Type:N"),
                alt.Tooltip("Cost:Q", format="$.4f"),
                alt.Tooltip("Cost:Q", format=".2%", title="% of Total"),
            ],
        )
        .properties(width="container", height=500)
        .configure_axis(labelFontSize=12, titleFontSize=14)
        .configure_legend(labelFontSize=12)
        .interactive()
    )

    st.altair_chart(line_chart, use_container_width=True)

    # Add cost breakdown analysis
    if st.checkbox("Show Cost Analysis"):
        total_cost = df_melt["Cost"].sum()
        cost_by_type = df_melt.groupby("Cost Type")["Cost"].sum()
        percentages = (cost_by_type / total_cost * 100).round(2)

        st.write("### Cost Breakdown by Type")
        breakdown_df = pd.DataFrame(
            {
                "Total Cost": cost_by_type.round(4),
                "Percentage": percentages.map(lambda x: f"{x:.2f}%"),
            }
        )
        st.dataframe(breakdown_df)

        if accumulate_eval_context:
            st.info(
                "📊 **Evaluation Cost Growth**: In accumulative mode, evaluation costs grow "
                "quadratically because each evaluator must process all previous evaluation "
                "outputs. This explains why evaluation costs dominate the total cost."
            )

    # Display raw data option
    if st.checkbox("Show Raw Data"):
        st.dataframe(
            df_melt.sort_values(["turn_index", "Cost Type"]).round(4)
        )


if __name__ == "__main__":
    main()
