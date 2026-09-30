"""
Браузерная smoke-проверка веб-интерфейса LibreChat на Playwright.
Покрывает требование раздела 1 ТЗ (qa.pdf):
'Включите одну браузерную smoke-проверку отправки сообщения и отображения результата'.
"""

import os
import pytest
from playwright.sync_api import sync_playwright

UI_URL = os.getenv("UI_URL", "http://localhost:3082")
USER_EMAIL = os.getenv("TEST_USER_EMAIL", "pavel@test.local")
USER_PASSWORD = os.getenv("TEST_USER_PASSWORD", "12345678")

def test_chat_smoke_alice_success():
    """
    SCENARIO-09 [P0 / UI Smoke]:
    Проверка сквозного пользовательского пути в LibreChat:
    1. Переход на страницу логина
    2. Авторизация пользователя
    3. Отправка сообщения о начислениях в чат
    4. Проверка отображения ответа агента с корректной суммой 150000 коп.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # 1. Открытие страницы логина
        page.goto(f"{UI_URL}/login")
        page.wait_for_selector("#email", timeout=10000)

        # 2. Авторизация
        page.fill("#email", USER_EMAIL)
        page.fill("#password", USER_PASSWORD)
        page.click("button[type=submit]")

        # 3. Ожидание перехода в чат
        page.wait_for_url("**/c/**", timeout=15000)

        # 4. Поиск поля ввода сообщения и отправка запроса
        textarea = page.wait_for_selector("#prompt-textarea, textarea", timeout=10000)
        assert textarea is not None, "Поле ввода сообщения чата не найдено"
        
        test_message = "Начисления 10001 за 2026-08"
        textarea.fill(test_message)
        page.keyboard.press("Enter")

        # 5. Ожидание и валидация ответа агента в DOM-дереве
        # Используем .first для предотвращения strict mode violation при наличии aria-live дубликата
        reply_locator = page.locator("text=150000").first
        reply_locator.wait_for(state="visible", timeout=15000)
        
        assert reply_locator.is_visible(), "Ответ агента с суммой 150000 коп не отобразился в чате"
        
        account_locator = page.locator("text=10001").first
        assert account_locator.is_visible(), "Номер счета 10001 не найден в истории диалога"

        browser.close()
