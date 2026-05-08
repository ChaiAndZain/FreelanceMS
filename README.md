# Freelance Management System

CLI-based tool that helps a freelancer track clients, projects, invoices, and earnings in one place. Data is saved in JSON files, and invoices can be emailed directly to clients via SMTP in multiple currencies.

## Features

- **Clients:** Add, view, update, delete
- **Projects:** Add, view, update, delete (with status tracking and overdue detection)
- **Invoices:** Create with line items, mark as Paid/Unpaid, delete, and send via SMTP email
- **Multi-Currency Invoices:** Choose USD or PKR per invoice. PKR rates are fetched live from forex.pk and snapshotted with the invoice. Internal data, reports, and charts always stay in USD.
- **Financial Reports:** Gross earnings, tax estimate, net income, profit margin (USD)
- **Charts:** Monthly earnings, project status, and client earnings (USD)
- **Data Persistence:** All data is automatically saved to JSON files

## Requirements

- Python 3.7+
- Dependencies: `pandas`, `matplotlib`, `python-dotenv`, `requests`, `beautifulsoup4`

## How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure email credentials (optional, only for sending invoices)

Copy `.env.example` to `.env` and fill in your SMTP credentials:

```
SMTP_USER=your.email@gmail.com
SMTP_PASSWORD=your-app-password-here
SMTP_FROM_NAME=Your Name
SMTP_FROM_EMAIL=your.email@gmail.com
```

> **Note for Gmail users:** A regular Gmail password will not work. You must create an [App Password](https://myaccount.google.com/apppasswords) (2-Step Verification must be enabled).

> The `.env` file is gitignored — never commit it to a public repo. Use `.env.example` as a shareable template.

### 3. Run the program

```bash
python main.py
```

## Project Structure

```
freelance_system/
├── main.py              # Entry point (CLI menu)
├── requirements.txt     # Python dependencies
├── .env                 # SMTP credentials (private, gitignored)
├── .env.example         # Shareable .env template
├── models/
│   ├── client.py        # Client class
│   ├── project.py       # Project class
│   └── invoice.py       # Invoice and InvoiceItem classes
├── utils/
│   ├── file_handler.py  # JSON save/load
│   ├── finance.py       # Financial calculations (USD)
│   ├── visualizer.py    # Matplotlib charts (USD)
│   ├── emailer.py       # SMTP email logic
│   └── currency.py      # Live USD→PKR rate (forex.pk)
├── data/                # JSON data files
└── reports/             # Generated PNG charts
```

## Sending an Invoice by Email

1. Main Menu → `3. Invoices`
2. Select `5. Send Invoice Email`
3. Enter the invoice ID (e.g. `INV001`)
4. The system looks up the client's email and asks for confirmation
5. Confirm to send the invoice as a plain-text email

If credentials are missing or SMTP login fails, a user-friendly error is shown (passwords and sensitive details are never printed).

## Multi-Currency Invoices (USD / PKR)

1. After adding line items, the system asks for the invoice currency
2. **USD** — creates a standard invoice
3. **PKR** — fetches the live USD→PKR rate from forex.pk:
   - If the network fails, you can enter the rate manually
   - The rate is snapshotted with the invoice (`fx_rate` in JSON) so the displayed amount never drifts

> Line items and amounts are always stored in USD. PKR is only used for display and email rendering, so charts and financial reports stay consistent regardless of which currency individual invoices were sent in.
