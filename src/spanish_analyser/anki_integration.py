"""
Модуль для интеграции с Anki

Предоставляет функциональность для:
- Подключения к коллекции Anki
- Поиска заметок по колодам
- Извлечения текста из карточек
"""

import os
from typing import List, Dict, Any, Optional
from anki.storage import Collection
from .config import config


class AnkiIntegration:
    """Класс для интеграции с Anki"""
    
    def __init__(self, collection_path: str = None):
        """
        Инициализация интеграции с Anki
        
        Args:
            collection_path: Путь к файлу коллекции Anki (.anki2)
                           Если не указан, используется путь из конфигурации
        """
        self.collection_path = collection_path or config.get_collection_path()
        self.collection = None
        self._connected = False
    
    def __enter__(self):
        """Контекстный менеджер - вход"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер - выход"""
        self.disconnect()
    
    def connect(self) -> bool:
        """
        Подключается к коллекции Anki
        
        Returns:
            True если подключение успешно, False в противном случае
        """
        try:
            if not os.path.exists(self.collection_path):
                print(f"❌ Файл коллекции не найден: {self.collection_path}")
                return False
            
            self.collection = Collection(self.collection_path)
            self._connected = True
            print(f"✅ Подключение к Anki успешно: {self.collection_path}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка подключения к Anki: {e}")
            self._connected = False
            return False
    
    def disconnect(self):
        """Отключается от коллекции Anki"""
        if self.collection:
            try:
                self.collection.close()
                print("✅ Отключение от Anki успешно")
            except Exception as e:
                print(f"⚠️ Ошибка при отключении от Anki: {e}")
            finally:
                self.collection = None
                self._connected = False
    
    def is_connected(self) -> bool:
        """
        Проверяет, подключены ли к Anki
        
        Returns:
            True если подключены, False в противном случае
        """
        return self._connected and self.collection is not None
    
    def get_deck_names(self) -> List[str]:
        """
        Получает список названий всех колод
        
        Returns:
            Список названий колод
        """
        if not self.is_connected():
            return []
        
        try:
            deck_names = [deck['name'] for deck in self.collection.decks.all()]
            return deck_names
        except Exception as e:
            print(f"❌ Ошибка получения названий колод: {e}")
            return []
    
    def find_notes_by_deck(self, deck_pattern: str = None) -> List[int]:
        """
        Находит заметки по паттерну названия колоды
        
        Args:
            deck_pattern: Паттерн для поиска колод (например, "Spanish*")
                        Если не указан, используется паттерн из конфигурации
        
        Returns:
            Список ID заметок
        """
        if not self.is_connected():
            return []
        
        deck_pattern = deck_pattern or config.get_deck_pattern()
        
        try:
            # Используем поиск Anki для поиска заметок в колодах по паттерну
            note_ids = self.collection.find_notes(f"deck:{deck_pattern}")
            return note_ids
        except Exception as e:
            print(f"❌ Ошибка поиска заметок по колоде {deck_pattern}: {e}")
            return []
    
    def extract_text_from_notes(self, note_ids: List[int], field_names: List[str] = None) -> List[Dict[str, Any]]:
        """
        Извлекает текст из заметок по указанным полям
        
        Args:
            note_ids: Список ID заметок
            field_names: Список названий полей для извлечения
                        Если не указан, используются поля из конфигурации
        
        Returns:
            Список словарей с данными заметок
        """
        if not self.is_connected():
            return []
        
        field_names = field_names or config.get_field_names()
        notes_data = []
        
        try:
            for note_id in note_ids:
                note = self.collection.get_note(note_id)
                note_data = {
                    'note_id': note_id,
                    'texts': []
                }
                
                # Извлекаем текст из указанных полей
                for field_name in field_names:
                    try:
                        field_index = note.fields.index(field_name)
                        field_text = note.fields[field_index]
                        if field_text:
                            note_data['texts'].append(field_text)
                    except ValueError:
                        # Поле не найдено, пропускаем
                        continue
                
                notes_data.append(note_data)
                
        except Exception as e:
            print(f"❌ Ошибка извлечения текста из заметок: {e}")
        
        return notes_data
    
    def get_note_count(self, deck_pattern: str = None) -> int:
        """
        Получает количество заметок в колоде
        
        Args:
            deck_pattern: Паттерн для поиска колоды
        
        Returns:
            Количество заметок
        """
        note_ids = self.find_notes_by_deck(deck_pattern)
        return len(note_ids)
    
    def get_deck_info(self, deck_pattern: str = None) -> Dict[str, Any]:
        """
        Получает информацию о колоде
        
        Args:
            deck_pattern: Паттерн для поиска колоды
        
        Returns:
            Словарь с информацией о колоде
        """
        deck_pattern = deck_pattern or config.get_deck_pattern()
        note_ids = self.find_notes_by_deck(deck_pattern)
        
        return {
            'deck_pattern': deck_pattern,
            'note_count': len(note_ids),
            'deck_names': self.get_deck_names()
        }
