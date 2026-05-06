#!/usr/bin/env python3
# ================================================================
# main.py  —  Freelance Management System
# CS112 / Python Programming — Semester Project
#
# Ye program ek freelancer ke liye complete management system hai.
# CLI (Command Line Interface) based hai — numbered menus se chalta hai.
# Saara data JSON files mein save hota hai.
# ================================================================

import sys
import os

# Apna project folder path mein add karo taake imports kaam karein
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
                              send_invoice_email)
from utils.visualizer import (chart_monthly_earnings,
                               chart_project_status,
                               chart_client_earnings)
from datetime import datetime


# ================================================================
# HELPER FUNCTIONS — UI ke liye chhote reusable functions
# ================================================================

def clear():
    """Screen saaf karo (Windows aur Linux dono ke liye)"""
    os.system("cls" if os.name == "nt" else "clear")


def header(title):
    """Har section ka heading print karo"""
    print("\n" + "═"*55)
    print(f"  {title}")
    print("═"*55)


def pause():
    """User ko padhne ka waqt do — Enter dabane ka wait karo"""
    input("\n  [Enter dabayein jari rakhne ke liye...]")


def get_input(prompt, required=True, input_type=str, min_val=None, max_val=None):
    """
    Safe user input lene ka function.
    - required: khaali nahi ho sakta
    - input_type: int ya float ka validation
    - min_val / max_val: range check
    """
    while True:
        try:
            value = input(f"  {prompt}: ").strip()

            # Required field khaali hai?
            if required and not value:
                print("  [!] Ye field khaali nahi ho sakta.")
                continue

            # Type conversion
            if value:
                value = input_type(value)

            # Range check
            if min_val is not None and value < min_val:
                print(f"  [!] Value {min_val} se kam nahi ho sakti.")
                continue
            if max_val is not None and value > max_val:
                print(f"  [!] Value {max_val} se zyada nahi ho sakti.")
                continue

            return value

        except ValueError:
            print(f"  [!] Galat format. {input_type.__name__} chahiye.")


def get_date_input(prompt):
    """YYYY-MM-DD format mein date lo — validate karo"""
    while True:
        date_str = input(f"  {prompt} (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("  [!] Galat date format. Misaal: 2025-06-30")


def choose_from_list(options, prompt="Option chunein"):
    """Numbered list se ek option select karwao"""
    for i, opt in enumerate(options, 1):
        print(f"    {i}. {opt}")
    while True:
        try:
            choice = int(input(f"  {prompt} (1-{len(options)}): "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            print(f"  [!] 1 aur {len(options)} ke beech mein daalen.")
        except ValueError:
            print("  [!] Sirf number daalen.")


# ================================================================
# CLIENT MANAGEMENT — Add, View, Update, Delete
# ================================================================

def menu_clients(clients):
    """Client management ka sub-menu"""
    while True:
        header("CLIENT MANAGEMENT")
        print("  1. Saare Clients Dekhein")
        print("  2. Naya Client Add Karein")
        print("  3. Client Update Karein")
        print("  4. Client Delete Karein")
        print("  0. Wapas Main Menu")

        choice = input("\n  Option: ").strip()

        if   choice == "1": view_clients(clients)
        elif choice == "2": add_client(clients)
        elif choice == "3": update_client(clients)
        elif choice == "4": delete_client(clients)
        elif choice == "0": break
        else: print("  [!] Galat option.")


def view_clients(clients):
    """Saare clients ki list dikhao"""
    header("CLIENTS LIST")
    if not clients:
        print("  Koi client nahi hai abhi.")
    else:
        for c in clients:
            print(f"\n{c}")
            print("  " + "-"*45)
    pause()


def add_client(clients):
    """Naya client add karo"""
    header("NAYA CLIENT ADD KAREIN")
    try:
        name   = get_input("Naam")
        email  = get_input("Email")
        phone  = get_input("Phone")
        company = get_input("Company (khaali chhor sakte hain)", required=False)
        print("  Payment Terms chunein:")
        terms  = choose_from_list(["Net 15", "Net 30", "Net 60", "Immediate"])

        # Agle unique ID generate karo
        cid = next_id("C", [c.get_id() for c in clients])

        new_client = Client(cid, name, email, phone, company or "N/A", terms)
        clients.append(new_client)
        save_clients(clients)    # file mein save karo

        print(f"\n  ✔ Client '{name}' add ho gaya! ID: {cid}")
    except KeyboardInterrupt:
        print("\n  [!] Operation cancel kiya gaya.")
    pause()


def update_client(clients):
    """Existing client ki details update karo"""
    header("CLIENT UPDATE KAREIN")
    if not clients:
        print("  Koi client nahi hai.")
        pause()
        return

    # ID se client dhundho
    cid = input("  Client ID daalen (e.g. C001): ").strip().upper()
    client = next((c for c in clients if c.get_id() == cid), None)

    if not client:
        print(f"  [!] ID '{cid}' ka client nahi mila.")
        pause()
        return

    print(f"\n  Current info:\n{client}")
    print("\n  Khaali chhor dein agar change nahi karna.\n")

    try:
        name    = input(f"  Naam [{client.get_name()}]: ").strip()
        email   = input(f"  Email [{client.get_email()}]: ").strip()
        phone   = input(f"  Phone [{client.get_phone()}]: ").strip()
        company = input(f"  Company [{client.get_company()}]: ").strip()

        # Sirf woh fields update karo jo user ne likha
        if name:    client.set_name(name)
        if email:   client.set_email(email)
        if phone:   client.set_phone(phone)
        if company: client.set_company(company)

        save_clients(clients)
        print("  ✔ Client update ho gaya!")
    except KeyboardInterrupt:
        print("\n  [!] Operation cancel kiya gaya.")
    pause()


def delete_client(clients):
    """Client delete karo"""
    header("CLIENT DELETE KAREIN")
    cid = input("  Delete karne wale client ka ID: ").strip().upper()
    client = next((c for c in clients if c.get_id() == cid), None)

    if not client:
        print(f"  [!] ID '{cid}' ka client nahi mila.")
        pause()
        return

    # Confirm lena zaroori hai — galti se delete na ho
    confirm = input(f"  '{client.get_name()}' ko delete karna chahte hain? (haan/nahi): ").strip().lower()
    if confirm == "haan":
        clients.remove(client)
        save_clients(clients)
        print("  ✔ Client delete ho gaya.")
    else:
        print("  Delete cancel kiya gaya.")
    pause()


# ================================================================
# PROJECT MANAGEMENT — Add, View, Update, Delete
# ================================================================

def menu_projects(projects, clients):
    """Project management ka sub-menu"""
    while True:
        header("PROJECT MANAGEMENT")
        print("  1. Saare Projects Dekhein")
        print("  2. Naya Project Add Karein")
        print("  3. Project Update Karein")
        print("  4. Project Delete Karein")
        print("  0. Wapas Main Menu")

        choice = input("\n  Option: ").strip()

        if   choice == "1": view_projects(projects)
        elif choice == "2": add_project(projects, clients)
        elif choice == "3": update_project(projects)
        elif choice == "4": delete_project(projects)
        elif choice == "0": break
        else: print("  [!] Galat option.")


def view_projects(projects):
    """Saare projects ki list dikhao"""
    header("PROJECTS LIST")
    if not projects:
        print("  Koi project nahi hai abhi.")
    else:
        for p in projects:
            print(f"\n{p}")
            print("  " + "-"*45)
    pause()


def add_project(projects, clients):
    """Naya project add karo"""
    header("NAYA PROJECT ADD KAREIN")
    if not clients:
        print("  [!] Pehle ek client add karein.")
        pause()
        return

    try:
        title = get_input("Project ka Title")

        # Client ID select karwao existing clients mein se
        print("  Client chunein:")
        for c in clients:
            print(f"    {c.get_id()} — {c.get_name()} ({c.get_company()})")
        cid = input("  Client ID: ").strip().upper()
        if not any(c.get_id() == cid for c in clients):
            print("  [!] Galat Client ID.")
            pause()
            return

        deadline     = get_date_input("Deadline")
        hourly_rate  = get_input("Hourly Rate (USD)", input_type=float, min_val=0.1)
        hours_worked = get_input("Hours Worked (0 agar abhi shuru nahi)", input_type=float, min_val=0)
        print("  Status chunein:")
        status      = choose_from_list(STATUS_OPTIONS)
        description = get_input("Description (optional)", required=False)

        pid = next_id("P", [p.get_id() for p in projects])

        new_project = Project(pid, title, cid, deadline,
                              hourly_rate, hours_worked,
                              status, description or "")
        projects.append(new_project)
        save_projects(projects)

        print(f"\n  ✔ Project '{title}' add ho gaya! ID: {pid}")
        print(f"     Estimated Earnings: ${new_project.gross_earning():.2f}")
    except KeyboardInterrupt:
        print("\n  [!] Operation cancel kiya gaya.")
    pause()


def update_project(projects):
    """Existing project update karo"""
    header("PROJECT UPDATE KAREIN")
    if not projects:
        print("  Koi project nahi hai.")
        pause()
        return

    pid = input("  Project ID daalen (e.g. P001): ").strip().upper()
    proj = next((p for p in projects if p.get_id() == pid), None)

    if not proj:
        print(f"  [!] ID '{pid}' ka project nahi mila.")
        pause()
        return

    print(f"\n  Current info:\n{proj}\n")
    print("  Khaali chhor dein agar change nahi karna.\n")

    try:
        title = input(f"  Title [{proj.get_title()}]: ").strip()
        deadline = input(f"  Deadline [{proj.get_deadline()}]: ").strip()
        hours_str = input(f"  Hours Worked [{proj.get_hours_worked()}]: ").strip()
        rate_str  = input(f"  Hourly Rate [{proj.get_hourly_rate()}]: ").strip()

        print("  Naya status chunein (Enter dabayein agar same rakhna hai):")
        for i, s in enumerate(STATUS_OPTIONS, 1):
            print(f"    {i}. {s}")
        st_choice = input("  Status (number ya khaali): ").strip()

        if title:    proj.set_title(title)
        if deadline:
            try:
                datetime.strptime(deadline, "%Y-%m-%d")
                proj.set_deadline(deadline)
            except ValueError:
                print("  [!] Galat date format — status nahi badla.")
        if hours_str:
            try: proj.set_hours_worked(float(hours_str))
            except: print("  [!] Galat hours value.")
        if rate_str:
            try: proj.set_hourly_rate(float(rate_str))
            except: print("  [!] Galat rate value.")
        if st_choice:
            try:
                idx = int(st_choice) - 1
                if 0 <= idx < len(STATUS_OPTIONS):
                    proj.set_status(STATUS_OPTIONS[idx])
            except:
                pass

        save_projects(projects)
        print("  ✔ Project update ho gaya!")
    except KeyboardInterrupt:
        print("\n  [!] Operation cancel kiya gaya.")
    pause()


def delete_project(projects):
    """Project delete karo"""
    header("PROJECT DELETE KAREIN")
    pid = input("  Delete karne wale project ka ID: ").strip().upper()
    proj = next((p for p in projects if p.get_id() == pid), None)

    if not proj:
        print(f"  [!] ID '{pid}' ka project nahi mila.")
        pause()
        return

    confirm = input(f"  '{proj.get_title()}' ko delete karna chahte hain? (haan/nahi): ").strip().lower()
    if confirm == "haan":
        projects.remove(proj)
        save_projects(projects)
        print("  ✔ Project delete ho gaya.")
    else:
        print("  Delete cancel kiya gaya.")
    pause()


# ================================================================
# INVOICE MANAGEMENT — Add, View, Update, Delete
# ================================================================

def menu_invoices(invoices, clients, projects):
    """Invoice management ka sub-menu"""
    while True:
        header("INVOICE MANAGEMENT")
        print("  1. Saari Invoices Dekhein")
        print("  2. Naya Invoice Banayein")
        print("  3. Invoice Status Update Karein")
        print("  4. Invoice Delete Karein")
        print("  5. Invoice Email Bhejo (Client ko)")
        print("  0. Wapas Main Menu")

        choice = input("\n  Option: ").strip()

        if   choice == "1": view_invoices(invoices)
        elif choice == "2": add_invoice(invoices, clients, projects)
        elif choice == "3": update_invoice_status(invoices)
        elif choice == "4": delete_invoice(invoices)
        elif choice == "5": email_invoice(invoices, clients)
        elif choice == "0": break
        else: print("  [!] Galat option.")


def view_invoices(invoices):
    """Saari invoices dikhao"""
    header("INVOICES LIST")
    if not invoices:
        print("  Koi invoice nahi hai abhi.")
    else:
        for inv in invoices:
            print(inv)
    pause()


def add_invoice(invoices, clients, projects):
    """Naya invoice banao"""
    header("NAYA INVOICE BANAYEIN")
    if not clients or not projects:
        print("  [!] Pehle clients aur projects add karein.")
        pause()
        return

    try:
        # Client aur project select karo
        print("  Client chunein:")
        for c in clients:
            print(f"    {c.get_id()} — {c.get_name()}")
        cid = input("  Client ID: ").strip().upper()
        if not any(c.get_id() == cid for c in clients):
            print("  [!] Galat Client ID.")
            pause()
            return

        print("\n  Project chunein:")
        client_projs = [p for p in projects if p.get_client_id() == cid]
        if not client_projs:
            print(f"  [!] Client {cid} ka koi project nahi.")
            pause()
            return
        for p in client_projs:
            print(f"    {p.get_id()} — {p.get_title()} (${p.gross_earning():.2f})")
        pid = input("  Project ID: ").strip().upper()
        if not any(p.get_id() == pid for p in client_projs):
            print("  [!] Galat Project ID.")
            pause()
            return

        issue_date = get_date_input("Invoice ki Date")
        due_days   = get_input("Kitne din mein payment chahiye", input_type=int, min_val=1)
        notes      = get_input("Notes (optional)", required=False)

        # Line items add karo
        items = []
        print("\n  Invoice items add karein (khaali description pe rok jaega):")
        while True:
            desc = input("    Item description (khaali = stop): ").strip()
            if not desc:
                break
            qty   = get_input(f"    '{desc}' ki quantity/hours", input_type=float, min_val=0.1)
            price = get_input(f"    '{desc}' ka unit price (USD)", input_type=float, min_val=0.01)
            items.append(InvoiceItem(desc, qty, price))

        if not items:
            print("  [!] Kam az kam ek item zaroori hai.")
            pause()
            return

        inv_id = next_id("INV", [i.get_id() for i in invoices])
        new_inv = Invoice(inv_id, cid, pid, issue_date, due_days,
                          items, "Unpaid", notes or "")
        invoices.append(new_inv)
        save_invoices(invoices)

        print(new_inv)   # naya invoice print karo
        print(f"\n  ✔ Invoice {inv_id} create ho gayi!")
    except KeyboardInterrupt:
        print("\n  [!] Operation cancel kiya gaya.")
    pause()


def update_invoice_status(invoices):
    """Invoice ka payment status update karo"""
    header("INVOICE STATUS UPDATE KAREIN")
    inv_id = input("  Invoice ID daalen (e.g. INV001): ").strip().upper()
    inv = next((i for i in invoices if i.get_id() == inv_id), None)

    if not inv:
        print(f"  [!] ID '{inv_id}' ki invoice nahi mili.")
        pause()
        return

    print(f"  Current Status: {inv.get_status()}")
    print("  Naya status chunein:")
    new_status = choose_from_list(INVOICE_STATUS)
    inv.set_status(new_status)
    save_invoices(invoices)
    print(f"  ✔ Invoice status '{new_status}' ho gaya!")
    pause()


def email_invoice(invoices, clients):
    """Invoice ko client ke email pe bhejo (SMTP via .env credentials)"""
    header("INVOICE EMAIL BHEJEIN")
    if not invoices:
        print("  Koi invoice nahi hai abhi.")
        pause()
        return

    inv_id = input("  Email karne wali Invoice ka ID (e.g. INV001): ").strip().upper()
    inv = next((i for i in invoices if i.get_id() == inv_id), None)
    if not inv:
        print(f"  [!] ID '{inv_id}' ki invoice nahi mili.")
        pause()
        return

    client = next((c for c in clients if c.get_id() == inv.get_client_id()), None)
    if not client:
        print(f"  [!] Is invoice ka client ({inv.get_client_id()}) record mein nahi mila.")
        pause()
        return

    print(f"\n  Invoice  : {inv.get_id()}  (Total: ${inv.grand_total():.2f})")
    print(f"  Client   : {client.get_name()}")
    print(f"  Email pe : {client.get_email()}")
    confirm = input("\n  Email bhejna confirm karein? (haan/nahi): ").strip().lower()
    if confirm != "haan":
        print("  Email cancel kiya gaya.")
        pause()
        return

    print("  Email bheji ja rahi hai... (rukein)")
    success, message = send_invoice_email(inv, client)
    if success:
        print(f"  ✔ {message}")
    else:
        print(f"  [!] {message}")
    pause()


def delete_invoice(invoices):
    """Invoice delete karo"""
    header("INVOICE DELETE KAREIN")
    inv_id = input("  Delete karne wali Invoice ka ID: ").strip().upper()
    inv = next((i for i in invoices if i.get_id() == inv_id), None)

    if not inv:
        print(f"  [!] ID '{inv_id}' ki invoice nahi mili.")
        pause()
        return

    confirm = input(f"  Invoice '{inv_id}' delete karna chahte hain? (haan/nahi): ").strip().lower()
    if confirm == "haan":
        invoices.remove(inv)
        save_invoices(invoices)
        print("  ✔ Invoice delete ho gayi.")
    else:
        print("  Delete cancel kiya gaya.")
    pause()


# ================================================================
# REPORTS & ANALYTICS
# ================================================================

def menu_reports(projects, clients, invoices):
    """Reports aur charts ka sub-menu"""
    while True:
        header("REPORTS & ANALYTICS")
        print("  1. Financial Summary Dekhein")
        print("  2. Monthly Earnings Report")
        print("  3. Client-wise Earnings Report")
        print("  4. Sab Charts Generate Karein (PNG files)")
        print("  0. Wapas Main Menu")

        choice = input("\n  Option: ").strip()

        if choice == "1":
            header("FINANCIAL SUMMARY")
            summary = calculate_summary(projects, invoices)
            print_financial_summary(summary)
            pause()

        elif choice == "2":
            header("MONTHLY EARNINGS REPORT")
            from utils.finance import monthly_earnings_report
            df = monthly_earnings_report(projects)
            if df.empty:
                print("  Koi completed project nahi.")
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
                print("  Koi completed project nahi.")
            else:
                print(f"\n  {'Client':<20} {'Total Earned':>12}")
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
            print("  [!] Galat option.")


# ================================================================
# MAIN MENU
# ================================================================

def main_menu():
    """
    Program ka main entry point.
    Startup par data load karo, phir menu loop chalao.
    """
    # ── Startup: JSON files se data load karo ────────────────────
    print("\n  Freelance Management System shuru ho raha hai...")
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
        print("  1.  Clients        — Clients manage karein")
        print("  2.  Projects       — Projects manage karein")
        print("  3.  Invoices       — Invoices banayein aur dekhein")
        print("  4.  Reports        — Financial reports aur charts")
        print("  0.  Bahar Niklen   — Program band karein")
        print()

        choice = input("  Option chunein: ").strip()

        if   choice == "1": menu_clients(clients)
        elif choice == "2": menu_projects(projects, clients)
        elif choice == "3": menu_invoices(invoices, clients, projects)
        elif choice == "4": menu_reports(projects, clients, invoices)
        elif choice == "0":
            print("\n  Khuda Hafiz! Shukriya Freelance Management System use karne ka.")
            print("  Aapka data save ho gaya hai.\n")
            break
        else:
            print("  [!] Galat option. 0 se 4 ke beech mein chunein.")
            pause()


# ================================================================
# Program yahan se shuru hota hai
# ================================================================
if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        # Ctrl+C dabaya — gracefully band karo
        print("\n\n  Program band ho raha hai... Khuda Hafiz!")
        sys.exit(0)
