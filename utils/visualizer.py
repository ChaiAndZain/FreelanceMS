import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from utils.finance import monthly_earnings_report, project_status_counts, client_earnings_report

# charts saveing path
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")



def _save_and_confirm(filename):
    """Chart ko file mein save karo aur path print karo"""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    filepath = os.path.join(REPORTS_DIR, filename)
    plt.savefig(filepath, dpi=150, bbox_inches="tight", facecolor="#1a1a2e") 
    plt.close() 
    print(f"\n  ✔ Chart saved: reports/{filename}")
    return filepath


def _apply_dark_style():
    """apply dark, professional style to all charts"""
    plt.rcParams.update({
        "figure.facecolor":  "#1a1a2e",    # dark navy background
        "axes.facecolor":    "#16213e",    # axes background
        "axes.edgecolor":    "#e0e0e0",
        "axes.labelcolor":   "#e0e0e0",
        "text.color":        "#e0e0e0",
        "xtick.color":       "#e0e0e0",
        "ytick.color":       "#e0e0e0",
        "grid.color":        "#2d4059",
        "grid.linestyle":    "--",
        "grid.alpha":        0.5,
        "font.family":       "DejaVu Sans",
    })


# monthly earnings bar chart
def chart_monthly_earnings(projects):
    """
    return a bar chart of the monthly earnings of the projects
    only completed projects are considered
    """
    df = monthly_earnings_report(projects)

    if df.empty:
        print("  [Info] No completed projects, no charts")
        return

    _apply_dark_style()
    fig, ax = plt.subplots(figsize=(10, 5))

    # gradient-like bars
    colors = plt.cm.cool([i / len(df) for i in range(len(df))])
    bars = ax.bar(df["Month"], df["Earnings"], color=colors)

    # add values on top of each bar
    for bar, val in zip(bars, df["Earnings"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"${val:,.0f}",
            ha="center", va="bottom", fontsize=9, color="#e0e0e0", fontweight="bold") 
            
    ax.set_title("Monthly Earnings Overview", fontsize=14, fontweight="bold", color="#e94560", pad=15)
    ax.set_xlabel("Month", fontsize=11)
    ax.set_ylabel("Earnings (usd)", fontsize=11)
    ax.grid(axis="y")
    plt.xticks(rotation=45)
    plt.tight_layout()
    _save_and_confirm("monthly_earnings.png")

# project status pie chart
def chart_project_status(projects):
    """
    return a pie chart of the number of projects in each status
    """
    counts = project_status_counts(projects)

    if not counts:
        print("  [Info] No projects, no chart")
        return

    _apply_dark_style()
    fig, ax = plt.subplots(figsize=(7, 7))

    # status colors
    status_colors = {
        "Pending":     "#f5a623",
        "In Progress": "#4a90d9",
        "Completed":   "#7ed321",
        "Cancelled":   "#e94560",
    }
    labels = list(counts.keys())
    sizes  = list(counts.values())
    colors = [status_colors.get(l, "#aaaaaa") for l in labels]

    # plot the pie chart simple 
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=140, pctdistance=0.75)
    for t in texts: t.set_color("#e0e0e0")
    for at in autotexts: at.set_color("white"); at.set_fontweight("bold")

    ax.set_title("Project Status Distribution", fontsize=14, fontweight="bold", color="#e94560", pad=20)
    plt.tight_layout()
    _save_and_confirm("project_status.png")

# client earnings bar chart
def chart_client_earnings(projects, clients):
    """
    return a horizontal bar chart of the earnings of the clients
    """
    df = client_earnings_report(projects, clients)

    if df.empty:
        print("  [Info] No completed projects, no chart")
        return

    _apply_dark_style()
    fig, ax = plt.subplots(figsize=(9, max(4, len(df) * 0.8)))

    colors = plt.cm.cool([i / len(df) for i in range(len(df))])
    bars = ax.barh(df["Client"], df["Earnings"], color=colors,
                   edgecolor="#0f3460", linewidth=0.8, height=0.6)

    # label values on each bar
    for bar, val in zip(bars, df["Earnings"]):
        ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2,
            f"${val:,.0f}", va="center", fontsize=9, color="#e0e0e0", fontweight="bold")

    ax.set_title("Earnings per Client", fontsize=14,
                 fontweight="bold", color="#e94560", pad=15)
    ax.set_xlabel("Total Earnings (USD)", fontsize=11)
    ax.grid(axis="x")
    plt.tight_layout()

    _save_and_confirm("client_earnings.png")


# generate all charts
def generate_all_charts(projects, clients):
    """generate all charts in one call"""
    print("\n  Charts generate ho rahe hain...")
    chart_monthly_earnings(projects)
    chart_project_status(projects)
    chart_client_earnings(projects, clients)
    print("  All charts saved in \"reports/\" folder ✔")
