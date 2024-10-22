import subprocess
import re

# Функция для получения статуса службы
def get_service_status(service_name) -> str:
    result = subprocess.run(["systemctl", "is-active", service_name], stdout=subprocess.PIPE)
    return "active" if result.stdout.decode().strip() == "active" else "inactive"

def get_service_info(service_name):
    # Получение статуса службы через systemctl
    status_output = subprocess.run(['systemctl', 'status', service_name], capture_output=True, text=True)
    # Извлечение информации из вывода
    active_match = re.search(r'Active:\s+(.+?)\s+since\s+.+?;\s*(.+)', status_output.stdout)
    pid_match = re.search(r'Main PID: (\d+)', status_output.stdout)
    memory_match = re.search(r'Memory:\s+([\d.]+[KMG]?)', status_output.stdout)
    cpu_match = re.search(r'CPU:\s+([\d.]+)', status_output.stdout)
    uptime_match = re.search(r'Active:\s+.*\s+since\s+(.+?)(?:\s+\(.*\))?', status_output.stdout)
    # Передача информации
    if active_match:
        status = active_match.group(1).strip()  # Получаем статус службы
        time_info = active_match.group(2).strip() if active_match.group(2) else "N/A"
        if "inactive" in status:
            is_active = f"Inactive ({time_info})"
        else:
            is_active = f"Active ({time_info})"
    else:
        is_active = "N/A"
    pid = pid_match.group(1) if pid_match else "N/A"
    memory = memory_match.group(1) if memory_match else "N/A"
    cpu = cpu_match.group(1) if cpu_match else "N/A"
    uptime = uptime_match.group(1) if uptime_match else "N/A"
    return {
        'is_active': is_active,
        'pid': pid,
        'memory': memory,
        'cpu': cpu,
        'uptime': uptime
    }

# функция для проверки существования службы
def is_service_exist(service_name: str) -> bool:
    try:
        # Используем systemctl для проверки, существует ли служба
        result = subprocess.run(
            ["systemctl", "status", service_name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return "Loaded" in result.stdout.decode()  # Проверяем, загружена ли служба
    except subprocess.CalledProcessError:
        return False