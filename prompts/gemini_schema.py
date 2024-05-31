from typing_extensions import TypedDict

class Thoughts(TypedDict):
    planning: list[str]
    criticism: list[str]

class Ability(TypedDict):
    ability_name: list[str]

def call_ability(
    thoughts: list[Thoughts],
    ability: list[Ability]
):
    pass