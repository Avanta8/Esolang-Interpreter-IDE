from interpreters.errors import (
    ErrorTypes,
    ExecutionEndedError,
    InterpreterError,
    NoInputError,
    NoPreviousExecutionError,
    ProgramError,
    ProgramRuntimeError,
    ProgramSyntaxError,
)

from interpreters.brainfuck import BrainfuckInterpreter, FastBrainfuckInterpreter