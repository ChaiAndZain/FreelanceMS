import sys
import os

# add project folder path to imports
sys.path.insert(0, os.path.dirname(__file__))

from models          import Client, Project, Invoice, InvoiceItem
from models.project  import STATUS_OPTIONS
from models.invoice  import INVOICE_STATUS
from utils           import (load_clients,  save_clients,
                              load_projects, save_projects,
                              load_invoices, save_invoices,
                              next_id, calculate_summary,
                              print_financial_summary,
                              generate_all_charts,
                              send_invoice_email,
                              get_usd_to_pkr_rate)
from utils.visualizer import (chart_monthly_earnings,
                               chart_project_status,
                               chart_client_earnings)
from datetime import datetime


# ================================================================
# ---------------------------HELPER FUNCTIONS --------------------
# ================================================================

def clear():
    """clear the screen"""
    os.system("cls" if os.name == "nt" else "clear")


def header(title):
    """prints heading of each section"""
    print("\n" + "═"*55)
    print(f"  {title}")
    print("═"*55)


def pause():
    """waits for Enter key to press"""
    input("\n  [Press Enter to contine...]")


def get_input(prompt, required=True, input_type=str, min_val=None, max_val=None):
    """
    get user input with validation
    - required: if True, the input is required
    - input_type: type of the input
    - min_val / max_val: minimum and maximum values
    """
    while True:
        try:
            value = input(f"  {prompt}: ").strip()

            # if required is True and the input is empty, print error message and continue
            if required and not value:
                print("  [!] This field is required.")
                continue

            # Type conversion
            if value:
                value = input_type(value)

            # Range check
            if min_val is not None and value < min_val:
                print(f"  [!] Value should be greater than {min_val}.")
                continue
            if max_val is not None and value > max_val:
                print(f"  [!] Value should be less than {max_val}.")
                continue

            return value

        except ValueError:
            print(f"  [!] Invalid format. {input_type.__name__} is required.")


def get_date_input(prompt):
    """get date in YYYY-MM-DD format"""
    while True:
        date_str = input(f"  {prompt} (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(date_str, "%Y-%m-%d") # validate date format
            return date_str
        except:
            print("  [!] Invalid date format. Example: 2026-06-30")


def choose_from_list(options, prompt="Select an option"):
    """select an option from a numbered list"""
    for i, opt in enumerate(options, 1):
        print(f"    {i}. {opt}")
    while True:
        try:
            choice = int(input(f"  {prompt} (1-{len(options)}): "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            print(f"  [!] Invalid option. Select a number between 1 and {len(options)}.")
        except:
            print("  [!] Invalid input. Please enter a valid number.")


# ================================================================
# ---------- Client Management --------
# ================================================================

def menu_clients(clients):
    """client management sub-menu"""
    while True:
        header("CLIENT MANAGEMENT")
        print("  1. View all clients")
        print("  2. Add a new client")
        print("  3. Update a client")
        print("  4. Delete a client")
        print("  0. Return to main menu")

        choice = input("\n  Select an option: ").strip()

        if   choice == "1": view_clients(clients)
        elif choice == "2": add_client(clients)
        elif choice == "3": update_client(clients)
        elif choice == "4": delete_client(clients)
        elif choice == "0": break
        else: print("  [!] Invalid option.")


def view_clients(clients):
    """view all clients"""
    header("CLIENTS LIST")
    if not clients:
        print("  No clients found.")
    else:
        for c in clients:
            print(f"\n{c}")
            print("  " + "-"*45)
    pause()


def add_client(clients):
    """add a new client"""
    header("ADD NEW CLIENT")
    try:
        name   = get_input("Name")
        email  = get_input("Email")
        phone  = get_input("Phone")
        company = get_input("Company (optional)", required=False)
        print("  Payment Terms:")
        terms  = choose_from_list(["Net 15", "Net 30", "Net 60", "Immediate"])

        # generate a unique ID for the new client
        cid = next_id("C", [c.get_id() for c in clients])

        new_client = Client(cid, name, email, phone, company or "N/A", terms)
        clients.append(new_client)
        save_clients(clients)    # file mein save karo

        print(f"\n  ✔ Client '{name}' has been added! with ID: {cid}")
    except KeyboardInterrupt:
        print("\n  [!] Operation cancelled.")
    pause()

# --------- Update Client ----
def update_client(clients):
    """update an existing client"""
    header("UPDATE CLIENT")
    if not clients:
        print("  No clients found.")
        pause()
        return

    # search for clientby ID
    cid = input("  Enter Client ID (e.g. C001): ").strip().upper()
    client = next((c for c in clients if c.get_id() == cid), None)

    if not client:
        print(f"  [!] Client with ID '{cid}' not found.")
        pause()
        return

    print(f"\n  Current info:\n{client}")
    print("\n  Leave blank if don't want to change.\n")

    try:
        name  = input(f"  Name [{client.get_name()}]: ").strip()
        email = input(f"  Email [{client.get_email()}]: ").strip()
        phone= input(f"  Phone [{client.get_phone()}]: ").strip()
        company = input(f"  Company [{client.get_company()}]: ").strip()

        # update only the fields that the user has provided
        if name: client.set_name(name)
        if email: client.set_email(email)
        if phone:client.set_phone(phone)
        if company: client.set_company(company)

        save_clients(clients)
        print("  ✔ client updated successfully!")
    except KeyboardInterrupt:
        print("\n  [!] Operation cancelled.")
    pause()


def delete_client(clients):
    """delete a client"""
    header("DELETE CLIENT")
    cid = input("  Enter Client ID to delete: ").strip().upper()
    client = next((c for c in clients if c.get_id() == cid), None)

    if not client:
        print(f"  [!] Client with ID '{cid}' not found.")
        pause()
        return

    # Confirm deletion
    confirm = input(f"  Do you want to delete '{client.get_name()}'? (yes/no): ").strip().lower()
    if confirm == "yes":
        clients.remove(client)
        save_clients(clients)
        print("  ✔ Client deleted successfully.")
    else:
        print("  Deletion cancelled.")
    pause()


# ================================================================
# --- Project Management --------
# ================================================================

def menu_projects(projects, clients):
    """project management sub-menu"""
    while True:
        header("PROJECT MANAGEMENT")
        print("  1. View all projects")
        print("  2. Add a new project")
        print("  3. Update a project")
        print("  4. Delete a project")
        print("  0. Return to main menu")

        choice = input("\n  Select an option: ").strip()

        if   choice == "1": view_projects(projects)
        elif choice == "2": add_project(projects, clients)
        elif choice == "3": update_project(projects)
        elif choice == "4": delete_project(projects)
        elif choice == "0": break
        else: print("  [!] Invalid option.")


def view_projects(projects):
    """view all projects"""
    header("PROJECTS LIST")
    if not projects:
        print("  No projects found.")
    else:
        for p in projects:
            print(f"\n{p}")
            print("  " + "-"*45)
    pause()


def add_project(projects, clients):
    """add a new project"""
    header("ADD NEW PROJECT")
    if not clients:
        print("  [!] Please add at least one client first.")
        pause()
        return

    try:
        title = get_input("Project Title")

        # select a client from the existing clients
        print("  Select a client:")
        for c in clients:
            print(f"    {c.get_id()} — {c.get_name()} ({c.get_company()})")
        cid = input("  Client ID: ").strip().upper()
        if not any(c.get_id() == cid for c in clients):
            print("  [!] Invalid client ID.")
            pause()
            return

        deadline     = get_date_input("Deadline")
        hourly_rate  = get_input("Hourly Rate (USD)", input_type=float, min_val=0.1)
        hours_worked = get_input("Hours Worked (0 if not started)", input_type=float, min_val=0)
        print("  Status:")
        status  = choose_from_list(STATUS_OPTIONS)
        description = get_input("Description (optional)", required=False)

        pid = next_id("P", [p.get_id() for p in projects])

        new_project = Project(pid, title, cid, deadline,
                              hourly_rate, hours_worked,
                              status, description or "")
        projects.append(new_project)
        save_projects(projects)

        print(f"\n  ✔ Project '{title}' has been added! with ID: {pid}")
        print(f"     Estimated Earnings: ${new_project.gross_earning():.2f}")
    except KeyboardInterrupt:
        print("\n  [!] Operation cancelled.")
    pause()


def update_project(projects):
    """update an existing project"""
    header("UPDATE PROJECT")
    if not projects:
        print("  No projects found.")
        pause()
        return

    pid = input("  Enter Project ID (e.g. P001): ").strip().upper()
    proj = next((p for p in projects if p.get_id() == pid), None)

    if not proj:
        print(f"  [!] Project with ID '{pid}' not found.")
        pause()
        return

    print(f"\n  Current info:\n{proj}\n")
    print("  Leave blank if don't want to change.\n")

    try:
        title = input(f"  Title [{proj.get_title()}]: ").strip()
        deadline = input(f"  Deadline [{proj.get_deadline()}]: ").strip()
        hours_str = input(f"  Hours Worked [{proj.get_hours_worked()}]: ").strip()
        rate_str  = input(f"  Hourly Rate [{proj.get_hourly_rate()}]: ").strip()

        print("  New status (Enter to keep same):")
        for i, s in enumerate(STATUS_OPTIONS, 1):
            print(f"    {i}. {s}")
        st_choice = input("  Status (number or leave blank): ").strip()

        if title:    proj.set_title(title)
        if deadline:
            try:
                datetime.strptime(deadline, "%Y-%m-%d")
                proj.set_deadline(deadline)
            except ValueError:
                print("  [!] Invalid date format.")
        if hours_str:
            try: proj.set_hours_worked(float(hours_str))
            except: print("  [!] Invalid hours value.")
        if rate_str:
            try: proj.set_hourly_rate(float(rate_str))
            except: print("  [!] Invalid rate value.")
        if st_choice:
            try:
                idx = int(st_choice) - 1
                if 0 <= idx < len(STATUS_OPTIONS):
                    proj.set_status(STATUS_OPTIONS[idx])
            except:
                pass

        save_projects(projects)
        print("  ✔ Project updated")
    except KeyboardInterrupt:
        print("\n  [!] Operation cancelled.")
    pause()


def delete_project(projects):
    """delete a project"""
    header("DELETE PROJECT")
    pid = input("  Enter Project ID to delete: ").strip().upper()
    proj = next((p for p in projects if p.get_id() == pid), None)

    if not proj:
        print(f"  [!] Project with ID '{pid}' not found.")
        pause()
        return

    confirm = input(f"  Do you want to delete '{proj.get_title()}'? (yes/no): ").strip().lower()
    if confirm == "yes":
        projects.remove(proj)
        save_projects(projects)
        print("  ✔ Project deleted successfully.")
    else:
        print("  Deletion cancelled.")
    pause()


# ================================================================
# ---------- Invoice Management ----------------------
# ================================================================

def menu_invoices(invoices, clients, projects):
    """invoice management sub-menu""" 
    while True:
        header("INVOICE MANAGEMENT")
        print("  1. View all invoices")
        print("  2. Add a new invoice")
        print("  3. Update invoice status")
        print("  4. Delete an invoice")
        print("  5. Email an invoice to the client")
        print("  0. Return to main menu")

        choice = input("\n  Select an option: ").strip()

        if   choice == "1": view_invoices(invoices)
        elif choice == "2": add_invoice(invoices, clients, projects)
        elif choice == "3": update_invoice_status(invoices)
        elif choice == "4": delete_invoice(invoices)
        elif choice == "5": email_invoice(invoices, clients)
        elif choice == "0": break
        else: print("  [!] Invalid option.")


def view_invoices(invoices):
    """view all invoices"""
    header("INVOICES LIST")
    if not invoices:
        print("  No invoices found.")
    else:
        for inv in invoices:
            print(inv)
    pause()


def add_invoice(invoices, clients, projects):
    """add a new invoice"""
    header("ADD NEW INVOICE")
    if not clients or not projects:
        print("  [!] Please add at least one client and one project first.")
        pause()
        return

    try:
        # select a client from the existing clients
        print("  Select a client:")
        for c in clients:
            print(f"    {c.get_id()} — {c.get_name()}")
        cid = input("  Client ID: ").strip().upper()
        if not any(c.get_id() == cid for c in clients):
            print("  [!] Invalid client ID.")
            pause()
            return

        print("\n  Select a project:")
        client_projs = [p for p in projects if p.get_client_id() == cid] # get all projects for the selected client
        if not client_projs:
            print(f"  [!] Client {cid} has no projects.")
            pause()
            return
        for p in client_projs:
            print(f"    {p.get_id()} — {p.get_title()} (${p.gross_earning():.2f})")
        pid = input("  Project ID: ").strip().upper()
        if not any(p.get_id() == pid for p in client_projs):
            print("  [!] Invalid project ID.")
            pause()
            return

        issue_date = get_date_input("Invoice Date")
        due_days = get_input("How many days for payment", input_type=int, min_val=1)
        notes  = get_input("Notes (optional)", required=False)

        # add line items to the invoice
        items = []
        print("\n  Add invoice items (leave description blank to stop):")
        while True:
            desc = input("    Item description (leave blank to stop): ").strip()
            if not desc:
                break
            qty   = get_input(f"    '{desc}' quantity or hours", input_type=float, min_val=0.1)
            price = get_input(f"    '{desc}' unit price (USD)", input_type=float, min_val=0.01)
            items.append(InvoiceItem(desc, qty, price))

        if not items:
            print("  [!] At least one item is required.")
            pause()
            return

        # select the currency for the invoice
        print("\n  Invoice currency chunein:")
        currency = choose_from_list(["USD", "PKR"])
        fx_rate = 1.0
        if currency == "PKR":
            print("  Fetching live USD→PKR rate...")
            rate = get_usd_to_pkr_rate()
            if rate is None:
                # Network fail — ask user to enter manual rate
                print("  Online rate not found.")
                manual = input("  Enter manual rate (1 USD = Rs. ?), "
                               "or leave blank to revert to USD: ").strip()
                if manual:
                    try:
                        rate = float(manual)
                    except ValueError:
                        print("  [!] Invalid rate.")
                        currency = "USD"
                else:
                    currency = "USD"
            if currency == "PKR":
                fx_rate = float(rate)
                print(f"  ✔ Rate lock: 1 USD = Rs. {fx_rate:.2f}")

        inv_id = next_id("INV", [i.get_id() for i in invoices])
        new_inv = Invoice(inv_id, cid, pid, issue_date, due_days,
                          items, "Unpaid", notes or "",
                          currency, fx_rate)
        invoices.append(new_inv)
        save_invoices(invoices)

        print(new_inv)   # naya invoice print karo
        print(f"\n  ✔ Invoice {inv_id} has been added!")
    except KeyboardInterrupt:
        print("\n  [!] Operation cancelled.")
    pause()


def update_invoice_status(invoices):
    """update the payment status of an invoice"""
    header("UPDATE INVOICE STATUS")
    inv_id = input("  Enter Invoice ID to update: ").strip().upper()
    inv = next((i for i in invoices if i.get_id() == inv_id), None)

    if not inv:
        print(f"  [!] Invoice with ID '{inv_id}' not found.")
        pause()
        return

    print(f"  Current Status: {inv.get_status()}")
    print("  Select a new status:")
    new_status = choose_from_list(INVOICE_STATUS)
    inv.set_status(new_status)
    save_invoices(invoices)
    print(f"  ✔ Invoice status '{new_status}' has been updated")
    pause()


def email_invoice(invoices, clients):
    """send an invoice email to the client"""
    header("EMAIL INVOICE")
    if not invoices:
        print("  No invoices found.")
        pause()
        return

    inv_id = input("  Enter Invoice ID to email: ").strip().upper()
    inv = next((i for i in invoices if i.get_id() == inv_id), None)
    if not inv:
        print(f"  [!] Invoice with ID '{inv_id}' not found.")
        pause()
        return

    client = next((c for c in clients if c.get_id() == inv.get_client_id()), None)
    if not client:
        print(f"  [!] Client with ID '{inv.get_client_id()}' not found.")
        pause()
        return

    print(f"\n  Invoice  : {inv.get_id()}  (Total: ${inv.grand_total():.2f})")
    print(f"  Client   : {client.get_name()}")
    print(f"  Email  : {client.get_email()}")
    confirm = input("\n  Confirm email sending? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("  Email sending cancelled.")
        pause()
        return

    print("  Sending email... ")
    success, message = send_invoice_email(inv, client)
    if success:
        print(f"  ✔ {message}")
    else:
        print(f"  [!] {message}")
    pause()


def delete_invoice(invoices):
    """delete an invoice"""
    header("DELETE INVOICE")
    inv_id = input("  Enter Invoice ID to delete: ").strip().upper()
    inv = next((i for i in invoices if i.get_id() == inv_id), None)

    if not inv:
        print(f"  [!] Invoice with ID '{inv_id}' not found.")
        pause()
        return

    confirm = input(f"  Do you want to delete Invoice '{inv_id}'? (yes/no): ").strip().lower()
    if confirm == "yes":
        invoices.remove(inv)
        save_invoices(invoices)
        print("  ✔ Invoice deleted successfully.")
    else:
        print("  Deletion cancelled.")
    pause()


# ================================================================
# REPORTS & CHARTS
# ================================================================

def menu_reports(projects, clients, invoices):
    """reports and charts sub-menu"""
    while True:
        header("REPORTS & ANALYTICS")
        print("  1. Financial Summary")
        print("  2. Monthly Earnings Report")
        print("  3. Client-wise Earnings Report")
        print("  4. Generate all charts (PNG files)")
        print("  0. Return to main menu")

        choice = input("\n  Select an option: ").strip()

        if choice == "1":
            header("FINANCIAL SUMMARY REPORT")
            summary = calculate_summary(projects, invoices)
            print_financial_summary(summary)
            pause()

        elif choice == "2":
            header("MONTHLY EARNINGS REPORT")
            from utils.finance import monthly_earnings_report
            df = monthly_earnings_report(projects)
            if df.empty:
                print("  No completed projects found.")
            else:
                print(f"\n  {'Month':<12} {'Earnings':>12}")
                print("  " + "-"*26)
                for _, row in df.iterrows():
                    print(f"  {row['Month']:<12} ${row['Earnings']:>10.2f}")
                print("  " + "-"*26)
                print(f"  {'TOTAL':<12} ${df['Earnings'].sum():>10.2f}")
            pause()

        elif choice == "3":
            header("CLIENT-WISE EARNINGS")
            from utils.finance import client_earnings_report
            df = client_earnings_report(projects, clients)
            if df.empty:
                print("  No completed projects found.")
            else:
                print(f"\n  {'Client':<20} {'Total Earnings':>12}")
                print("  " + "-"*34)
                for _, row in df.iterrows():
                    print(f"  {row['Client']:<20} ${row['Earnings']:>10.2f}")
            pause()

        elif choice == "4":
            generate_all_charts(projects, clients)
            pause()

        elif choice == "0":
            break
        else:
            print("  [!] Invalid option.")


# ================================================================
# MAIN MENAGEMENT SYSTEM
# ================================================================

def main_menu():
    """
    main entry point
    load data on startup, then enter the main menu loop
    """
    # ── Startup: load data from JSON files ────────────────────
    print("\n  Freelance Management System starting...")
    clients  = load_clients()
    projects = load_projects()
    invoices = load_invoices()
    print(f"  ✔ Data load ho gaya | "
          f"{len(clients)} clients, {len(projects)} projects, "
          f"{len(invoices)} invoices")

    # ── Main Loop ────────────────────────────────────────────────
    while True:
        clear()
        print("\n" + "═"*55)
        print("    FREELANCE MANAGEMENT SYSTEM")
        print("    Python Semester Project")
        print("═"*55)
        print("\n  MAIN MENU:\n")
        print("  1.  Clients        — Manage clients") 
        print("  2.  Projects       — Manage projects")
        print("  3.  Invoices       — Manage invoices")
        print("  4.  Reports        — Financial reports and charts")
        print("  0.  Exit           — Exit the program")
        print()

        choice = input("  Select an option: ").strip()

        if   choice == "1": menu_clients(clients)
        elif choice == "2": menu_projects(projects, clients)
        elif choice == "3": menu_invoices(invoices, clients, projects)
        elif choice == "4": menu_reports(projects, clients, invoices)
        elif choice == "0":
            print("\n  Thank you for using the Freelance Management System.")
            print("  Your data has been saved.\n")
            break
        else:
            print("  [!] Invalid option. Select a number between 0 and 4.")
            pause()


# ================================================================
# Program yahan se shuru hota hai
# ================================================================
if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        # Ctrl+C pressed — gracefully exit
        print("\n\n  Program is exiting... Thank you for using the Freelance Management System.")
        sys.exit(0)
