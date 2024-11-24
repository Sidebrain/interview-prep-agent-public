from app.event_agents.evaluations.evaluator_base import (
    EvaluatorBase,
)


class Evaluator(EvaluatorBase):
    pass


relevance_evaluator = Evaluator(
    evaluation_instruction="check the relevance of the answer to the question"
)

exaggeration_evaluator = Evaluator(
    evaluation_instruction="check the exaggeration of the answer"
)

embellishment_evaluator = Evaluator(
    evaluation_instruction="check the embellishment of the answer"
)

structured_thinking_evaluator = Evaluator(
    evaluation_instruction="check the structured thinking of the answer"
)
