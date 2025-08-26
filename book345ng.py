from pydantic import BaseModel, ConfigDict
import threading
import time
from typing import Final


class AttackPower(BaseModel):
    # PydanticDeprecatedSince211: Annotation 'value' is marked as final and has a default value. Pydantic treats 'value' as a class variable, but it will be considered as a normal field in V3 to be aligned with dataclasses. If you still want 'value' to be considered as a class variable, annotate it as: `ClassVar[<type>] = <default>.`. Deprecated in Pydantic V2.11 to be removed in V3.0.
    # value: Final[int] = 0
    model_config = ConfigDict(frozen=True)
    value: int = 0

    def add(self, x: "AttackPower") -> "AttackPower":
        return AttackPower(value=self.value + x.value)

    def reset(self) -> "AttackPower":
        return AttackPower(value=0)


class weapon(BaseModel):
    attackPower: AttackPower

    def enhance(self, increment: AttackPower) -> "weapon":
        new_power = self.attackPower.add(increment)
        return weapon(attackPower=new_power)

    def reset(self) -> "weapon":
        new_power = self.attackPower.reset()
        return weapon(attackPower=new_power)


# これはエラーになる
# AttackPowerA.value = 20

# 共有リソース（新しいインスタンスで更新）
AttackPowerA = AttackPower(value=10)
AttackPowerB = AttackPower(value=10)


weaponA = weapon(attackPower=AttackPowerA)
weaponB = weapon(attackPower=AttackPowerB)

lock = threading.Lock()


def thread_func_add():
    global weaponA
    for _ in range(5):
        with lock:
            AttackPower1 = AttackPower(value=1)
            weaponA = weaponA.enhance(AttackPower1)
            print(f"[weaponA] value = {weaponA.attackPower.value}")
        time.sleep(0.1)


def thread_func_reset():
    global weaponB
    for _ in range(3):
        with lock:
            weaponB = weaponB.reset()
            print(f"[weaponB] value = {weaponB.attackPower.value}")
        time.sleep(0.3)


# スレッド起動
thread_add = threading.Thread(target=thread_func_add)
thread_reset = threading.Thread(target=thread_func_reset)

thread_add.start()
thread_reset.start()
thread_add.join()
thread_reset.join()
