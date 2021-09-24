from PyQt5 import Qsci, QtGui


class _LanguageLexer(Qsci.QsciLexerCustom):

    # _default_font = QtGui.QFont('Source Code Pro', 10)
    # _default_font = QtGui.QFont('Fira Code', 10)
    _default_font = QtGui.QFont('Consolas', 10)
    _default_colour = QtGui.QColor('black')

    _styles = []

    _language = ''

    def __init__(self, parent=None):
        super().__init__(parent)

        self._set_defaults()
        self._define_styles()

    def _set_defaults(self):
        self.setDefaultFont(self._default_font)
        self.setDefaultColor(self._default_colour)

    def _define_styles(self):
        self.style_to_description = {}
        self.description_to_style = {}
        for i, (description, style) in enumerate(self._styles):
            self.style_to_description[i] = description
            self.description_to_style[description] = i
            for method, arg in style.items():
                getattr(self, method)(arg, i)

    def language(self):
        return self._language

    def description(self, style_num):
        return self.style_to_description.get(style_num, '')

    def styleText(self, start, end):
        raise NotImplementedError


class NoneLexer(_LanguageLexer):

    _styles = [
        (
            'none',
            {},
        ),
    ]

    def styleText(self, start, end):
        pass


class BrainfuckLexer(_LanguageLexer):

    _styles = [
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
            'io',
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

    _language = 'Brainfuck'

    def styleText(self, start, end):
        self.startStyling(start)

        text = self.editor().text()[start:end]

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
