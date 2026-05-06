# ================================================================
# utils/visualizer.py
# Matplotlib se charts banao aur PNG files mein save karo
# CLI mein inline render nahi hota isliye files mein save karte hain
# ================================================================

import os
import matplotlib
matplotlib.use("Agg")          # GUI window nahi chahiye — file save karne ke liye
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from utils.finance import (monthly_earnings_report, project_status_counts,
                            client_earnings_report)

# Charts kahan save honge
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")


def _ensure_reports_dir():
    """reports/ folder nahi hai toh bana do"""
    os.makedirs(REPORTS_DIR, exist_ok=True)


def _save_and_confirm(filename):
    """Chart ko file mein save karo aur path print karo"""
    _ensure_reports_dir()
    filepath = os.path.join(REPORTS_DIR, filename)
    plt.savefig(filepath, dpi=150, bbox_inches="tight",
                facecolor="#1a1a2e")   # dark background ke saath save karo
    plt.close()   # memory free karo
    print(f"\n  ✔ Chart save ho gaya: reports/{filename}")
    return filepath


def _apply_dark_style():
    """Saare charts mein dark, professional style apply karo"""
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


# ── Chart 1: Monthly Earnings Bar Chart ──────────────────────────

def chart_monthly_earnings(projects):
    """
    Har mahine ki earnings ka bar chart banao.
    X-axis: months, Y-axis: USD earnings
    """
    df = monthly_earnings_report(projects)

    if df.empty:
        print("  [Info] Koi completed project nahi — chart nahi ban sakta.")
        return

    _apply_dark_style()
    fig, ax = plt.subplots(figsize=(10, 5))

    # Gradient-like bars — neeche se upar color badalta hai
    colors = plt.cm.cool([i / len(df) for i in range(len(df))])
    bars = ax.bar(df["Month"], df["Earnings"], color=colors,
                  edgecolor="#0f3460", linewidth=0.8, width=0.6)

    # Har bar ke upar value dikhao
    for bar, val in zip(bars, df["Earnings"]):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(df["Earnings"]) * 0.02,
                f"${val:,.0f}", ha="center", va="bottom",
                fontsize=9, color="#e0e0e0", fontweight="bold")

    ax.set_title("Monthly Earnings Overview", fontsize=14,
                 fontweight="bold", color="#e94560", pad=15)
    ax.set_xlabel("Month", fontsize=11)
    ax.set_ylabel("Earnings (USD)", fontsize=11)
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.grid(axis="y")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    _save_and_confirm("monthly_earnings.png")


# ── Chart 2: Project Status Pie Chart ────────────────────────────

def chart_project_status(projects):
    """
    Kitne projects Pending / In Progress / Completed / Cancelled hain
    — pie chart mein dikhao
    """
    counts = project_status_counts(projects)

    if not counts:
        print("  [Info] Koi project nahi — chart nahi ban sakta.")
        return

    _apply_dark_style()
    fig, ax = plt.subplots(figsize=(7, 7))

    # Har status ke liye rang
    status_colors = {
        "Pending":     "#f5a623",
        "In Progress": "#4a90d9",
        "Completed":   "#7ed321",
        "Cancelled":   "#e94560",
    }
    labels = list(counts.keys())
    sizes  = list(counts.values())
    colors = [status_colors.get(l, "#aaaaaa") for l in labels]

    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors,
        autopct="%1.1f%%", startangle=140,
        pctdistance=0.75,
        wedgeprops={"edgecolor": "#1a1a2e", "linewidth": 2}
    )
    for t in texts:      t.set_color("#e0e0e0")
    for at in autotexts: at.set_color("white"); at.set_fontweight("bold")

    ax.set_title("Project Status Distribution", fontsize=14,
                 fontweight="bold", color="#e94560", pad=20)
    plt.tight_layout()

    _save_and_confirm("project_status.png")


# ── Chart 3: Client Earnings Bar Chart ───────────────────────────

def chart_client_earnings(projects, clients):
    """
    Har client se kitni kamai hui — horizontal bar chart
    """
    df = client_earnings_report(projects, clients)

    if df.empty:
        print("  [Info] Koi completed project nahi — chart nahi ban sakta.")
        return

    _apply_dark_style()
    fig, ax = plt.subplots(figsize=(9, max(4, len(df) * 0.8)))

    colors = plt.cm.plasma([i / len(df) for i in range(len(df))])
    bars = ax.barh(df["Client"], df["Earnings"], color=colors,
                   edgecolor="#0f3460", linewidth=0.8, height=0.6)

    # Har bar ke sath value
    for bar, val in zip(bars, df["Earnings"]):
        ax.text(bar.get_width() + max(df["Earnings"]) * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f"${val:,.0f}", va="center",
                fontsize=9, color="#e0e0e0", fontweight="bold")

    ax.set_title("Earnings per Client", fontsize=14,
                 fontweight="bold", color="#e94560", pad=15)
    ax.set_xlabel("Total Earnings (USD)", fontsize=11)
    ax.xaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.grid(axis="x")
    plt.tight_layout()

    _save_and_confirm("client_earnings.png")


# ── Generate All Charts ───────────────────────────────────────────

def generate_all_charts(projects, clients):
    """Ek call mein teeno charts generate karo"""
    print("\n  Charts generate ho rahe hain...")
    chart_monthly_earnings(projects)
    chart_project_status(projects)
    chart_client_earnings(projects, clients)
    print("  Sab charts reports/ folder mein save ho gaye! ✔")
