import itertools
from pathlib import Path

import pytest
from pytestqt import qtbot

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtTest import QTest

from esolang_IDE.controllers.runner_controller import RunnerController
from esolang_IDE.code_text import CodeText
from esolang_IDE.code_runner import CodeRunner

from esolang_IDE.file_info import FileInfo

from esolang_IDE.constants import FileTypes

SAMPLE_PROGRAMS_PATH = (Path(__file__).parent / 'sample_programs').resolve()


def read_file(filename):
    return FileInfo.from_filepath((SAMPLE_PROGRAMS_PATH / filename).resolve()).read()


@pytest.fixture(autouse=True)
def setup(request, qtbot):

    code_text = CodeText()
    code_text.set_lexer(FileTypes.BRAINFUCK.to_lexer())

    runner = CodeRunner()

    controller = RunnerController(code_text, runner)
    controller.set_filetype(FileTypes.BRAINFUCK)

    request.cls.code_text = code_text
    request.cls.code_runner = runner
    request.cls.runner_controller = controller

    # code_text.show()
    # runner.show()


class _BaseTest:

    code_text: CodeText
    code_runner: CodeRunner
    runner_controller: RunnerController

    filename: str

    @pytest.fixture(autouse=True)
    def setup_text(self):
        self.source_code = read_file(self.filename)
        self.code_text.setText(self.source_code)

    def test_text_correct(self):
        assert self.source_code == self.code_text.text()

    def get_raw_output_text(self):
        return self.code_runner.get_output_text().toPlainText()


class TestRunCode(_BaseTest):

    filename = 'hello world.b'

    def test_run_output_correct(self, qtbot: qtbot.QtBot):
        with qtbot.waitSignal(
            self.runner_controller._output_text.completed, timeout=1000
        ) as blocker:

            self.runner_controller.run_code()

        assert self.get_raw_output_text() == 'Hello World!' * 20


class TestInfiniteOutput(_BaseTest):

    filename = 'forever output.b'
    _output = ''.join(chr(i) for i in range(1, 256, 2)).replace(
        '\r', '\n'
    )  # TextEdit converts \r to \n

    def test_run(self, qtbot: qtbot.QtBot):
        self.runner_controller.run_code()

        qtbot.wait(500)

        self.runner_controller.interrupt()

        assert len(self.get_raw_output_text()) >= 1000

        for a, b in zip(self.get_raw_output_text(), self._output):
            print(repr(a), repr(b))
            assert a == b

        assert self.get_raw_output_text().startswith(self._output)

    def test_interrupt(self, qtbot: qtbot.QtBot):

        for ms in itertools.islice(itertools.cycle((100, 200, 300)), 10):
            self.runner_controller.run_code()
            qtbot.wait(ms)
            self.runner_controller.interrupt()

            output = self.get_raw_output_text()
            assert output == ''.join(
                itertools.islice(itertools.cycle(self._output), len(output))
            )

    def test_long_run(self, qtbot: qtbot.QtBot):
        self.runner_controller.run_code()
        qtbot.wait(5000)
        self.runner_controller.interrupt()
        output = self.get_raw_output_text()
        assert output == ''.join(
            itertools.islice(itertools.cycle(self._output), len(output))
        )


if __name__ == "__main__":
    pytest.main()
