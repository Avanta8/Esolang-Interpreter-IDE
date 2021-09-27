from typing import Callable, Optional


class BaseInterpreter:
    def __init__(
        self,
        code: str,
        input_func: Callable = input,
        output_func: Callable = print,
        undo_input_func: Optional[Callable] = None,
    ):
        pass

    def run(self) -> str:
        """Run the program and return the output"""
        pass

    def step(self) -> tuple[int, int]:
        pass


class VisualiserInterpreter(BaseInterpreter):
    def back(self) -> tuple[int, int]:
        pass
