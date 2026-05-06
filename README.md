# Freelance Management System
**Python Programming — Semester Project**

---

## Project Overview
Ek CLI-based tool jo ek freelancer ko apne clients, projects, invoices,
aur earnings ek jagah track karne deta hai. Data JSON files mein save hota hai.

---

## Setup & Installation

### 1. Requirements Install Karein
```bash
pip install pandas matplotlib
```

### 2. Program Chalayein
```bash
cd freelance_system
python main.py
```

---

## Project Structure
```
freelance_system/
├── main.py              ← Program yahan se shuru hota hai (CLI menu)
├── models/
│   ├── client.py        ← Client class
│   ├── project.py       ← Project class
│   └── invoice.py       ← Invoice + InvoiceItem classes
├── utils/
│   ├── file_handler.py  ← JSON save/load
│   ├── finance.py       ← Financial calculations (Pandas)
│   └── visualizer.py    ← Matplotlib charts
├── data/
│   ├── clients.json     ← Clients ka data
│   ├── projects.json    ← Projects ka data
│   └── invoices.json    ← Invoices ka data
├── reports/             ← Generated PNG charts yahan save honge
└── README.md
```

---

## Features
- **Clients:** Add, View, Update, Delete
- **Projects:** Add, View, Update, Delete (status tracking + overdue detection)
- **Invoices:** Create with line items, status update (Paid/Unpaid), delete
- **Financial Reports:** Gross earnings, tax estimate, net income, profit margin
- **Charts:** Monthly earnings bar chart, project status pie chart, client earnings chart
- **Data Persistence:** Sab data JSON files mein automatically save hota hai

---

## Dependencies
- Python 3.7+
- `pandas` — report generation
- `matplotlib` — chart generation
