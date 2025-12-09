from datetime import datetime, timedelta
from pathlib import Path
import base64
import requests
import re

# ==========================
# CONFIGURACIÓN API
# ==========================

BASE_URL = "https://splynx.ipnext.com.ar/api/2.0"

API_KEY = "xxx"
API_SECRET = "xxx"

auth = base64.b64encode(f"{API_KEY}:{API_SECRET}".encode()).decode()
HEADERS = {
    "Authorization": f"Basic {auth}",
    "Accept": "application/json"
}

# ==========================
# DETECCIÓN AUTOMÁTICA DEL ESCRITORIO
# ==========================

home = Path.home()

if (home / "Desktop").exists():
    DESKTOP = home / "Desktop"
elif (home / "Escritorio").exists():
    DESKTOP = home / "Escritorio"
else:
    DESKTOP = home  # fallback

BASE_DIR = DESKTOP / "Splynx_Comentarios"
BASE_DIR.mkdir(exist_ok=True)


# ==========================
# FUNCIONES AUXILIARES
# ==========================

def sanitize_filename(name: str) -> str:
    if not name:
        name = "sin_nombre"
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:150]


def get_yesterday_date():
    today = datetime.now().date()
    return today - timedelta(days=1)


def get_comments_for_date(target_date):
    """
    Trae TODOS los comentarios y filtra por fecha YYYY-MM-DD.
    """
    date_str = target_date.strftime("%Y-%m-%d")
    url = f"{BASE_URL}/admin/scheduling/tasks-comments"

    resp = requests.get(url, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    comentarios = data["data"] if isinstance(data, dict) else data
    return [c for c in comentarios if c["created_at"][:10] == date_str]


def get_task(task_id: int):
    """
    Trae una task para obtener info del técnico, título, cliente, estado, etc.
    """
    url = f"{BASE_URL}/admin/scheduling/tasks/{task_id}"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data["data"] if isinstance(data, dict) and "data" in data else data


def get_technician_name(task: dict, comments: list):
    tech = (
        task.get("technician_name")
        or task.get("employee_name")
        or task.get("user_name")
        or (task.get("employee") or {}).get("name")
    )
    if tech:
        return tech

    # fallback: nombre del admin que comentó
    if comments:
        return comments[0].get("admin_name", "Sin_tecnico")

    return "Sin_tecnico"


def get_task_title(task: dict, task_id: int):
    return (
        task.get("title")
        or task.get("name")
        or task.get("subject")
        or f"Tarea_{task_id}"
    )


def format_task_file(task: dict, comments: list):
    task_id = task.get("id")
    title = get_task_title(task, task_id)
    technician = get_technician_name(task, comments)

    customer = (
        task.get("customer_name")
        or (task.get("customer") or {}).get("name", "")
        if isinstance(task.get("customer"), dict)
        else ""
    )

    lines = []
    lines.append(f"Orden de servicio / Task: {title} (ID: {task_id})")
    lines.append(f"Técnico: {technician}")
    if customer:
        lines.append(f"Cliente: {customer}")
    lines.append("")

    if not comments:
        lines.append("Sin comentarios.")
    else:
        lines.append("Comentarios del día:")
        lines.append("-----------")
        comments = sorted(comments, key=lambda x: x["created_at"])
        for c in comments:
            lines.append(f"[{c['created_at']}] {c.get('admin_name', '')}:")
            lines.append(c.get("comment", ""))
            lines.append("-" * 40)

    return "\n".join(lines)


def build_output_path(target_date, technician: str, title: str):
    date_folder = BASE_DIR / target_date.strftime("%Y-%m-%d")
    tech_folder = date_folder / sanitize_filename(technician)
    tech_folder.mkdir(parents=True, exist_ok=True)

    filename = sanitize_filename(title) + ".txt"
    return tech_folder / filename


# ==========================
# MAIN
# ==========================

def main():
    # ESTE ARCHIVO SIEMPRE USA AYER
    target_date = get_yesterday_date()
    print(f"Obteniendo comentarios del día: {target_date} (modo: ayer)")

    comments = get_comments_for_date(target_date)
    print(f"Comentarios encontrados (por fecha de comentario): {len(comments)}")

    if not comments:
        print("No hay comentarios.")
        return

    # Agrupación por task_id
    comments_by_task = {}
    for c in comments:
        comments_by_task.setdefault(c["task_id"], []).append(c)

    print(f"Tasks con comentarios en esa fecha: {len(comments_by_task)}")

    processed = 0
    skipped_not_closed = 0

    for task_id, task_comments in comments_by_task.items():
        try:
            task = get_task(task_id)
        except Exception as e:
            print(f"Error obteniendo task {task_id}: {e}")
            continue

        # FILTRO: solo tasks cerradas (closed == "1")
        closed_flag = str(task.get("closed", "0"))
        if closed_flag != "1":
            skipped_not_closed += 1
            continue

        title = get_task_title(task, task_id)
        technician = get_technician_name(task, task_comments)

        output_path = build_output_path(target_date, technician, title)
        content = format_task_file(task, task_comments)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Guardado en: {output_path}")
        processed += 1

    print(f"\nResumen:")
    print(f"  Tasks procesadas (cerradas): {processed}")
    print(f"  Tasks con comentarios en la fecha pero NO cerradas: {skipped_not_closed}")


if __name__ == "__main__":
    main()
