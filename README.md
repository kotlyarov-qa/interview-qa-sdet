# QA / SDET: стартовое окружение

Условие: [qa.pdf](qa.pdf). Контракт и данные: [CONTRACT.md](CONTRACT.md).
Эта папка самодостаточна: соседние задания для запуска не нужны.

## Запуск

Требуется Docker Engine/Desktop с Compose v2+, интернет для первой сборки.
Ориентир по ресурсам: 6 ГБ свободной RAM и 8 ГБ диска.
Проверено на Linux amd64; на другой архитектуре организатор сначала проверяет запуск
или выдаёт удалённую среду. При занятом порте измените PORT в `.env`.

```bash
cp .env.example .env
docker compose up -d --build --wait
docker compose exec -e AGENT_URL=http://localhost:8090 agent npm run preflight
```

Последняя команда выполняет полный агентный цикл на mock без платного API.
API: `http://localhost:8092`. Логи: `artifacts/runs.jsonl`.

```bash
curl http://localhost:8092/run \
  -H 'Authorization: Bearer demo-alice' \
  -H 'Content-Type: application/json' \
  -d '{"message":"Начисления 10001 за 2026-08","mode":"mock","tool_mode":"success"}'
```

## Разработка

Node 24.14.0 (`.nvmrc`), `npm ci`, `npm run typecheck`, `npm test`.
Без Node на хосте: `docker compose exec agent npm run typecheck` и `docker compose exec agent npm test`.
После изменения файлов пересоберите контейнер: `docker compose up -d --build --wait`.
Для запуска сервера на хосте: `PORT=8092 npm start` (сначала остановите Docker-сервис).
Python 3.12 + uv 0.11.6: `uv sync --frozen`, `uv run python scripts/sample_run.py`.
В примере один вызов API; evaluator и сценарии по PDF реализует кандидат.
Начальные npm-тесты проверяют инфраструктуру и не означают отсутствие учебного дефекта.

## Реальная модель

Организатор отдельно выдаёт coding agent и доступ к модели с квотой.
Заполните MODEL_* в `.env`, затем `docker compose up -d --force-recreate agent`.
Пример: `RUN_MODE=real uv run python scripts/sample_run.py`.
Ключ хранится только в `.env`, сервер не передаёт его клиенту. Не включайте `.env` в сдачу.
Прогон реальной модели до выдачи ключа имеет статус BLOCKED; mock его не заменяет.

## Сброс и сдача

Данные инструментов неизменяемые; каждый `/run` — новый граф без истории.
Сброс процесса: `docker compose restart agent`. Предыдущие JSONL не влияют на новые запуски;
сохраняйте их как доказательства, не очищайте перед сдачей.
Остановка: `docker compose down`.
Настройки coding agent, два skills, требуемые тесты, AI_USAGE.md и отчёт создаёт кандидат.

## Браузер: настоящий LibreChat

UI: http://localhost:3082. Версия v0.8.0, образ закреплён digest; исходный commit
`b7d13cec6f3a63c7b81f5781f6b5cab289e33d70`.

Создать локальный учебный логин один раз:
```bash
docker compose exec -T librechat npm run create-user -- candidate@example.test Candidate candidate demo-browser-password --email-verified=true
```
Войти с `candidate@example.test` / `demo-browser-password`.
В меню модели выбрать **alice-success → interview-mock**.
Отправить `Начисления 10001 за 2026-08`: ожидается 150000 коп.
Другие endpoint-профили переключают сессию/режим инструмента; `interview-real`
использует настоящую модель при заполненных MODEL_*.

Логин LibreChat — вход в тестовый интерфейс. Alice/Bob — две **учебные серверные
сессии инструментов**, выбранные конфигурацией endpoint, не роли пользователей LibreChat.
Оба профиля намеренно доступны тестировщику. Права проверяются по токену инструмента,
который модель не выбирает. Это стенд проверки агента, не проверка multi-tenant авторизации LibreChat.

Путь браузерной проверки: LibreChat UI → custom endpoint → bridge `/v1/chat/completions`
→ настоящий `@librechat/agents` → учебные инструменты. Встроенный Agent Builder LibreChat
в этой конфигурации не используется; объект проверки и все точки подмены описаны явно.

Playwright уже закреплён в npm: `npm ci`, `npx playwright install chromium`.
Конфигурация: `playwright.config.ts`; свои браузерные тесты добавляйте в `e2e/`.
На Linux для браузера могут понадобиться библиотеки: `npx playwright install --with-deps chromium`.

Новый сценарий начинайте с New chat. Полный сброс только этого учебного стенда:
`docker compose down -v`, `docker compose up -d --wait`, затем снова создайте логин.
Это удаляет историю чатов и пользователей локальной MongoDB.
Модель/инструменты не требуют внешнего Langfuse: JSONL достаточно.

## Работа и сдача через GitHub

Создайте отдельный репозиторий **в своём GitHub-аккаунте** и перенесите в него
только папку своего задания из стартового комплекта. Работайте и сохраняйте
результат в этом репозитории. Первый коммит — стартовый комплект, последующие
коммиты — изменения по ходу выполнения; сохраните историю работы.

Репозиторий может быть публичным или приватным. Для приватного заранее
предоставьте доступ проверяющему; его GitHub-аккаунт уточните у организатора.
Не публикуйте `.env`, ключи, лицензии и другие секреты.

Для сдачи отправьте:
- ссылку на свой GitHub-репозиторий и SHA финального коммита;
- README с командами запуска и проверок;
- код, тесты, отчёт и остальные артефакты из условия задания.

Одного ZIP-архива или patch вместо GitHub-репозитория недостаточно.
