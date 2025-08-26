from pydantic import BaseModel
import threading
import time


class MyModel(BaseModel):
    value: int = 0

    class Config:
        validate_assignment = True  # メンバ変数を直接変更可能にする

    def add_inplace(self, x: int) -> None:
        self.value += x

    def reset_inplace(self) -> None:
        self.value = 0


# 共有インスタンス
model = MyModel(value=10)
lock = threading.Lock()


def thread_func_add():
    for _ in range(2):
        with lock:
            model.add_inplace(1)
            print(f"[Add] value = {model.value}")
        time.sleep(0.1)


def thread_func_reset():
    with lock:
        model.reset_inplace()
        print(f"[Reset] value = {model.value}")


# スレッド起動
thread_c = threading.Thread(target=thread_func_add)
thread_d = threading.Thread(target=thread_func_reset)

thread_c.start()
thread_d.start()
thread_c.join()
thread_d.join()

print("Final value:", model.value)
