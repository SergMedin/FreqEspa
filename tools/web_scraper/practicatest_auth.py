#!/usr/bin/env python3
"""
Модуль авторизации для practicatest.com

Предоставляет функционал для:
- Входа в аккаунт practicatest.com
- Управления сессией
- Проверки статуса авторизации
- Безопасного выхода из аккаунта
"""

import os
import time
import logging
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class PracticaTestAuth:
    """Класс для авторизации на practicatest.com"""
    
    def __init__(self, config_file: str = None):
        """
        Инициализация модуля авторизации
        
        Args:
            config_file: Путь к файлу конфигурации
        """
        # Загружаем конфигурацию
        if config_file is None:
            # Ищем .env в корневой папке проекта
            project_root = Path(__file__).parent.parent.parent
            config_file = project_root / ".env"
        
        self.config = self._load_config(config_file)
        
        # Создаём сессию requests
        self.session = requests.Session()
        
        # Настройка User-Agent
        self.session.headers.update({
            'User-Agent': self.config.get('USER_AGENT', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        })
        
        # Статус авторизации
        self.is_authenticated = False
        self.login_time = None
        self.session_timeout = self.config.get('SESSION_TIMEOUT', 3600)
        
        # URL для авторизации
        self.base_url = self.config.get('PRACTICATEST_BASE_URL', 'https://practicatest.com')
        self.login_url = self.config.get('PRACTICATEST_LOGIN_URL', 'https://practicatest.com/login')
        self.tests_url = self.config.get('PRACTICATEST_TESTS_URL', 'https://practicatest.com/tests/permiso-B')
        
        logger.info("Модуль авторизации practicatest.com инициализирован")
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """
        Загружает конфигурацию из файла
        
        Args:
            config_file: Путь к файлу конфигурации
            
        Returns:
            Словарь с настройками
        """
        config = {}
        
        # Пытаемся загрузить .env файл
        env_path = Path(config_file)
        if env_path.exists():
            load_dotenv(env_path)
            logger.info(f"Конфигурация загружена из {config_file}")
        else:
            logger.warning(f"Файл конфигурации {config_file} не найден")
        
        # Загружаем переменные окружения
        config.update({
            'PRACTICATEST_EMAIL': os.getenv('PRACTICATEST_EMAIL'),
            'PRACTICATEST_PASSWORD': os.getenv('PRACTICATEST_PASSWORD'),
            'PRACTICATEST_BASE_URL': os.getenv('PRACTICATEST_BASE_URL', 'https://practicatest.com'),
            'PRACTICATEST_LOGIN_URL': os.getenv('PRACTICATEST_LOGIN_URL', 'https://practicatest.com/login'),
            'PRACTICATEST_TESTS_URL': os.getenv('PRACTICATEST_TESTS_URL', 'https://practicatest.com/tests/permiso-B'),
            'DOWNLOAD_DELAY_MIN': float(os.getenv('DOWNLOAD_DELAY_MIN', '3')),
            'DOWNLOAD_DELAY_MAX': float(os.getenv('DOWNLOAD_DELAY_MAX', '7')),
            'LOGIN_DELAY': float(os.getenv('LOGIN_DELAY', '2')),
            'SESSION_TIMEOUT': int(os.getenv('SESSION_TIMEOUT', '3600')),
            'MAX_RETRIES': int(os.getenv('MAX_RETRIES', '3')),
            'USER_AGENT': os.getenv('USER_AGENT', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        })
        
        return config
    
    def login(self) -> bool:
        """
        Выполняет вход в аккаунт practicatest.com
        
        Returns:
            True если вход успешен, False в противном случае
        """
        if not self.config.get('PRACTICATEST_EMAIL') or not self.config.get('PRACTICATEST_PASSWORD'):
            logger.error("Email или пароль не указаны в конфигурации")
            return False
        
        try:
            logger.info("Начинаю процесс авторизации на practicatest.com")
            
            # Сначала получаем главную страницу для получения cookies
            logger.info("Получаю главную страницу...")
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            # Небольшая задержка
            time.sleep(self.config.get('LOGIN_DELAY', 2))
            
            # Получаем страницу входа для анализа формы
            logger.info("Получаю страницу входа...")
            response = self.session.get(self.login_url, timeout=30)
            response.raise_for_status()
            
            # Анализируем форму входа (базовая реализация)
            # В реальности может потребоваться более сложный анализ
            login_data = {
                'email': self.config['PRACTICATEST_EMAIL'],
                'password': self.config['PRACTICATEST_PASSWORD'],
                'remember': '1'  # Запомнить пользователя
            }
            
            # Выполняем POST запрос для входа
            logger.info("Отправляю данные для входа...")
            response = self.session.post(
                self.login_url,
                data=login_data,
                timeout=30,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Проверяем успешность входа
            if self._check_login_success(response):
                self.is_authenticated = True
                self.login_time = datetime.now()
                logger.info("✅ Авторизация на practicatest.com успешна!")
                return True
            else:
                logger.error("❌ Авторизация не удалась")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка сети при авторизации: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при авторизации: {e}")
            return False
    
    def _check_login_success(self, response: requests.Response) -> bool:
        """
        Проверяет успешность входа
        
        Args:
            response: Ответ сервера после попытки входа
            
        Returns:
            True если вход успешен
        """
        # Проверяем по URL (если произошёл редирект на главную)
        if 'practicatest.com' in response.url and '/login' not in response.url:
            return True
        
        # Проверяем по содержимому страницы
        content = response.text.lower()
        
        # Ищем признаки успешного входа
        success_indicators = [
            'mi cuenta',  # Моя учётная запись
            'cerrar sesión',  # Выйти
            'logout',
            'welcome',
            'bienvenido'
        ]
        
        # Ищем признаки неудачного входа
        failure_indicators = [
            'error de autenticación',
            'credenciales incorrectas',
            'invalid credentials',
            'login failed'
        ]
        
        # Проверяем успешные индикаторы
        for indicator in success_indicators:
            if indicator in content:
                return True
        
        # Проверяем неудачные индикаторы
        for indicator in failure_indicators:
            if indicator in content:
                return False
        
        # Если не можем определить, считаем неудачным
        logger.warning("Не удалось определить статус авторизации")
        return False
    
    def is_session_valid(self) -> bool:
        """
        Проверяет валидность текущей сессии
        
        Returns:
            True если сессия активна
        """
        if not self.is_authenticated:
            return False
        
        # Проверяем время жизни сессии
        if self.login_time and datetime.now() - self.login_time > timedelta(seconds=self.session_timeout):
            logger.info("Сессия истекла по времени")
            self.is_authenticated = False
            return False
        
        # Проверяем доступ к защищённой странице
        try:
            response = self.session.get(self.tests_url, timeout=10)
            if response.status_code == 200:
                return True
            else:
                logger.info("Сессия недействительна (статус: {})".format(response.status_code))
                self.is_authenticated = False
                return False
        except Exception as e:
            logger.error(f"Ошибка при проверке сессии: {e}")
            self.is_authenticated = False
            return False
    
    def refresh_session(self) -> bool:
        """
        Обновляет сессию если необходимо
        
        Returns:
            True если сессия обновлена или активна
        """
        if self.is_session_valid():
            logger.info("Сессия активна, обновление не требуется")
            return True
        
        logger.info("Обновляю сессию...")
        return self.login()
    
    def logout(self) -> bool:
        """
        Выполняет выход из аккаунта
        
        Returns:
            True если выход успешен
        """
        try:
            if self.is_authenticated:
                # Отправляем запрос на выход (если есть такой endpoint)
                logout_url = f"{self.base_url}/logout"
                response = self.session.get(logout_url, timeout=10)
                
                # Очищаем состояние
                self.is_authenticated = False
                self.login_time = None
                
                logger.info("✅ Выход из аккаунта выполнен")
                return True
            else:
                logger.info("Не авторизован, выход не требуется")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка при выходе: {e}")
            # Всё равно очищаем состояние
            self.is_authenticated = False
            self.login_time = None
            return False
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Возвращает информацию о текущей сессии
        
        Returns:
            Словарь с информацией о сессии
        """
        info = {
            'is_authenticated': self.is_authenticated,
            'base_url': self.base_url,
            'tests_url': self.tests_url,
            'session_timeout': self.session_timeout
        }
        
        if self.login_time:
            info['login_time'] = self.login_time.isoformat()
            info['session_age'] = (datetime.now() - self.login_time).total_seconds()
            info['session_valid'] = self.is_session_valid()
        
        return info
    
    def close(self):
        """Закрывает сессию и очищает ресурсы"""
        try:
            if self.is_authenticated:
                self.logout()
            self.session.close()
            logger.info("Сессия practicatest.com закрыта")
        except Exception as e:
            logger.error(f"Ошибка при закрытии сессии: {e}")
    
    def __enter__(self):
        """Поддержка контекстного менеджера"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Автоматическое закрытие при выходе из контекста"""
        self.close()
