import pandas as pd
from datetime import datetime


def calculate_summary(projects, invoices):
    """
    return a summary of the financial performance of the projects and invoices
    """
    # Total earnings from all projects
    completed = [p for p in projects if p.get_status() == "Completed"]
    gross_all = sum(p.gross_earning() for p in projects)
    gross_completed = sum(p.gross_earning() for p in completed)

    # invoice totals
    paid_invoices=[inv for inv in invoices if inv.get_status() == "Paid"]
    unpaid_invoices =[inv for inv in invoices if inv.get_status() == "Unpaid"]

    total_invoiced  = sum(inv.grand_total() for inv in invoices)
    total_received= sum(inv.grand_total() for inv in paid_invoices)
    total_pending = sum(inv.grand_total() for inv in unpaid_invoices)

    # tax estimate (10% of gross completed earnings)
    tax_rate=0.10
    tax_estimate = gross_completed * tax_rate

    # net income 
    net_income = gross_completed - tax_estimate

    # profit margin % 
    profit_margin = (net_income / gross_completed * 100) if gross_completed > 0 else 0

    # average project value
    avg_project_value = (gross_completed / len(completed)) if completed else 0

    return {
        "total_projects":     len(projects),
        "completed_projects": len(completed),
        "gross_all":          gross_all,
        "gross_completed":    gross_completed,
        "tax_estimate":       tax_estimate,
        "net_income":         net_income,
        "profit_margin":      profit_margin,
        "avg_project_value":  avg_project_value,
        "total_invoiced":     total_invoiced,
        "total_received":     total_received,
        "total_pending":      total_pending,
    }


def monthly_earnings_report(projects):
    """
    return a report of the monthly earnings of the projects
    only completed projects are considered
    """
    completed = [p for p in projects if p.get_status() == "Completed"]

    if not completed:
        # no completed projects, return an empty dataframe
        return pd.DataFrame(columns=["Month", "Earnings"])

    rows = []
    for p in completed:
        try:
            # get the month from the deadline
            dt= datetime.strptime(p.get_deadline(), "%Y-%m-%d")
            month =dt.strftime("%Y-%m") # "2025-03"
            rows.append({"Month": month, "Earnings": p.gross_earning()})
        except:
            pass 

    if not rows:
        return pd.DataFrame(columns=["Month", "Earnings"])

    df = pd.DataFrame(rows)
    # group by munth and sum the earnin
    monthly = df.groupby("Month")["Earnings"].sum().reset_index()
    monthly = monthly.sort_values("Month") 
    return monthly


def project_status_counts(projects):
    """
    return a count of the number of projects in each status
    """
    counts = {}
    for p in projects:
        status = p.get_status()
        counts[status] = counts.get(status, 0) + 1
    return counts


def client_earnings_report(projects, clients):
    """
    return a report of the earnings of the clients
    only completed projects are considered
    """
    # Client ID-Name mapping
    id_to_name = {c.get_id(): c.get_name() for c in clients}

    rows = []
    for p in projects:
        if p.get_status() == "Completed":
            name = id_to_name.get(p.get_client_id(), p.get_client_id()) # client name or Id
            rows.append({"Client": name, "Earnings": p.gross_earning()})

    if not rows:
        return pd.DataFrame(columns=["Client", "Earnings"])

    # group by client and sum the earnings
    df = pd.DataFrame(rows)
    report = df.groupby("Client")["Earnings"].sum().reset_index()
    report = report.sort_values("Earnings", ascending=False) # sort by earnings
    return report


def print_financial_summary(summary):
    """print the financial summary in a formatted table"""
    print("\n" + "="*50)
    print("       FINANCIAL SUMMARY")
    print("="*50)
    print(f"  Total Projects       : {summary['total_projects']}")
    print(f"  Completed Projects   : {summary['completed_projects']}")
    print("-"*50)
    print(f"  Gross Earnings (All) : ${summary['gross_all']:>10.2f}")
    print(f"  Gross (Completed)    : ${summary['gross_completed']:>10.2f}")
    print(f"  Tax Estimate (10%)   : ${summary['tax_estimate']:>10.2f}")
    print(f"  Net Income           : ${summary['net_income']:>10.2f}")
    print(f"  Profit Margin        : {summary['profit_margin']:>9.1f}%")
    print(f"  Avg Project Value    : ${summary['avg_project_value']:>10.2f}")
    print("-"*50)
    print(f"  Total Invoiced       : ${summary['total_invoiced']:>10.2f}")
    print(f"  Total Received       : ${summary['total_received']:>10.2f}")
    print(f"  Total Pending        : ${summary['total_pending']:>10.2f}")
    print("="*50)
