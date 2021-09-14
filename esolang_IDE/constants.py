import enum


class FileTypes(enum.Enum):
    NONE = enum.auto()
    TEXT = enum.auto()
    BRAINFUCK = enum.auto()
    PYTHON = enum.auto()

    @classmethod
    def from_extension(cls, extension):
        return {
            '.txt': cls.TEXT,
            '.b': cls.BRAINFUCK,
            '.py': cls.PYTHON,
        }.get(extension, cls.NONE)
