# ================================================================
# utils/file_handler.py
# JSON files mein data save aur load karne ka kaam yahan hota hai
# Startup par load, har change par save
# ================================================================

import json
import os

# JSON files ka path — data/ folder mein hain
DATA_DIR      = os.path.join(os.path.dirname(__file__), "..", "data")
CLIENTS_FILE  = os.path.join(DATA_DIR, "clients.json")
PROJECTS_FILE = os.path.join(DATA_DIR, "projects.json")
INVOICES_FILE = os.path.join(DATA_DIR, "invoices.json")


def _ensure_data_dir():
    """Data folder exist nahi karta toh bana do"""
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_json(filepath):
    """
    JSON file se data load karo.
    File nahi hai ya empty hai toh khali list return karo.
    """
    try:
        if not os.path.exists(filepath):
            return []          # pehli baar chala raha hai — file nahi hai
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:    # file hai lekin khali hai
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        # JSON corrupt hai — khali list se shuru karo
        print(f"  [Warning] {filepath} ka data corrupt tha. Fresh start ho raha hai.")
        return []
    except Exception as e:
        print(f"  [Error] File load nahi hui: {e}")
        return []


def _save_json(filepath, data):
    """
    Data ko JSON file mein save karo.
    indent=4 se human-readable format mein save hota hai.
    """
    try:
        _ensure_data_dir()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"  [Error] Data save nahi hua: {e}")


# ── Clients ──────────────────────────────────────────────────────

def load_clients():
    """clients.json se Client objects ki list load karo"""
    from models.client import Client
    raw = _load_json(CLIENTS_FILE)
    return [Client.from_dict(c) for c in raw]


def save_clients(clients):
    """Client objects ki list ko clients.json mein save karo"""
    _save_json(CLIENTS_FILE, [c.to_dict() for c in clients])


# ── Projects ─────────────────────────────────────────────────────

def load_projects():
    """projects.json se Project objects ki list load karo"""
    from models.project import Project
    raw = _load_json(PROJECTS_FILE)
    return [Project.from_dict(p) for p in raw]


def save_projects(projects):
    """Project objects ki list ko projects.json mein save karo"""
    _save_json(PROJECTS_FILE, [p.to_dict() for p in projects])


# ── Invoices ─────────────────────────────────────────────────────

def load_invoices():
    """invoices.json se Invoice objects ki list load karo"""
    from models.invoice import Invoice
    raw = _load_json(INVOICES_FILE)
    return [Invoice.from_dict(i) for i in raw]


def save_invoices(invoices):
    """Invoice objects ki list ko invoices.json mein save karo"""
    _save_json(INVOICES_FILE, [i.to_dict() for i in invoices])


# ── Helper: Agle ID generate karo ────────────────────────────────

def next_id(prefix, existing_ids):
    """
    Naya unique ID generate karo.
    Jaise: C001, C002... ya P001, P002...
    """
    numbers = []
    for eid in existing_ids:
        try:
            numbers.append(int(eid[len(prefix):]))  # prefix hata ke number lo
        except:
            pass
    next_num = max(numbers, default=0) + 1
    return f"{prefix}{next_num:03d}"   # zero-padded 3 digit number
