Log Viewer
===========

Описание
--------
Простое приложение для просмотра логов. Состоит из фронтенда (static HTML) и бэкенда на FastAPI. Предназначено для развёртывания на удалённой ноде (например, node1) с помощью Ansible, либо запуска локально для разработки.

Цели
-----
- Быстрый просмотр логов через веб-интерфейс.
- Лёгкое локальное тестирование и запуск.
- Развёртывание на сервере через Ansible.

Репозиторий для клона (используется в плейбуке Ansible):
https://github.com/psych0panda/log_viewer.git

Структура проекта (важные части)
--------------------------------
- backend/ — FastAPI-приложение
- frontend/ — статическая страница
- ansible/ — плейбук и инвентори для развёртывания

Требования
----------
Python 3.11+ (или 3.x с поддержкой venv)

Локальная установка (рекомендуемый рабочий процесс)
---------------------------------------------------
1) В корне репозитория создайте виртуальное окружение и активируйте его:

```bash
python3 -m venv .venv
# Для zsh/bash
source .venv/bin/activate
```

Если создание venv завершается с ошибкой про ensurepip, на Debian/Ubuntu установите пакет `python3-venv`:

```bash
sudo apt update && sudo apt install -y python3-venv
```

2) Установите зависимости:

```bash
pip install -r backend/requirements.txt
```

3) Запустите сервер разработки:

```bash
# из корня репозитория
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

По умолчанию сервер будет доступен на http://localhost:8000 (локально) или http://<node-host>:8000 (на удалённой ноде).

Быстрая проверка импорта (после активации venv):

```bash
python -c "import fastapi; print('fastapi', fastapi.__version__)"
```

Ansible: типичные ошибки и их исправления
----------------------------------------
Если при выполнении плейбука на удалённой ноде (например, node1) вы видите ошибки, обратите внимание на два распространённых момента:

1) "The virtual environment was not created successfully because ensurepip is not available"
   - На сервере отсутствует пакет `python3-venv`. Добавьте задачу apt в плейбук до создания venv, например:

```yaml
- name: Убедиться, что python3-venv установлен
  apt:
    name: python3-venv
    state: present
    update_cache: yes
```

2) Ошибка поиска `requirements.txt` с путём вида `/opt/log_viewer/log_viewer/backend/requirements.txt`
   - Это происходит, когда репозиторий клонируется в папку `/opt/log_viewer`, а внутри репозитория снова есть `log_viewer` — проверьте путь в задаче git и используйте корректный `dest`.
   - В плейбуке должно быть что-то вроде `dest: /opt/log_viewer` и затем ссылка на `backend/requirements.txt` как `/opt/log_viewer/backend/requirements.txt` (без дублирования `log_viewer` в пути).

Рекомендуемые проверки в плейбуке:
- Правильный `dest` при клоне репозитория
- Наличие пакета `python3-venv` перед созданием venv
- Использовать `pip` из venv: `/opt/log_viewer/venv/bin/pip3 install -r /opt/log_viewer/backend/requirements.txt`

Примечания по веткам Git
-----------------------
Плейбуки не должны принудительно менять ветку `master->main`. Проверяйте, что в задачах git не указано `version: main`, если ваша ветка называется `master`. Лучше передавать переменную `repo_version` и использовать её в плейбуке.

Готово
------
README добавлен. Если нужно, могу также подправить ваш Ansible-плейбук (`ansible/configure_docker_logging.yml`) чтобы фиксировать ошибки с venv и путями автоматически — скажите, и я внесу конкретные правки.

