"""
Syntax highlighters for the UI.

This module contains classes for syntax highlighting in text editors.
"""

from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
import re
from typing import Dict


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document, colors):
        super().__init__(document)
        self.colors = colors
        self.highlighting_rules = []
        self._setup_formats()

    def _setup_formats(self):
        # Keywords
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor(self.colors['keyword']))
        self.keyword_format.setFontWeight(QFont.Bold)
        keywords = ['and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'exec', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'not', 'or', 'pass', 'print', 'raise', 'return', 'try', 'while', 'with', 'yield']
        for word in keywords:
            pattern = r'\b' + word + r'\b'
            self.highlighting_rules.append((re.compile(pattern), self.keyword_format))

        # Strings
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor(self.colors['string']))
        self.highlighting_rules.append((re.compile(r'\".*?(?<!\\)\"'), self.string_format))
        self.highlighting_rules.append((re.compile(r"'.*?(?<!\\)'"), self.string_format))

        # Comments
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor(self.colors['comment']))
        self.comment_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'#.*'), self.comment_format))

        # Numbers
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor(self.colors['number']))
        self.highlighting_rules.append((re.compile(r'\b[0-9]+\b'), self.number_format))

        # Functions
        self.function_format = QTextCharFormat()
        self.function_format.setForeground(QColor(self.colors['function']))
        self.function_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'\b[A-Za-z0-9_]+(?=\s*\()'), self.function_format))

    def update_colors(self, colors):
        self.colors = colors
        self.highlighting_rules = []
        self._setup_formats()
        self.rehighlight()

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)


class JSONHighlighter(QSyntaxHighlighter):
    def __init__(self, document, colors):
        super().__init__(document)
        self.colors = colors
        self.highlighting_rules = []
        self._setup_formats()

    def _setup_formats(self):
        # Strings
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor(self.colors['string']))
        self.highlighting_rules.append((re.compile(r'\".*?(?<!\\)\"'), self.string_format))

        # Numbers
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor(self.colors['number']))
        self.highlighting_rules.append((re.compile(r'\b-?[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?\b'), self.number_format))

        # Keys
        self.key_format = QTextCharFormat()
        self.key_format.setForeground(QColor(self.colors['key']))
        self.key_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((re.compile(r'\"[^\"]*\"(?=\s*:)'), self.key_format))

        # True/False/Null
        self.boolean_format = QTextCharFormat()
        self.boolean_format.setForeground(QColor(self.colors['boolean']))
        self.boolean_format.setFontWeight(QFont.Bold)
        for word in ['true', 'false', 'null']:
            pattern = r'\b' + word + r'\b'
            self.highlighting_rules.append((re.compile(pattern), self.boolean_format))

    def update_colors(self, colors):
        self.colors = colors
        self.highlighting_rules = []
        self._setup_formats()
        self.rehighlight()

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)
