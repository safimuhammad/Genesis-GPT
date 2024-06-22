from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal
import instructor


class CallStack(BaseModel):
    ability_name: str = Field(..., description="Name of the ability")
    reasoning: str = Field(
        ..., description="Reasoning behind the use of this ability, Keep it a 1 liner."
    )
    args: Dict[str, Any] = Field(
        ...,
        description="args required for the ability to run, Using the previous executed tasks and task informations.",
    )
    execution_decision: Literal["start", "done", "await"] = Field(
        ...,
        description="""Determine the appropriate status for this ability based on the following criteria:
                    - START: The task should be executed now based on its planning and priority.
                    - DONE: The task has already been completed, as indicated by 'previous_agent_output: [ability_name : 'ability_output']'.
                    - AWAIT: The task cannot be executed until another ability is completed, according to the planning.
                    - If one ability is based on the output of another ability, then they cannot START together.
                    """,
    )


class AbilityExecution(BaseModel):
    call_stack: CallStack


class ExecutionOrder(BaseModel):
    order_of_execution: List[AbilityExecution]
