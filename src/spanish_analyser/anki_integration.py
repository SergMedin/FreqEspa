"""
Модуль для интеграции с Anki

Предоставляет функциональность для:
- Открытия коллекций Anki
- Поиска заметок по колодам
- Извлечения текста из карточек
- Анализа содержимого коллекции
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path


class AnkiIntegration:
    """Класс для работы с коллекциями Anki"""
    
    def __init__(self, collection_path: Optional[str] = None):
        """
        Инициализация интеграции с Anki
        
        Args:
            collection_path: Путь к файлу коллекции .anki2
        """
        self.collection_path = collection_path or self._get_default_collection_path()
        self.collection = None
        self._is_connected = False
    
    def _get_default_collection_path(self) -> str:
        """Получает путь к коллекции по умолчанию для macOS"""
        # Путь по умолчанию для macOS
        default_path = os.path.expanduser(
            "~/Library/Application Support/Anki2/User 1/collection.anki2"
        )
        return default_path
    
    def connect(self) -> bool:
        """
        Подключается к коллекции Anki
        
        Returns:
            True если подключение успешно, False в противном случае
        """
        try:
            # Импортируем здесь, чтобы избежать ошибок если Anki не установлен
            from anki.storage import Collection
            
            if not os.path.exists(self.collection_path):
                print(f"Коллекция не найдена по пути: {self.collection_path}")
                return False
            
            self.collection = Collection(self.collection_path)
            self._is_connected = True
            print(f"Успешно подключились к коллекции: {self.collection_path}")
            return True
            
        except ImportError:
            print("Ошибка: модуль anki не найден. Убедитесь, что Anki установлен.")
            return False
        except Exception as e:
            print(f"Ошибка при подключении к коллекции: {e}")
            return False
    
    def disconnect(self):
        """Отключается от коллекции"""
        if self.collection:
            self.collection.close()
            self.collection = None
            self._is_connected = False
            print("Отключились от коллекции")
    
    def is_connected(self) -> bool:
        """Проверяет, подключены ли к коллекции"""
        return self._is_connected
    
    def get_deck_names(self) -> List[str]:
        """
        Получает список названий всех колод
        
        Returns:
            Список названий колод
        """
        if not self._is_connected:
            print("Не подключены к коллекции")
            return []
        
        try:
            deck_names = [deck['name'] for deck in self.collection.decks.all()]
            return deck_names
        except Exception as e:
            print(f"Ошибка при получении списка колод: {e}")
            return []
    
    def find_notes_by_deck(self, deck_pattern: str) -> List[int]:
        """
        Находит заметки по паттерну названия колоды
        
        Args:
            deck_pattern: Паттерн для поиска колоды (например, "Spanish*")
            
        Returns:
            Список ID заметок
        """
        if not self._is_connected:
            print("Не подключены к коллекции")
            return []
        
        try:
            note_ids = self.collection.find_notes(f"deck:{deck_pattern}")
            return note_ids
        except Exception as e:
            print(f"Ошибка при поиске заметок: {e}")
            return []
    
    def get_note_fields(self, note_id: int) -> Dict[str, Any]:
        """
        Получает поля заметки по ID
        
        Args:
            note_id: ID заметки
            
        Returns:
            Словарь с полями заметки
        """
        if not self._is_connected:
            print("Не подключены к коллекции")
            return {}
        
        try:
            note = self.collection.get_note(note_id)
            return {
                'id': note_id,
                'fields': note.fields,
                'note_type': note.note_type(),
                'tags': note.tags
            }
        except Exception as e:
            print(f"Ошибка при получении заметки {note_id}: {e}")
            return {}
    
    def extract_text_from_notes(self, note_ids: List[int], field_names: List[str] = None) -> List[Dict[str, Any]]:
        """
        Извлекает текст из заметок по указанным полям
        
        Args:
            note_ids: Список ID заметок
            field_names: Список названий полей для извлечения
            
        Returns:
            Список словарей с данными заметок
        """
        if not self._is_connected:
            print("Не подключены к коллекции")
            return []
        
        if not field_names:
            field_names = ['FrontText', 'BackText']
        
        notes_data = []
        
        for note_id in note_ids:
            note_info = self.get_note_fields(note_id)
            if not note_info:
                continue
            
            # Определяем индексы нужных полей
            field_indexes = []
            for i, field_name in enumerate(note_info['fields']):
                if field_name in field_names:
                    field_indexes.append(i)
            
            # Извлекаем текст из нужных полей
            extracted_texts = []
            for idx in field_indexes:
                if idx < len(note_info['fields']):
                    extracted_texts.append(note_info['fields'][idx])
            
            notes_data.append({
                'note_id': note_id,
                'texts': extracted_texts,
                'note_type': note_info['note_type'],
                'tags': note_info['tags']
            })
        
        return notes_data
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Получает статистику коллекции
        
        Returns:
            Словарь со статистикой
        """
        if not self._is_connected:
            print("Не подключены к коллекции")
            return {}
        
        try:
            stats = {
                'total_notes': self.collection.note_count(),
                'total_cards': self.collection.card_count(),
                'total_decks': len(self.collection.decks.all()),
                'collection_path': self.collection_path
            }
            return stats
        except Exception as e:
            print(f"Ошибка при получении статистики: {e}")
            return {}
    
    def __enter__(self):
        """Контекстный менеджер для автоматического подключения/отключения"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Автоматическое отключение при выходе из контекста"""
        self.disconnect()
