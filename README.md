# Тестовое задание: AI-first QA / SDET Engineer - LibreChat ЖКХ Агент

* **Кандидат:** Павел Котляров ([GitHub: kotlyarov-qa](https://github.com/kotlyarov-qa))
* **Email:** `pavel.kotlyarov.it@gmail.com`
* **Объект проверки:** LibreChat в Docker, сценарий «Сведения о начислениях ЖКХ».

---

## 1. Быстрый старт (Запуск окружения)

Требуется Docker Engine / Docker Desktop и Python 3.11+.

```bash
# 1. Подготовка файла конфигурации
cp .env.example .env

# 2. Поднятие контейнеров (агент + LibreChat UI + MongoDB)
docker compose up -d --build --wait

# 3. Установка зависимостей для тестов
pip install -r requirements.txt
playwright install chromium
```

Точки входа:
* **LibreChat Web UI:** `http://localhost:3082`
* **Agent Bridge API:** `http://localhost:8092`
* **Логи и трассы:** `artifacts/runs.jsonl`

---

## 2. Запуск тестов

### Регрессионный набор (API тесты контрактов, прав и дефекта):
```bash
pytest tests/test_agent_api.py -v
```
> **Результат:** 7 PASS, 1 FAIL.
> Тест `test_08_EDUCATIONAL_DEFECT_timeout_masks_as_ok` падает с ненулевым кодом выхода (Exit Code 1), подтверждая наличие зашитого учебного дефекта в `src/adapter.ts`.

### Браузерный UI Smoke-тест на Playwright:
```bash
pytest tests/test_chat_smoke.py -v
```
*(Также доступен TypeScript-вариант в `e2e/chat.spec.ts`: `npx playwright test`)*.

### Запуск всего набора тестов:
```bash
pytest -v
```

### Запуск с реальной моделью и точки подмены (Mock / Real):
* **Точки подмены:** Переключение режима агента на моки или внешнюю LLM осуществляется параметром `"mode": "mock"` / `"mode": "real"` в payload `/agent/run`. В режиме `mock` используются детерминированные синтетические данные, исключающие флаппинг.
* **Запуск проверки шлюза реальной модели:**
  ```bash
  pytest tests/test_agent_api.py -k test_07_real_model_gate_blocked -v
  ```
  *(При отсутствии переменной `MODEL_API_KEY` в `.env` тест проверяет гейт защиты: сервис корректно возвращает HTTP 503 со статусом `BLOCKED`, не допуская падения тестов из-за отсутствия внешнего ключа).*

---


## 3. Найденный учебный дефект

* **Где находится:** `src/adapter.ts:3`
  ```typescript
  export function adaptCharges(result: Result<Charge[]>): Result<Charge[]> {
    if (result.status === 'timeout') return { status: 'ok', data: [] };
    return result;
  }
  ```
* **Суть бага:** При таймауте базы данных начислений адаптер стирает ошибку `timeout` и передает модели статус `ok` с пустым списком начислений. В результате агент пишет жителю: *«Начислено 0 коп. Источник успешно прочитан»*.
* **Нарушение контракта:** Нарушено правило из `qa.pdf`: *«Таймаут, ошибка и запрет доступа не означают нулевые начисления»*.
* **Баг-репорт:** См. [docs/BUG_REPORT.md](docs/BUG_REPORT.md).

---

## 4. Сценарий живого изменения (Live demo на защите)

Для демонстрации связи моков и ассертов:
1. Открываем `src/adapter.ts` и убираем подмену статуса:
   ```typescript
   export function adaptCharges(result: Result<Charge[]>): Result<Charge[]> {
     return result; // Пробрасываем реальный статус без подмены
   }
   ```
2. Пересобираем контейнер агента: `docker compose up -d --build --wait agent`.
3. Повторно запускаем тест: `pytest tests/test_agent_api.py -v`.
4. **Результат:** Статус `timeout` доходит до выхода без искажений, тест становится зеленым (PASS).

---

## 5. Документация проекта

* [docs/TEST_MATRIX.md](docs/TEST_MATRIX.md) - Матрица сценариев с приоритетами, рисками и статусами.
* [docs/BUG_REPORT.md](docs/BUG_REPORT.md) - Баг-репорт с цепочкой событий из трейса.
* [docs/RELEASE_DECISION.md](docs/RELEASE_DECISION.md) - Заключение о блокировке релиза (NO-GO).
* [docs/AI_USAGE.md](docs/AI_USAGE.md) - Отчет об использовании coding agent, навыки и ручные правки.
* [skills/](skills/) - Настроенные скиллы агента (`add-regression-test`, `analyze-trace`).
