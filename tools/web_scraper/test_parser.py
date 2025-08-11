#!/usr/bin/env python3
"""
Тестовый скрипт для проверки парсера practicatest.com

Этот скрипт демонстрирует работу парсера:
1. Авторизация
2. Переход на страницу с тестами
3. Поиск раздела "Test del Permiso B"
4. Поиск кнопки "VER LOS TEST"
5. Получение таблицы с тестами
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

from practicatest_auth import PracticaTestAuth
from practicatest_parser import PracticaTestParser


def test_parser_functionality():
    """Тестирует основной функционал парсера"""
    print("🧪 Тестирование парсера practicatest.com")
    print("=" * 60)
    
    # Создаём экземпляр авторизации
    auth = PracticaTestAuth()
    
    try:
        # Авторизуемся
        print("\n🔐 Шаг 1: Авторизация...")
        if not auth.login():
            print("❌ Авторизация не удалась")
            return False
        
        print("✅ Авторизация успешна!")
        
        # Создаём парсер
        print("\n🔍 Шаг 2: Создание парсера...")
        parser = PracticaTestParser(auth.session)
        print("✅ Парсер создан")
        
        # Переходим на страницу с тестами
        print("\n🌐 Шаг 3: Переход на страницу с тестами...")
        if not parser.navigate_to_tests_page():
            print("❌ Не удалось перейти на страницу с тестами")
            return False
        
        print("✅ Переход на страницу с тестами успешен")
        
        # Анализируем структуру страницы
        print("\n📊 Шаг 4: Анализ структуры страницы...")
        debug_info = parser.debug_page_structure()
        
        print("📋 Информация о странице:")
        print(f"  URL: {debug_info.get('url', 'НЕ ИЗВЕСТЕН')}")
        print(f"  Заголовок: {debug_info.get('title', 'НЕ НАЙДЕН')}")
        print(f"  Размер страницы: {debug_info.get('page_size', 0)} байт")
        print(f"  Количество таблиц: {debug_info.get('tables_count', 0)}")
        print(f"  Количество форм: {debug_info.get('forms_count', 0)}")
        print(f"  Количество модальных окон: {debug_info.get('modals_count', 0)}")
        
        print("\n📝 Заголовки на странице:")
        for i, header in enumerate(debug_info.get('headers', [])[:10], 1):
            print(f"  {i}. {header}")
        
        print("\n🔘 Кнопки на странице:")
        for i, button in enumerate(debug_info.get('buttons', [])[:10], 1):
            print(f"  {i}. {button}")
        
        print("\n🔗 Ссылки на странице:")
        for i, link in enumerate(debug_info.get('links', [])[:10], 1):
            print(f"  {i}. {link}")
        
        # Ищем раздел "Test del Permiso B"
        print("\n🎯 Шаг 5: Поиск раздела 'Test del Permiso B'...")
        test_section = parser.find_test_section()
        
        if test_section:
            print("✅ Раздел 'Test del Permiso B' найден")
            print(f"  HTML: {str(test_section)[:200]}...")
        else:
            print("⚠️ Раздел 'Test del Permiso B' не найден")
        
        # Ищем кнопку "VER LOS TEST"
        print("\n🔘 Шаг 6: Поиск кнопки 'VER LOS TEST'...")
        ver_button = parser.find_ver_los_test_button()
        
        if ver_button:
            print("✅ Кнопка 'VER LOS TEST' найдена")
            print(f"  Тип: {ver_button.name}")
            print(f"  HTML: {str(ver_button)[:200]}...")
        else:
            print("⚠️ Кнопка 'VER LOS TEST' не найдена")
        
        # Пытаемся получить таблицу с тестами
        print("\n📋 Шаг 7: Получение таблицы с тестами...")
        tests_data = parser.parse_tests_data()
        
        if tests_data:
            print(f"✅ Найдено {len(tests_data)} тестов")
            print("\n📊 Данные тестов:")
            for i, test in enumerate(tests_data[:5], 1):  # Показываем первые 5
                print(f"  Тест {i}:")
                for key, value in test.items():
                    if key != 'raw_html':
                        print(f"    {key}: {value}")
                    else:
                        print(f"    {key}: {str(value)[:100]}...")
        else:
            print("⚠️ Данные тестов не найдены")
        
        # Получаем содержимое текущей страницы
        print("\n📄 Шаг 8: Получение содержимого страницы...")
        page_content = parser.get_page_content()
        
        if page_content:
            print(f"✅ Содержимое страницы получено ({len(page_content)} символов)")
            print(f"  Первые 500 символов: {page_content[:500]}...")
        else:
            print("❌ Не удалось получить содержимое страницы")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании парсера: {e}")
        return False
    
    finally:
        # Закрываем сессию
        auth.close()
        print("\n🔒 Сессия закрыта")


def main():
    """Главная функция"""
    print("🚀 Запуск тестирования парсера practicatest.com")
    print("=" * 60)
    
    # Проверяем наличие .env файла
    project_root = Path(__file__).parent.parent.parent
    env_file = project_root / ".env"
    
    if not env_file.exists():
        print("⚠️  Файл .env не найден!")
        print("💡 Создайте файл .env с вашими данными для входа:")
        print("   PRACTICATEST_EMAIL=ваш_email@example.com")
        print("   PRACTICATEST_PASSWORD=ваш_пароль")
        return
    
    print(f"✅ Файл .env найден: {env_file.absolute()}")
    
    # Тестируем парсер
    success = test_parser_functionality()
    
    # Итоговый результат
    print("\n" + "="*60)
    if success:
        print("🎉 Тестирование парсера завершено успешно!")
        print("💡 Парсер готов к работе")
    else:
        print("⚠️  Тестирование парсера не завершено")
        print("💡 Проверьте логи выше для диагностики")
    
    print("\n🔚 Тестирование завершено")


if __name__ == "__main__":
    main()
