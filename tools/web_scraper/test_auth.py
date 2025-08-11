#!/usr/bin/env python3
"""
Тестовый скрипт для проверки авторизации на practicatest.com

Этот скрипт демонстрирует работу модуля авторизации
"""

import sys
import logging
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from tools.web_scraper import PracticaTestAuth, DrivingTestsDownloader


def test_auth_module():
    """Тестирует модуль авторизации"""
    print("🔐 Тестирование модуля авторизации practicatest.com")
    print("=" * 60)
    
    # Создаём экземпляр авторизации
    auth = PracticaTestAuth()
    
    try:
        # Показываем текущую конфигурацию
        print("\n📋 Текущая конфигурация:")
        config = auth.config
        for key, value in config.items():
            if 'PASSWORD' in key:
                print(f"  {key}: {'*' * len(str(value)) if value else 'НЕ УКАЗАН'}")
            else:
                print(f"  {key}: {value}")
        
        # Проверяем статус авторизации
        print("\n🔍 Статус авторизации:")
        status = auth.get_session_info()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # Пытаемся войти в систему
        print("\n🚀 Попытка входа в систему...")
        if auth.login():
            print("✅ Вход выполнен успешно!")
            
            # Показываем обновлённый статус
            print("\n📊 Обновлённый статус:")
            status = auth.get_session_info()
            for key, value in status.items():
                print(f"  {key}: {value}")
            
            # Проверяем валидность сессии
            print(f"\n🔐 Валидность сессии: {auth.is_session_valid()}")
            
        else:
            print("❌ Вход не удался")
            print("\n💡 Возможные причины:")
            print("  - Неверный email или пароль")
            print("  - Файл config.env не создан")
            print("  - Переменные окружения не настроены")
            print("  - Проблемы с сетью")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
    
    finally:
        # Закрываем сессию
        auth.close()
        print("\n🔒 Сессия закрыта")


def test_downloader_with_auth():
    """Тестирует загрузчик с авторизацией"""
    print("\n\n📥 Тестирование загрузчика с авторизацией")
    print("=" * 60)
    
    # Создаём загрузчик
    downloader = DrivingTestsDownloader()
    
    try:
        # Показываем статус авторизации
        print("\n🔍 Статус авторизации загрузчика:")
        auth_status = downloader.get_auth_status()
        for key, value in auth_status.items():
            print(f"  {key}: {value}")
        
        # Пытаемся загрузить тестовую страницу
        print("\n🚀 Попытка загрузки тестовой страницы...")
        success = downloader.download_test_page(1, "test_auth_page.html")
        
        if success:
            print("✅ Страница загружена успешно!")
        else:
            print("❌ Загрузка страницы не удалась")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании загрузчика: {e}")
    
    finally:
        # Закрываем загрузчик
        downloader.close()
        print("\n🔒 Загрузчик закрыт")


def main():
    """Главная функция"""
    print("🧪 Тестирование модуля авторизации practicatest.com")
    print("=" * 60)
    
    # Проверяем наличие файла конфигурации
    config_file = Path("config.env")
    if not config_file.exists():
        print("⚠️  Файл config.env не найден!")
        print("💡 Создайте файл config.env на основе config.env.example")
        print("💡 Укажите ваши реальные email и пароль")
        return
    
    # Тестируем модуль авторизации
    test_auth_module()
    
    # Тестируем загрузчик с авторизацией
    test_downloader_with_auth()
    
    print("\n🎉 Тестирование завершено!")


if __name__ == "__main__":
    main()
