import json
import os

# JSON files /data/ directory
DATA_DIR      = os.path.join(os.path.dirname(__file__), "..", "data")
CLIENTS_FILE  = os.path.join(DATA_DIR, "clients.json")
PROJECTS_FILE = os.path.join(DATA_DIR, "projects.json")
INVOICES_FILE = os.path.join(DATA_DIR, "invoices.json")


def _ensure_data_dir():
    """ensure the data directory exists"""
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_json(filepath):
    """
    load data from a JSON file, 
    if the file does not exist or is empty, return an empty list
    """
    try:
        if not os.path.exists(filepath):
            return []          # first time loading the file
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content: 
                return []
            return json.loads(content)
    except Exception as e:
        print(f"  [!] Failed to load file: {e}")
        return []


def _save_json(filepath, data):
    """
    save data to a JSON file,
    indent=4 for human-readable format
    """
    try:
        _ensure_data_dir()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"  [!] Failed to save data: {e}")


# ------------- Clients -------------

def load_clients():
    """load Client objects from clients.json"""
    from models.client import Client
    raw = _load_json(CLIENTS_FILE)
    return [Client.from_dict(c) for c in raw]


def save_clients(clients):
    """save Client objects to clients.json"""
    _save_json(CLIENTS_FILE, [c.to_dict() for c in clients])


# ---- pprojects -----------------

def load_projects():
    """load Project objects from projects.json"""
    from models.project import Project
    raw = _load_json(PROJECTS_FILE)
    return [Project.from_dict(p) for p in raw]


def save_projects(projects):
    """save Project objects to projects.json"""
    _save_json(PROJECTS_FILE, [p.to_dict() for p in projects])


# --------- invoices -------------

def load_invoices():
    """load Invoice objects from invoices.json"""
    from models.invoice import Invoice
    raw = _load_json(INVOICES_FILE)
    return [Invoice.from_dict(i) for i in raw]


def save_invoices(invoices):
    """save invoice objects to invoices.json"""
    _save_json(INVOICES_FILE, [i.to_dict() for i in invoices])


# ---------- Helper: Generate next ID -----

def next_id(prefix, existing_ids):
    """
    generate a new unique ID.
    Example:C001, C002..., P001,
    """
    numbers = []
    for eid in existing_ids:
        try:
            numbers.append(int(eid[len(prefix):]))  # remove the prefix and convert to int
        except:
            pass
    next_num = max(numbers, default=0) + 1
    return f"{prefix}{next_num:03d}"   # prefix + 3 digit number
