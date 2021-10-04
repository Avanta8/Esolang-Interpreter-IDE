import enum

import esolang_IDE.visualisers as visualisers
import esolang_IDE.interpreters as interpreters
import esolang_IDE.input_decoders as input_decoders
import esolang_IDE.lexers as lexers


class FileTypes(enum.Enum):
    NONE = enum.auto()
    TEXT = enum.auto()
    BRAINFUCK = enum.auto()
    PYTHON = enum.auto()

    def to_visualiser(self) -> type[visualisers.BaseVisualiserWidget]:
        return {
            FileTypes.NONE: visualisers.NoVisualiserWidget,
            FileTypes.BRAINFUCK: visualisers.BrainfuckVisualiserWidget,
        }.get(self, visualisers.NoVisualiserWidget)

    def to_interpreter(self) -> type[interpreters.BaseInterpreter]:
        return {
            FileTypes.NONE: interpreters.BaseInterpreter,
            FileTypes.BRAINFUCK: interpreters.BrainfuckInterpreter,
        }.get(self, interpreters.BaseInterpreter)

    def to_runner_interpreter(self) -> type[interpreters.BaseInterpreter]:
        return {
            FileTypes.NONE: interpreters.BaseInterpreter,
            FileTypes.BRAINFUCK: interpreters.FastBrainfuckInterpreter,
        }.get(self, interpreters.BaseInterpreter)

    def to_input_decoder(self) -> type[input_decoders.BaseDecoder]:
        return {
            FileTypes.NONE: input_decoders.BaseDecoder,
            FileTypes.BRAINFUCK: input_decoders.BrainfuckDecoder,
        }.get(self, input_decoders.BaseDecoder)

    def to_lexer(self) -> type[lexers.LanguageLexer]:
        return {
            FileTypes.NONE: lexers.NoneLexer,
            FileTypes.BRAINFUCK: lexers.BrainfuckLexer,
        }.get(self, lexers.NoneLexer)

    @classmethod
    def from_extension(cls, extension):
        return {
            '.txt': cls.TEXT,
            '.b': cls.BRAINFUCK,
            '.py': cls.PYTHON,
        }.get(extension, cls.NONE)
