from pydantic import BaseModel, ConfigDict
from enum import Enum


class StateType(Enum):
    alive = 1
    dead = 0


class HitPoint(BaseModel):
    model_config = ConfigDict(frozen=True)
    amount: int
    MIN: int = 0

    def damage(self, damage_amount: int) -> "HitPoint":
        next_amount = max(self.amount - damage_amount, self.MIN)
        return HitPoint(amount=next_amount)

    def is_zero(self) -> bool:
        return self.amount == 0


class States(BaseModel):
    state: int = StateType.alive.value

    def add(self, value: int) -> "States":
        return States(state=self.state + value)


class Member(BaseModel):
    model_config = ConfigDict(frozen=True)
    hitpoint: HitPoint
    states: States

    def damage(self, damage_amount: int) -> "Member":
        new_hitpoint = self.hitpoint.damage(damage_amount)
        new_states = self.states
        if (new_hitpoint).is_zero():
            new_states = self.states.add(StateType.dead.value)
        return Member(hitpoint=new_hitpoint, states=new_states)


member = Member(hitpoint=HitPoint(amount=100), states=States())

member = member.damage(200)

print("HitPoint:", member.hitpoint.amount)
print("States:", member.states.state)
