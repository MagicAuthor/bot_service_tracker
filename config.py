import os
from dotenv import load_dotenv, dotenv_values

#load_dotenv()

def reload_env():
    # Явно перезагружаем переменные окружения из файла .env
    env_values = dotenv_values(".env")
    for key, value in env_values.items():
        os.environ[key] = value

# Перезагружаем переменные перед их использованием
reload_env()

API_TOKEN = os.getenv('API_TOKEN')
ADMINS = list(map(int, os.getenv('ADMINS').split(',')))