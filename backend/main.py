import subprocess
import json
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
import uvicorn
from typing import Optional

app = FastAPI()

# Добавляем CORS middleware для разрешения запросов от фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажите конкретные origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Конфигурация
GCE_INSTANCE_NAMES = ['neuroboss-service-prod', 'rag-service-prod', 'agent-service-prod']
GCE_ZONE = 'us-central1-a'

def get_docker_containers_gcloud(instance_name, zone):
    """
    Получает список Docker-контейнеров на GCE инстансе,
    используя `gcloud compute ssh`.
    """
    # Команда для получения списка контейнеров в формате JSON
    # Флаг --format '{{json .}}' выводит по одному JSON объекту на строку
    # Используем `sudo` на случай, если пользователь не в группе docker
    command = "sudo docker ps --format '{{json .}}'"
    try:
        # Выполняем команду на удаленной машине
        gcloud_command = [
            'gcloud', 'compute', 'ssh', f'psychopanda@{instance_name}',
            '--zone', zone,
            '--ssh-flag=-T',
            '--command', command,
            '--quiet'
        ]
        result = subprocess.run(
            gcloud_command,
            capture_output=True,
            text=True,
            check=True
        )
        # Каждая строка вывода - это отдельный JSON объект для контейнера
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                containers.append(json.loads(line))
        return containers
    except FileNotFoundError:
        error_msg = f"Error: gcloud command not found for {instance_name}"
        print(error_msg)
        return error_msg
    except subprocess.CalledProcessError as e:
        error_msg = f"Error running gcloud for {instance_name}: {e.stderr}"
        print(error_msg)
        return error_msg

def get_container_logs_gcloud(instance_name, zone, container_id_or_name):
    """
    Получает логи для указанного Docker-контейнера на GCE инстансе.

    Args:
        instance_name (str): Имя GCE инстанса.
        zone (str): Зона GCE инстанса.
        container_id_or_name (str): Имя или ID контейнера.

    Returns:
        str: Логи контейнера или None в случае ошибки.
    """
    command = f"sudo docker logs {container_id_or_name}"

    try:
        gcloud_command = [
            'gcloud', 'compute', 'ssh', f'psychopanda@{instance_name}',
            '--zone', zone,
            '--ssh-flag=-T',
            '--command', command,
            '--quiet'
        ]
        result = subprocess.run(
            gcloud_command,
            capture_output=True,
            text=True,
            check=True
        )
        # Объединяем stdout и stderr для полных логов
        full_logs = result.stdout + result.stderr
        return full_logs
    except subprocess.CalledProcessError as e:
        error_msg = f"Error running gcloud for {instance_name}: {e.stderr}"
        print(error_msg)
        return None

@app.get("/")
def read_root():
    return FileResponse("frontend/index.html")

@app.get("/api/nodes")
def get_nodes():
    nodes = [{"id": name, "name": name} for name in GCE_INSTANCE_NAMES]
    return {"nodes": nodes}

@app.get("/api/containers")
def get_containers(node: str):
    containers = get_docker_containers_gcloud(node, GCE_ZONE)
    if isinstance(containers, str):
        raise HTTPException(status_code=500, detail=containers)
    container_names = [c.get('Names', c.get('ID', '')) for c in containers]
    return {"containers": container_names}

@app.get("/api/logs")
def get_logs(node: str, container: str):
    logs = get_container_logs_gcloud(node, GCE_ZONE, container)
    if logs is None:
        raise HTTPException(status_code=500, detail="Error fetching logs")
    # Логируем количество строк для диагностики
    lines_count = len(logs.split('\n'))
    print(f"Logs for {container} on {node}: {lines_count} lines")
    # Для streaming, но пока возвращаем как текст
    return StreamingResponse(iter([logs]), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=27015)
