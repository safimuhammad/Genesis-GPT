from typing_extensions import TypedDict
from pydantic import Field
import typing


class Thoughts(TypedDict):
    planning: list[str] = Field(
        ..., description="Step by step reasoning of the problem"
    )
    criticism: str = Field(..., description="criticize your planning or None")


class Args(TypedDict):
    arg_name: str
    is_static: bool = Field(
        ..., description="If arg_value cannot be decided set to false."
    )
    arg_value: str = Field(
        ..., description="If arg_value is not availibe set this to None"
    )


class AbilityDetail(TypedDict):
    plan_for_tool: str = Field(..., description="Plan for the specific tool")
    tool_to_use: str
    args: list[Args]


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
