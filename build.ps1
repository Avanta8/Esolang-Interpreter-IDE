.\venv\Scripts\activate
pyinstaller esolang_IDE/__main__.py -F `
--name "Esolang-IDE" `
--hidden-import PyQt5.QtPrintSupport `
--onefile `
--clean `
-w