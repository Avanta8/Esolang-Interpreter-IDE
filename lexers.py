from PyQt5 import Qsci, QtCore, QtGui


class BrainfuckLexer(Qsci.QsciLexerCustom):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._define_styles()

    def _define_styles(self):
        self.setDefaultFont(QtGui.QFont('Source Code Pro', 10))
        self.setDefaultColor(QtGui.QColor('black'))

        styles = [
            (
                'loop',
                {
                    'setColor': QtGui.QColor('red'),
                },
            ),
            (
                'pointer',
                {
                    'setColor': QtGui.QColor('purple'),
                },
            ),
            (
                'cell',
                {
                    'setColor': QtGui.QColor('green'),
                },
            ),
            (
                'input/output',
                {
                    'setColor': QtGui.QColor('blue'),
                },
            ),
            (
                'comment',
                {
                    'setColor': QtGui.QColor('grey'),
                },
            ),
        ]

        self.styles_descriptions = {}
        for i, (description, style) in enumerate(styles):
            self.styles_descriptions[i] = description
            for method, arg in style.items():
                getattr(self, method)(arg, i)

    def language(self):
        return 'Brainfuck'

    def description(self, style_num):
        return self.styles_descriptions.get(style_num, '')

    def styleText(self, start, end):
        self.startStyling(start)

        text = self.parent().text()[start:end]

        for char in text:
            if char in '[]':
                style = 0
            elif char in ',.':
                style = 3
            elif char in '<>':
                style = 2
            elif char in '-+':
                style = 1
            else:
                style = 4

            self.setStyling(1, style)
