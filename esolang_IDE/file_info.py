import os
from dataclasses import dataclass

from constants import FileTypes


@dataclass
class FileInfo:
    filepath: str
    filename: str
    filetype: FileTypes

    def read(self):
        with open(self.filepath, 'r') as file:
            read = file.read()
        return read

    def write(self, text):
        with open(self.filepath, 'w') as file:
            file.write(text)

    def is_empty(self):
        empty = not self.filepath

        if empty:
            assert (
                self.filepath == self.filename == '' and self.filetype is FileTypes.NONE
            ), (
                'FileInfo is empty but some attributes are not empty'
                f' {self.filepath=}, {self.filename=}, {self.filetype=}'
            )
        else:
            assert (
                self.filetype != ''
                and self.filename != ''
            ), (
                'FileInfo is not empty but one or more arribuetes are empty'
                f' {self.filepath=}, {self.filename=}, {self.filetype=}'
            )
        
        return empty

    @classmethod
    def from_filepath(cls, filepath):
        if not filepath:
            return cls.from_empty()

        extension = os.path.splitext(filepath)[1]
        filetype = FileTypes.from_extension(extension)
        filename = os.path.basename(filepath)
        return cls(filepath, filename, filetype)

    @classmethod
    def from_empty(cls):
        return cls('', '', FileTypes.NONE)
