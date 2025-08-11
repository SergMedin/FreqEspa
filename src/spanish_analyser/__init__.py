"""
Spanish Analyser - модуль для анализа испанского языка с интеграцией Anki

Этот модуль предоставляет инструменты для:
- Анализа испанских текстов
- Работы с коллекциями Anki
- Обработки и перевода испанских слов
- Создания карточек для изучения
"""

__version__ = "0.1.0"
__author__ = "Sergey"

from .text_processor import SpanishTextProcessor
from .anki_integration import AnkiIntegration
from .word_analyzer import WordAnalyzer

__all__ = [
    "SpanishTextProcessor",
    "AnkiIntegration", 
    "WordAnalyzer"
]
