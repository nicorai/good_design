from pydantic import BaseModel, ConfigDict


class HitPoint(BaseModel):
    amount: int


class States(BaseModel):
    def add() -> None:
        pass


class Menber(BaseModel):
    model_config = ConfigDict(frozen=True)
    hitpoint: HitPoint
    states: States

    def damage(self, damage_amount: int) -> "Menber":
        return Menber(
            hitpoint=HitPoint(amount=self.hitpoint.amount - damage_amount),
            states=self.states,
        )


menber = Menber(hitpoint=HitPoint(amount=100), states=States())

menber = menber.damage(200)

print("HitPoint:", menber.hitpoint.amount)
