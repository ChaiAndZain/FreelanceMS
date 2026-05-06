# Freelance Management System
**Python Programming — Semester Project**

---

## Project Overview
Ek CLI-based tool jo ek freelancer ko apne clients, projects, invoices,
aur earnings ek jagah track karne deta hai. Data JSON files mein save hota hai.
Invoices ko seedha client ke email address pe SMTP ke zariye bhi bheja ja sakta hai.

---

## Setup & Installation

### 1. Requirements Install Karein
```bash
pip install -r requirements.txt
```

### 2. Email Credentials Configure Karein (optional, sirf email feature ke liye)
Project root mein `.env` file pehle se di gayi hai (template ke saath).
Apni asli SMTP credentials usme bhar dein:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USER=your.email@gmail.com
SMTP_PASSWORD=your-app-password-here
SMTP_FROM_NAME=Your Name
SMTP_FROM_EMAIL=your.email@gmail.com
```

> **Gmail walon ke liye nota:** regular Gmail password kaam nahi karega.
> Aap ko ek **App Password** banana hoga:
> https://myaccount.google.com/apppasswords
> (2-Step Verification on hona zaroori hai.)

> **Important:** `.env` file `.gitignore` mein hai — kabhi public repo mein
> commit mat karein. Sharing ke liye `.env.example` template use karein.

### 3. Program Chalayein
```bash
cd freelance_system
python main.py
```

---

## Project Structure
```
freelance_system/
├── main.py              ← Program yahan se shuru hota hai (CLI menu)
├── requirements.txt     ← Python dependencies
├── .env                 ← SMTP credentials (private, gitignored)
├── .env.example         ← .env ka shareable template
├── .gitignore
├── models/
│   ├── client.py        ← Client class
│   ├── project.py       ← Project class
│   └── invoice.py       ← Invoice + InvoiceItem classes
├── utils/
│   ├── file_handler.py  ← JSON save/load
│   ├── finance.py       ← Financial calculations (Pandas, USD)
│   ├── visualizer.py    ← Matplotlib charts (USD)
│   ├── emailer.py       ← SMTP email bhejne ka logic
│   └── currency.py      ← USD→PKR live rate (forex.pk scraper)
├── data/
│   ├── clients.json
│   ├── projects.json
│   └── invoices.json
├── reports/             ← Generated PNG charts
└── README.md
```

---

## Features
- **Clients:** Add, View, Update, Delete
- **Projects:** Add, View, Update, Delete (status tracking + overdue detection)
- **Invoices:** Create with line items, status update (Paid/Unpaid), delete,
  aur **client ke email address pe SMTP se bhejo**
- **Multi-Currency Invoices:** Har invoice ke liye USD ya **PKR** chunein.
  PKR ke liye live rate forex.pk se fetch hoti hai aur invoice ke saath
  snapshot ho jaati hai. **Internal data, reports aur charts hamesha USD
  mein hote hain** — sirf invoice ka display/email currency-aware hai.
- **Financial Reports:** Gross earnings, tax estimate, net income, profit margin (USD)
- **Charts:** Monthly earnings bar chart, project status pie chart, client earnings chart (USD)
- **Data Persistence:** Sab data JSON files mein automatically save hota hai
- **Secure Credentials:** SMTP login `.env` file mein, code se alag

---

## Invoice Email Bhejne Ka Tarika
1. Main Menu → `3. Invoices`
2. Phir → `5. Invoice Email Bhejo`
3. Invoice ID daalein (e.g. `INV001`)
4. System automatically client ka email lookup karke confirmation maangega
5. `haan` likhein — invoice plain-text email ke roop mein bhej di jayegi

Agar credentials missing hon ya SMTP login fail ho jaye, user-friendly
error message dikhayi degi (password aur sensitive details print nahi hoti).

---

## Multi-Currency Invoices (USD / PKR)
1. Invoice banate waqt items add karne ke baad system **Currency** poochega
2. **USD** chunein → standard invoice ban jayegi
3. **PKR** chunein → system live USD→PKR rate forex.pk se fetch karega:
   - Network problem ho toh manually rate enter kar sakte hain
   - Rate invoice ke saath **snapshot** ho jaati hai (JSON mein `fx_rate`)
   - Future views aur emails wahi locked rate use karte hain — taake
     amount kabhi mismatch na ho

> **Important:** Invoice ki line items aur amounts JSON mein hamesha
> USD mein store hoti hain. PKR sirf display + email render ke liye hai.
> Iska matlab: charts, financial summary, monthly/client earnings reports
> hamesha USD mein consistent rahti hain — chahe individual invoices PKR
> mein bheji gayi hon.

---

## Dependencies
- Python 3.7+
- `pandas` — report generation
- `matplotlib` — chart generation
- `python-dotenv` — `.env` file se credentials load karna
- `requests` + `beautifulsoup4` — live USD→PKR rate fetch karna
