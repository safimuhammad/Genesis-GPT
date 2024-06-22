from typing_extensions import TypedDict
from pydantic import Field


class Thoughts(TypedDict):
    planning: list[str] = Field(
        ..., description="Step by step reasoning of the problem"
    )
    criticism: str = Field(..., description="criticize your planning")


class AbilityDetail(TypedDict):
    plan_for_tool: str = Field(..., description="Plan for the specific tool")
    tool_to_use: str


class AbilityGraph(TypedDict):
    ability: str = Field(..., description="tool_to_use")  # Node
    next_ability: list[str] = Field(
        ...,
        description="the next tool to use, that is connected to this task, form a clear task graph",
    )  # Edges


class Ability(TypedDict):
    ability_name: list[AbilityDetail]


def call_ability(
    thoughts: list[Thoughts], ability: list[Ability], graph: list[AbilityGraph]
):
    pass
