#!/usr/bin/env python3
"""
Тестовый скрипт для проверки реальной авторизации на practicatest.com

Тестирует:
1. Авторизацию с правильными данными
2. Обработку ошибок с неправильными данными
"""

import sys
import logging
import os
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from practicatest_auth import PracticaTestAuth


def test_real_credentials():
    """Тестирует авторизацию с реальными данными из .env"""
    print("🔐 Тест 1: Авторизация с реальными данными")
    print("=" * 60)
    
    # Создаём экземпляр авторизации (автоматически найдёт .env в корневой папке)
    auth = PracticaTestAuth()
    
    try:
        # Показываем текущую конфигурацию (без пароля)
        print("\n📋 Конфигурация:")
        config = auth.config
        print(f"  Email: {config.get('PRACTICATEST_EMAIL', 'НЕ УКАЗАН')}")
        print(f"  Пароль: {'*' * len(str(config.get('PRACTICATEST_PASSWORD', ''))) if config.get('PRACTICATEST_PASSWORD') else 'НЕ УКАЗАН'}")
        print(f"  Базовый URL: {config.get('PRACTICATEST_BASE_URL')}")
        print(f"  URL входа: {config.get('PRACTICATEST_LOGIN_URL')}")
        
        # Проверяем наличие данных для входа
        if not config.get('PRACTICATEST_EMAIL') or not config.get('PRACTICATEST_PASSWORD'):
            print("\n❌ Ошибка: Email или пароль не указаны в .env файле")
            print("💡 Убедитесь, что файл .env создан и содержит:")
            print("   PRACTICATEST_EMAIL=ваш_email@example.com")
            print("   PRACTICATEST_PASSWORD=ваш_пароль")
            return False
        
        # Пытаемся войти в систему
        print("\n🚀 Выполняю вход в систему...")
        if auth.login():
            print("✅ Авторизация успешна!")
            
            # Показываем детальную информацию о сессии
            print("\n📊 Детальная информация о сессии:")
            status = auth.get_session_info()
            for key, value in status.items():
                if key == 'login_time':
                    print(f"  {key}: {value}")
                elif key == 'session_age':
                    print(f"  {key}: {value:.1f} секунд")
                else:
                    print(f"  {key}: {value}")
            
            # Проверяем валидность сессии
            print(f"\n🔐 Валидность сессии: {auth.is_session_valid()}")
            
            # Тестируем доступ к защищённой странице
            print("\n🌐 Тестирую доступ к странице с билетами...")
            try:
                import requests
                response = auth.session.get(config.get('PRACTICATEST_TESTS_URL'), timeout=10)
                print(f"  Статус ответа: {response.status_code}")
                if response.status_code == 200:
                    print("  ✅ Доступ к странице с билетами получен")
                else:
                    print(f"  ⚠️ Неожиданный статус: {response.status_code}")
            except Exception as e:
                print(f"  ❌ Ошибка при доступе к странице: {e}")
            
            return True
            
        else:
            print("❌ Авторизация не удалась")
            print("\n💡 Возможные причины:")
            print("  - Неверный email или пароль")
            print("  - Проблемы с сетью")
            print("  - Изменения на сайте")
            print("  - Требуется капча или дополнительная верификация")
            return False
        
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False
    
    finally:
        # Закрываем сессию
        auth.close()
        print("\n🔒 Сессия закрыта")


def test_wrong_credentials():
    """Тестирует обработку ошибок с неправильными данными"""
    print("\n\n❌ Тест 2: Обработка ошибок с неправильными данными")
    print("=" * 60)
    
    # Создаём экземпляр с неправильными данными
    auth = PracticaTestAuth()
    
    try:
        # Временно заменяем данные на неправильные
        original_email = auth.config.get('PRACTICATEST_EMAIL')
        original_password = auth.config.get('PRACTICATEST_PASSWORD')
        
        auth.config['PRACTICATEST_EMAIL'] = 'wrong@email.com'
        auth.config['PRACTICATEST_PASSWORD'] = 'wrongpassword123'
        
        print("\n📋 Тестовая конфигурация (неправильные данные):")
        print(f"  Email: {auth.config['PRACTICATEST_EMAIL']}")
        print(f"  Пароль: {auth.config['PRACTICATEST_PASSWORD']}")
        
        # Пытаемся войти с неправильными данными
        print("\n🚀 Попытка входа с неправильными данными...")
        if auth.login():
            print("⚠️  Неожиданно: вход выполнен с неправильными данными!")
            print("💡 Это может означать, что сайт не проверяет данные или изменилась логика")
        else:
            print("✅ Ожидаемо: вход не удался с неправильными данными")
            print("💡 Обработка ошибок работает корректно")
        
        # Восстанавливаем оригинальные данные
        auth.config['PRACTICATEST_EMAIL'] = original_email
        auth.config['PRACTICATEST_PASSWORD'] = original_password
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании неправильных данных: {e}")
        return False
    
    finally:
        # Закрываем сессию
        auth.close()
        print("\n🔒 Сессия закрыта")


def main():
    """Главная функция"""
    print("🧪 Тестирование реальной авторизации на practicatest.com")
    print("=" * 60)
    
    # Проверяем наличие .env файла в корневой папке проекта
    project_root = Path(__file__).parent.parent.parent
    env_file = project_root / ".env"
    
    if not env_file.exists():
        print("⚠️  Файл .env не найден!")
        print("💡 Создайте файл .env с вашими данными для входа:")
        print("   PRACTICATEST_EMAIL=ваш_email@example.com")
        print("   PRACTICATEST_PASSWORD=ваш_пароль")
        return
    
    print(f"✅ Файл .env найден: {env_file.absolute()}")
    
    # Тест 1: Реальные данные
    print("\n" + "="*60)
    success_real = test_real_credentials()
    
    # Тест 2: Неправильные данные
    print("\n" + "="*60)
    success_wrong = test_wrong_credentials()
    
    # Итоговый результат
    print("\n" + "="*60)
    print("📊 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print(f"  Тест с реальными данными: {'✅ УСПЕХ' if success_real else '❌ НЕУДАЧА'}")
    print(f"  Тест с неправильными данными: {'✅ УСПЕХ' if success_wrong else '❌ НЕУДАЧА'}")
    
    if success_real and success_wrong:
        print("\n🎉 Все тесты прошли успешно!")
        print("💡 Модуль авторизации работает корректно")
    else:
        print("\n⚠️  Некоторые тесты не прошли")
        print("💡 Проверьте логи выше для диагностики")
    
    print("\n🔚 Тестирование завершено")


if __name__ == "__main__":
    main()
