import enum

import esolang_IDE.visualisers as visualisers
import esolang_IDE.interpreters as interpreters
import esolang_IDE.input_decoders as input_decoders


class FileTypes(enum.Enum):
    NONE = enum.auto()
    TEXT = enum.auto()
    BRAINFUCK = enum.auto()
    PYTHON = enum.auto()

    def to_visualiser(self) -> visualisers.BaseVisualiserWidget:
        return {
            FileTypes.NONE: visualisers.NoVisualiserWidget,
            FileTypes.BRAINFUCK: visualisers.BrainfuckVisualiserWidget,
        }.get(self, visualisers.NoVisualiserWidget)

    def to_interpreter(self) -> interpreters.BaseInterpreter:
        return {
            FileTypes.NONE: interpreters.BaseInterpreter,
            FileTypes.BRAINFUCK: interpreters.BrainfuckInterpreter,
        }.get(self, interpreters.BaseInterpreter)

    def to_runner_interpreter(self) -> interpreters.BaseInterpreter:
        return {
            FileTypes.NONE: interpreters.BaseInterpreter,
            FileTypes.BRAINFUCK: interpreters.FastBrainfuckInterpreter,
        }.get(self, interpreters.BaseInterpreter)

    def to_input_decoder(self) -> input_decoders.BaseDecoder:
        return {
            FileTypes.NONE: input_decoders.BaseDecoder,
            FileTypes.BRAINFUCK: input_decoders.BrainfuckDecoder,
        }.get(self, input_decoders.BaseDecoder)

    @classmethod
    def from_extension(cls, extension):
        return {
            '.txt': cls.TEXT,
            '.b': cls.BRAINFUCK,
            '.py': cls.PYTHON,
        }.get(extension, cls.NONE)
