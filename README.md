# Тестовое задание: AI-first QA / SDET Engineer — LibreChat ЖКХ Агент

* **Кандидат:** Павел Котляров ([GitHub: kotlyarov-qa](https://github.com/kotlyarov-qa))
* **Email:** `pavel.kotlyarov.it@gmail.com`
* **Объект проверки:** LibreChat в Docker, сценарий «Сведения о начислениях ЖКХ».

---

## 1. Быстрый старт (Запуск окружения)

Требуется Docker Engine / Docker Desktop и Python 3.11+.

```bash
# 1. Клонирование и подготовка .env
cp .env.example .env

# 2. Поднятие контейнеров (агент + LibreChat UI + MongoDB)
docker compose up -d --build --wait

# 3. Установка тестовых зависимостей Python
pip install -r requirements.txt
playwright install chromium
```

Сервисы доступны:
* **LibreChat Web UI:** `http://localhost:3082`
* **Agent Bridge API:** `http://localhost:8092`
* **Трассы и логи:** `artifacts/runs.jsonl`

---

## 2. Запуск тестов одной командой

### Регрессионный набор (API тесты контрактов, прав и дефекта):
```bash
pytest tests/test_agent_api.py -v
```
> **Результат:** 7 PASS, 1 FAIL. 
> Падающий тест `test_08_EDUCATIONAL_DEFECT_timeout_masks_as_ok` возвращает ненулевой код выхода (Exit Code 1), доказывая наличие учебного дефекта в `src/adapter.ts`.

### Браузерный UI Smoke-тест на Playwright:
```bash
pytest tests/test_chat_smoke.py -v
```
*(Также доступен TypeScript-вариант в `e2e/chat.spec.ts`: `npx playwright test`)*.

### Запуск всего набора тестов:
```bash
pytest -v
```

---

## 3. Найденный учебный дефект

* **Где зашит:** `src/adapter.ts:3`
  ```typescript
  export function adaptCharges(result: Result<Charge[]>): Result<Charge[]> {
    if (result.status === 'timeout') return { status: 'ok', data: [] };
    return result;
  }
  ```
* **Суть дефекта:** При таймауте источника данных начислений адаптер стирает ошибку `timeout` и передает агенту успешный статус `ok` с пустым списком начислений. В результате агент дезинформирует жителя заявлением: *«Начислено 0 коп. Источник успешно прочитан»*.
* **Нарушение контракта:** Прямое нарушение правила из `qa.pdf`: *«Таймаут, ошибка и запрет доступа не означают нулевые начисления»*.
* **Подробный баг-репорт:** См. [docs/BUG_REPORT.md](docs/BUG_REPORT.md).

---

## 4. Сценарий живого изменения для защиты (Live Demo для Антона)

Для демонстрации взаимосвязи моков и ассертов:
1. Открываем `src/adapter.ts` и исправляем дефект, возвращая чистый `result`:
   ```typescript
   export function adaptCharges(result: Result<Charge[]>): Result<Charge[]> {
     return result; // Убираем маскирование timeout -> ok
   }
   ```
2. Пересобираем агент: `docker compose up -d --build --wait agent`.
3. Запускаем тест `test_08_EDUCATIONAL_DEFECT_timeout_masks_as_ok`.
4. **Результат:** Тест теперь проверяет, что статус `timeout` успешно дошел до выхода, и тест проходит (PASS).

---

## 5. Документация проекта

* 📋 [docs/TEST_MATRIX.md](docs/TEST_MATRIX.md) — Матрица 10 сценариев с приоритетами, рисками и статусами.
* 🐛 [docs/BUG_REPORT.md](docs/BUG_REPORT.md) — Воспроизводимый баг-репорт с цепочкой событий из трейса.
* 🚦 [docs/RELEASE_DECISION.md](docs/RELEASE_DECISION.md) — Заключение о блокировке релиза (NO-GO).
* 🤖 [docs/AI_USAGE.md](docs/AI_USAGE.md) — Отчет об использовании coding agent, навыки и ручные исправления.
* 🛠 [skills/](skills/) — Настроенные скиллы агента (`add-regression-test`, `analyze-trace`).
