from pathlib import Path
from datetime import datetime
import base64
import requests
import re
from collections import defaultdict

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
# DETECCIÓN ESCRITORIO
# ==========================

home = Path.home()
if (home / "Desktop").exists():
    DESKTOP = home / "Desktop"
elif (home / "Escritorio").exists():
    DESKTOP = home / "Escritorio"
else:
    DESKTOP = home

BASE_DIR = DESKTOP / "Splynx_Tecnicos_Calendar"
BASE_DIR.mkdir(exist_ok=True)

# ==========================
# CONFIG
# ==========================

DATE_FIELD = "scheduled_from"   # usamos la fecha de agenda (calendar)

# Mapeo de ID de usuario (assignee) -> nombre del técnico
TECH_NAMES = {
    23: "Antonio Marquez",
    24: "Andy Medina",
    26: "Emanuel Villalba",
    29: "Denis Corzo",
    32: "Rodrigo Sosa",
    39: "Fernando Recalde",
}

# False = solo tareas con técnico asignado (igual que Calendar filtrado por admin)
# True  = además crea grupo/carpeta "SIN_ASIGNAR"
INCLUIR_SIN_ASIGNAR = False


# ==========================
# HELPERS
# ==========================

def sanitize_filename(name: str) -> str:
    if not name:
        name = "sin_nombre"
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:120]


def get_json(url, params=None):
    resp = requests.get(url, headers=HEADERS, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["data"] if isinstance(data, dict) and "data" in data else data


def get_projects_map():
    url = f"{BASE_URL}/admin/scheduling/projects"
    projects = get_json(url)
    return {p["id"]: p.get("title", f"Proyecto_{p['id']}") for p in projects}


def get_locations_map():
    try:
        url = f"{BASE_URL}/admin/scheduling/locations"
        locations = get_json(url)
        return {loc["id"]: loc.get("name", f"location_{loc['id']}") for loc in locations}
    except Exception:
        return {}


def get_all_tasks():
    url = f"{BASE_URL}/admin/scheduling/tasks"
    return get_json(url)


def is_task_today(task: dict, today_str: str) -> bool:
    value = task.get(DATE_FIELD)
    if not value:
        return False
    return value[:10] == today_str


def is_task_closed(task: dict) -> bool:
    return str(task.get("closed", "0")) == "1"


def is_task_scheduled(task: dict) -> bool:
    # Solo las que realmente están en calendario
    return str(task.get("is_scheduled", "0")) == "1"


def build_tech_folder(tech_name: str) -> Path:
    folder_name = sanitize_filename(tech_name)
    folder = BASE_DIR / folder_name
    folder.mkdir(parents=True, exist_ok=True)
    return folder


# ==========================
# MAIN
# ==========================

def main():
    today_str = datetime.now().date().strftime("%Y-%m-%d")
    print(f"Generando resumen por técnico (CALENDAR) para el día: {today_str}")
    print(f"Carpeta base: {BASE_DIR}")

    projects_map = get_projects_map()
    locations_map = get_locations_map()
    tasks = get_all_tasks()
    print(f"Tareas totales recibidas: {len(tasks)}")

    # tech_name -> {"pendientes": [tareas], "cerradas": [tareas]}
    tech_tasks = defaultdict(lambda: {"pendientes": [], "cerradas": []})

    for t in tasks:
        # 1) solo tareas del día
        if not is_task_today(t, today_str):
            continue

        # 2) solo tareas calendarizadas
        if not is_task_scheduled(t):
            continue

        # 3) manejo de técnico asignado / sin asignar
        assignee = t.get("assignee")
        if assignee is None:
            if not INCLUIR_SIN_ASIGNAR:
                # si no queremos mostrar las sin asignar, las salteamos
                continue
            tech_name = "SIN_ASIGNAR"
        else:
            tech_name = TECH_NAMES.get(assignee, f"user_id={assignee}")

        closed = is_task_closed(t)

        if closed:
            tech_tasks[tech_name]["cerradas"].append(t)
        else:
            tech_tasks[tech_name]["pendientes"].append(t)

    print(f"Técnicos (incluyendo SIN_ASIGNAR si aplica): {len(tech_tasks)}")

    # Generar archivo por técnico
    for tech_name, buckets in tech_tasks.items():
        tech_folder = build_tech_folder(tech_name)
        output_file = tech_folder / f"tareas_{today_str}.txt"

        pendientes = buckets["pendientes"]
        cerradas = buckets["cerradas"]

        total_pendientes = len(pendientes)
        total_cerradas = len(cerradas)

        lines = []
        lines.append(f"Técnico: {tech_name}")
        lines.append(f"Fecha: {today_str}")
        lines.append(f"Tareas pendientes (calendarizadas): {total_pendientes}")
        lines.append(f"Tareas cerradas   (calendarizadas): {total_cerradas}")
        lines.append("")
        lines.append("=" * 70)
        lines.append("PENDIENTES")
        lines.append("=" * 70)
        lines.append("")

        pendientes_sorted = sorted(
            pendientes,
            key=lambda x: ((x.get(DATE_FIELD) or ""), (x.get("title") or "").lower())
        )

        for t in pendientes_sorted:
            tid = t.get("id")
            title = t.get("title") or t.get("name") or f"Tarea {tid}"
            scheduled_from = t.get(DATE_FIELD) or ""
            project_id = t.get("project_id")
            location_id = t.get("location_id")
            address = t.get("address") or ""

            proyecto = projects_map.get(project_id, f"Proyecto_{project_id}")
            if location_id and location_id in locations_map:
                ubicacion = locations_map[location_id]
            elif address:
                ubicacion = address
            elif location_id:
                ubicacion = f"location_id={location_id}"
            else:
                ubicacion = "Sin ubicación"

            lines.append(f"- ID {tid}")
            if scheduled_from:
                lines.append(f"  Programada: {scheduled_from}")
            lines.append(f"  Proyecto:   {proyecto}")
            lines.append(f"  Ubicación:  {ubicacion}")
            lines.append(f"  Título:     {title}")
            lines.append("")

        lines.append("")
        lines.append("=" * 70)
        lines.append("CERRADAS")
        lines.append("=" * 70)
        lines.append("")

        cerradas_sorted = sorted(
            cerradas,
            key=lambda x: ((x.get(DATE_FIELD) or ""), (x.get("title") or "").lower())
        )

        for t in cerradas_sorted:
            tid = t.get("id")
            title = t.get("title") or t.get("name") or f"Tarea {tid}"
            scheduled_from = t.get(DATE_FIELD) or ""
            project_id = t.get("project_id")
            location_id = t.get("location_id")
            address = t.get("address") or ""

            proyecto = projects_map.get(project_id, f"Proyecto_{project_id}")
            if location_id and location_id in locations_map:
                ubicacion = locations_map[location_id]
            elif address:
                ubicacion = address
            elif location_id:
                ubicacion = f"location_id={location_id}"
            else:
                ubicacion = "Sin ubicación"

            lines.append(f"- ID {tid}")
            if scheduled_from:
                lines.append(f"  Programada: {scheduled_from}")
            lines.append(f"  Proyecto:   {proyecto}")
            lines.append(f"  Ubicación:  {ubicacion}")
            lines.append(f"  Título:     {title}")
            lines.append("")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"Generado: {output_file}")

    print("\nListo. Cada técnico tiene su archivo con PENDIENTES y CERRADAS de hoy según el CALENDAR.")


if __name__ == "__main__":
    main()
nt("\nListo. Cada técnico tiene su archivo con PENDIENTES y CERRADAS de hoy según el CALENDAR.")


if __name__ == "__main__":
    main()
