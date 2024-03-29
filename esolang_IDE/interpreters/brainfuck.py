import functools
from collections import deque

from .base_interpreter import BaseInterpreter, VisualiserInterpreter
from .errors import (
    ErrorTypes,
    ExecutionEndedError,
    NoInputError,
    NoPreviousExecutionError,
    ProgramRuntimeError,
    ProgramSyntaxError,
)


class BrainfuckInterpreter(VisualiserInterpreter):
    """Brainfuck interpreter."""

    def __init__(
        self,
        code,
        input_func=input,
        output_func=print,
        undo_input_func=None,
        maxlen=1_000_000,
    ):
        self.code = code
        self.input_func = input_func
        self.output_func = output_func
        self.undo_input_func = undo_input_func
        self.brackets = self.match_brackets(code)
        self.tape = [0]
        self.tape_pointer = 0
        self.code_pointer = -1
        self.output = ''
        self.instruction_count = 0
        self.past = deque(maxlen=maxlen)
        self.commands = {
            '[': self.open_loop,
            ']': self.close_loop,
            '>': self.increment_pointer,
            '<': self.decrement_pointer,
            '+': self.increment_cell,
            '-': self.decrement_cell,
            ',': self.accept_input,
            '.': self.add_output,
        }

    def step(self):
        if self.code_pointer + 1 >= len(self.code):
            raise ExecutionEndedError

        self.past.append(
            (
                self.code_pointer,
                self.tape_pointer,
                self.tape[self.tape_pointer],
                len(self.output),
            )
        )

        self.code_pointer += 1
        try:
            while self.current_instruction not in self.commands:
                self.code_pointer += 1
        except IndexError:
            self.code_pointer = self.past.pop()[0]
            raise ExecutionEndedError

        code_pointer = self.code_pointer
        self.instruction_count += 1

        # I feel like `self.instruction_count` should be incremented after the command is executed.
        # However, this breaks self.decrement_pointer` calling `self.back` as it would decreament
        # the instruction count without incementing it in the first place.

        self.commands[self.current_instruction]()

        return code_pointer, 1

    def back(self):
        try:
            prev_info = self.past.pop()
        except IndexError:
            raise NoPreviousExecutionError
        assert (
            self.instruction_count != 0
        ), f'prev_info not empty but instruction count = {self.instruction_count}'

        if self.current_instruction == ',' and self.undo_input_func is not None:
            self.undo_input_func()

        self.code_pointer, self.tape_pointer, tape_val, output_len = prev_info

        if output_len != len(self.output):
            self.output = self.output[:-1]
            self.output_func(self.output)
        self.tape[self.tape_pointer] = tape_val
        self.instruction_count -= 1
        return (self.code_pointer, 1) if self.code_pointer >= 0 else (0, 0)

    def run(self):
        while True:
            try:
                self.step()
            except ExecutionEndedError:
                break
        return self.output

    def open_loop(self):
        if self.current_cell == 0:
            self.code_pointer = self.brackets[self.code_pointer]

    def close_loop(self):
        if self.current_cell != 0:
            self.code_pointer = self.brackets[self.code_pointer]

    def increment_pointer(self):
        self.tape_pointer += 1
        if self.tape_pointer >= len(self.tape):
            self.tape.append(0)

    def decrement_pointer(self):
        self.tape_pointer -= 1
        if self.tape_pointer < 0:
            error_location = self.code_pointer
            self.back()  # Reset back to was it was before
            raise ProgramRuntimeError(ErrorTypes.INVALID_TAPE_CELL, (error_location, 1))

    def increment_cell(self):
        self.tape[self.tape_pointer] = (self.tape[self.tape_pointer] + 1) % 256

    def decrement_cell(self):
        self.tape[self.tape_pointer] = (self.tape[self.tape_pointer] - 1) % 256

    def accept_input(self):
        input_ = self.input_func()
        if input_:
            self.tape[self.tape_pointer] = ord(input_) % 256
        else:
            self.code_pointer = self.past.pop()[0]
            self.instruction_count -= 1
            raise NoInputError

    def add_output(self):
        self.output += chr(self.current_cell)
        if self.output_func:
            self.output_func(self.output)

    def get_visual(self):
        """Information for visualiser"""
        return self.tape, self.tape_pointer

    @property
    def current_cell(self):
        return self.tape[self.tape_pointer]

    @property
    def current_instruction(self):
        return self.code[self.code_pointer]

    @staticmethod
    def match_brackets(code):
        stack = deque()  # deque is faster than list
        brackets = {}
        for i, char in enumerate(code):
            if char == '[':
                stack.append(i)
            elif char == ']':
                try:
                    match = stack.pop()
                except IndexError:
                    raise ProgramSyntaxError(ErrorTypes.UNMATCHED_CLOSE_PAREN, (i, 1))
                brackets[match] = i
                brackets[i] = match
        if stack:
            raise ProgramSyntaxError(ErrorTypes.UNMATCHED_OPEN_PAREN, (stack[-1], 1))
        return brackets


class FastBrainfuckInterpreter(BaseInterpreter):
    def __init__(self, code, input_func=input, output_func=None):
        self.commands, self.brackets = self._compile(code)
        self.input_func = input_func
        self.output_func = output_func
        self.tape = [0] * 40000

        self.reset()

    def run(self):
        self.running = True
        while self.running:
            # self.commands[self.command_pointer]()
            # self.command_pointer += 1
            self.step()
        return ''.join(self.output)

    def step(self):
        if self.finished:
            raise ExecutionEndedError()
        self.commands[self.command_pointer]()
        self.command_pointer += 1

    def open_loop(self):
        if self.current_cell == 0:
            self.command_pointer = self.brackets[self.command_pointer]

    def close_loop(self):
        if self.current_cell != 0:
            self.command_pointer = self.brackets[self.command_pointer]

    def pointer_op(self, times):
        self.tape_pointer += times
        if not 0 <= self.tape_pointer < 40000:
            raise ProgramRuntimeError(
                ErrorTypes.INVALID_TAPE_CELL, location=self.tape_pointer
            )

    def cell_op(self, times):
        self.tape[self.tape_pointer] = (self.tape[self.tape_pointer] + times) % 256

    def accept_input(self):
        input_ = self.input_func()
        if not input_:
            raise NoInputError(f'input: {input_}')
        self.tape[self.tape_pointer] = ord(input_) % 256

    def add_output(self):
        self.output.append(chr(self.current_cell))
        if self.output_func:
            self.output_func(chr(self.current_cell))

    def stop(self):
        self.running = False
        self.finished = True

    def reset(self):
        self.running = False
        self.finished = False
        self.command_pointer = 0
        self.tape_pointer = 0
        self.output = []

    @property
    def current_cell(self):
        return self.tape[self.tape_pointer]

    def _compile(self, code):
        command_funcs = {
            '[': self.open_loop,
            ']': self.close_loop,
            '>': self.pointer_op,
            '<': self.pointer_op,
            '+': self.cell_op,
            '-': self.cell_op,
            ',': self.accept_input,
            '.': self.add_output,
        }

        pointer_ops = set('<>')
        cell_ops = set('+-')

        bracket_stack = []
        brackets = {}
        final_commands = []
        code_len = len(code)
        i = 0

        while i < code_len:
            char = code[i]
            arg = None

            if char == '[':
                bracket_stack.append(len(final_commands))
            elif char == ']':
                try:
                    match = bracket_stack.pop()
                except IndexError:
                    raise ProgramSyntaxError(ErrorTypes.UNMATCHED_CLOSE_PAREN, (i, 1))
                current = len(final_commands)
                brackets[match] = current
                brackets[current] = match

            if char in pointer_ops:
                arg = 0
                while i < code_len and code[i] in pointer_ops:
                    arg += 1 if code[i] == '>' else -1
                    i += 1
            elif char in cell_ops:
                arg = 0
                while i < code_len and code[i] in cell_ops:
                    arg += 1 if code[i] == '+' else -1
                    i += 1
            else:
                i += 1

            if char in command_funcs:
                command = command_funcs[char]
                if arg is None:
                    final_commands.append(command)
                else:
                    final_commands.append(functools.partial(command, arg))

        final_commands.append(self.stop)

        if bracket_stack:
            raise ProgramSyntaxError(ErrorTypes.UNMATCHED_OPEN_PAREN)
        return final_commands, brackets
