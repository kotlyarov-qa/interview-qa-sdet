---
name: add-regression-test
description: Скилл для создания детерминированного регрессионного автотеста на Python/Pytest по контракту AI-агента.
---

# Skill: Добавление регрессионного теста (add-regression-test)

## Назначение
Используется coding agent для автоматической генерации тестовых функций на Pytest при появлении новых сценариев или требований контракта агента ЖКХ.

## Правила генерации теста:
1. **Не полагаться только на текст `answer`:**
   Обязательно валидировать структуру `events`:
   - Названия вызванных инструментов (`get_account`, `get_charges`).
   - Переданные аргументы (`account_number`, `account_id`, `period`).
   - Исходный ответ сервиса (`source.status`).
   - Переданный агенту результат (`result.status`, `result.data`).
2. **Проверка прав и сессий:**
   - Для Alice использовать токен `demo-alice` (счет 10001).
   - Для Bob использовать токен `demo-bob` (счет 20002).
   - Проверять разграничение доступа на уровне инструмента, а не только вежливый отказ модели.
3. **Строгая валидация числовых значений:**
   - Суммы начислений проверяются в копейках (целые числа).

## Шаблон теста:
```python
def test_scenario_name(agent_client, alice_headers):
    payload = {
        "message": "<запрос>",
        "mode": "mock", # или real
        "tool_mode": "success" # success, empty, timeout, forbidden, error, injection
    }
    response = agent_client.post("/run", headers=alice_headers, json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Валидация цепочки событий
    assert len(data["events"]) > 0
    # Проверка свойств контракта
    ...
```
