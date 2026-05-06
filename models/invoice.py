# ================================================================
# models/invoice.py
# Invoice class — payment ka record yahan hoga
# Project ke complete hone ke baad invoice generate hoti hai
# ================================================================

from datetime import datetime, timedelta

# Invoice ke possible statuses
INVOICE_STATUS = ["Unpaid", "Paid", "Overdue"]

class InvoiceItem:
    """Invoice ki ek line item — kya kaam kiya aur kitne ka"""

    def __init__(self, description, quantity, unit_price):
        self.description = description       # kaam ka naam
        self.quantity    = float(quantity)   # kitna (hours ya units)
        self.unit_price  = float(unit_price) # per unit price

    def total(self):
        # is item ka total = quantity * price
        return self.quantity * self.unit_price

    def to_dict(self):
        return {
            "description": self.description,
            "quantity":    self.quantity,
            "unit_price":  self.unit_price
        }

    @classmethod
    def from_dict(cls, d):
        return cls(d["description"], d["quantity"], d["unit_price"])


class Invoice:
    """
    Client ko bheji jaane wali invoice.
    Ek ya zyada InvoiceItems hoti hain.
    Tax calculate karta hai aur net total dikhata hai.
    """

    TAX_RATE = 0.10   # 10% tax rate (badal sakte hain)

    def __init__(self, invoice_id, client_id, project_id,
                 issue_date, due_days, items, status="Unpaid", notes=""):
        self.__invoice_id  = invoice_id     # unique ID (INV001...)
        self.__client_id   = client_id      # client ka ID
        self.__project_id  = project_id     # related project
        self.__issue_date  = issue_date     # invoice ki date (YYYY-MM-DD)
        self.__due_days    = int(due_days)  # kitne din mein payment chahiye
        self.__items       = items          # list of InvoiceItem objects
        self.__status      = status         # Unpaid / Paid / Overdue
        self.__notes       = notes          # extra notes

    # ── Getters ──────────────────────────────────────────────────
    def get_id(self):          return self.__invoice_id
    def get_client_id(self):   return self.__client_id
    def get_project_id(self):  return self.__project_id
    def get_issue_date(self):  return self.__issue_date
    def get_due_days(self):    return self.__due_days
    def get_items(self):       return self.__items
    def get_status(self):      return self.__status
    def get_notes(self):       return self.__notes

    def set_status(self, s):   self.__status = s
    def set_notes(self, n):    self.__notes = n

    # ── Due date calculate karo ───────────────────────────────────
    def due_date(self):
        try:
            issue = datetime.strptime(self.__issue_date, "%Y-%m-%d")
            return (issue + timedelta(days=self.__due_days)).strftime("%Y-%m-%d")
        except:
            return "N/A"

    # ── Sub-total (tax se pehle) ──────────────────────────────────
    def subtotal(self):
        return sum(item.total() for item in self.__items)

    # ── Tax amount ───────────────────────────────────────────────
    def tax_amount(self):
        return self.subtotal() * Invoice.TAX_RATE

    # ── Grand total (tax ke baad) ─────────────────────────────────
    def grand_total(self):
        return self.subtotal() + self.tax_amount()

    # ── Item add karo ────────────────────────────────────────────
    def add_item(self, item: InvoiceItem):
        self.__items.append(item)

    # ── Dictionary mein convert karo ─────────────────────────────
    def to_dict(self):
        return {
            "invoice_id":  self.__invoice_id,
            "client_id":   self.__client_id,
            "project_id":  self.__project_id,
            "issue_date":  self.__issue_date,
            "due_days":    self.__due_days,
            "items":       [i.to_dict() for i in self.__items],
            "status":      self.__status,
            "notes":       self.__notes
        }

    @classmethod
    def from_dict(cls, data):
        items = [InvoiceItem.from_dict(i) for i in data.get("items", [])]
        return cls(
            data["invoice_id"],
            data["client_id"],
            data["project_id"],
            data["issue_date"],
            data["due_days"],
            items,
            data.get("status", "Unpaid"),
            data.get("notes", "")
        )

    # ── Formatted invoice print karo ─────────────────────────────
    def __str__(self):
        lines = [
            f"\n  {'='*45}",
            f"  INVOICE: {self.__invoice_id}",
            f"  {'='*45}",
            f"  Client ID  : {self.__client_id}",
            f"  Project ID : {self.__project_id}",
            f"  Issue Date : {self.__issue_date}",
            f"  Due Date   : {self.due_date()}",
            f"  Status     : {self.__status}",
            f"  {'-'*45}",
            f"  {'Description':<25} {'Qty':>5} {'Price':>8} {'Total':>9}",
            f"  {'-'*45}",
        ]
        for item in self.__items:
            lines.append(
                f"  {item.description:<25} {item.quantity:>5.1f} "
                f"${item.unit_price:>7.2f} ${item.total():>8.2f}"
            )
        lines += [
            f"  {'-'*45}",
            f"  {'Subtotal':<35} ${self.subtotal():>8.2f}",
            f"  {'Tax (10%)':<35} ${self.tax_amount():>8.2f}",
            f"  {'GRAND TOTAL':<35} ${self.grand_total():>8.2f}",
            f"  {'='*45}",
        ]
        if self.__notes:
            lines.append(f"  Notes: {self.__notes}")
        return "\n".join(lines)
