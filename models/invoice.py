# ================================================================
# models/invoice.py
# Invoice class — payment ka record yahan hoga
# Project ke complete hone ke baad invoice generate hoti hai
#
# IMPORTANT: Internal storage hamesha USD mein hota hai (data,
# reports, charts — sab USD-based). `currency` field sirf is invoice
# ke display ke liye hai. PKR ke liye fx_rate (USD->PKR snapshot)
# bhi save hoti hai taake future views consistent rahein.
# ================================================================

from datetime import datetime, timedelta

# Invoice ke possible statuses
INVOICE_STATUS = ["Unpaid", "Paid", "Overdue"]

# Supported display currencies
SUPPORTED_CURRENCIES = ["USD", "PKR"]


class InvoiceItem:
    """Invoice ki ek line item — kya kaam kiya aur kitne ka (USD mein)"""

    def __init__(self, description, quantity, unit_price):
        self.description = description       # kaam ka naam
        self.quantity    = float(quantity)   # kitna (hours ya units)
        self.unit_price  = float(unit_price) # per unit price USD mein

    def total(self):
        # is item ka total USD mein = quantity * price
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

    Currency notes:
    - subtotal(), tax_amount(), grand_total() hamesha USD return karte hain
      (reports aur summaries inhi pe depend karte hain)
    - display_*() methods invoice ki currency mein values dete hain
    """

    TAX_RATE = 0.10   # 10% tax rate (badal sakte hain)

    def __init__(self, invoice_id, client_id, project_id,
                 issue_date, due_days, items, status="Unpaid", notes="",
                 currency="USD", fx_rate=1.0):
        self.__invoice_id  = invoice_id     # unique ID (INV001...)
        self.__client_id   = client_id      # client ka ID
        self.__project_id  = project_id     # related project
        self.__issue_date  = issue_date     # invoice ki date (YYYY-MM-DD)
        self.__due_days    = int(due_days)  # kitne din mein payment chahiye
        self.__items       = items          # list of InvoiceItem objects
        self.__status      = status         # Unpaid / Paid / Overdue
        self.__notes       = notes          # extra notes

        # Currency snapshot — change nahi hote baad mein, taake invoice
        # exactly waisa hi dikhe jaisa client ko bheja gaya tha
        currency = (currency or "USD").upper()
        if currency not in SUPPORTED_CURRENCIES:
            currency = "USD"
        self.__currency = currency
        # USD ke liye rate hamesha 1.0; PKR ke liye snapshot rate
        self.__fx_rate = float(fx_rate) if currency != "USD" else 1.0

    # ── Getters ──────────────────────────────────────────────────
    def get_id(self):          return self.__invoice_id
    def get_client_id(self):   return self.__client_id
    def get_project_id(self):  return self.__project_id
    def get_issue_date(self):  return self.__issue_date
    def get_due_days(self):    return self.__due_days
    def get_items(self):       return self.__items
    def get_status(self):      return self.__status
    def get_notes(self):       return self.__notes
    def get_currency(self):    return self.__currency
    def get_fx_rate(self):     return self.__fx_rate

    def set_status(self, s):   self.__status = s
    def set_notes(self, n):    self.__notes = n

    # ── Due date calculate karo ───────────────────────────────────
    def due_date(self):
        try:
            issue = datetime.strptime(self.__issue_date, "%Y-%m-%d")
            return (issue + timedelta(days=self.__due_days)).strftime("%Y-%m-%d")
        except:
            return "N/A"

    # ── USD-canonical amounts (reports inhe use karti hain) ──────
    def subtotal(self):
        return sum(item.total() for item in self.__items)

    def tax_amount(self):
        return self.subtotal() * Invoice.TAX_RATE

    def grand_total(self):
        return self.subtotal() + self.tax_amount()

    # ── Display amounts (invoice ki currency mein) ───────────────
    def currency_symbol(self):
        return "Rs." if self.__currency == "PKR" else "$"

    def convert(self, usd_amount):
        """USD amount ko invoice currency mein convert karo"""
        return usd_amount * self.__fx_rate

    def display_unit_price(self, item):
        return item.unit_price * self.__fx_rate

    def display_item_total(self, item):
        return item.total() * self.__fx_rate

    def display_subtotal(self):
        return self.convert(self.subtotal())

    def display_tax(self):
        return self.convert(self.tax_amount())

    def display_total(self):
        return self.convert(self.grand_total())

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
            "notes":       self.__notes,
            "currency":    self.__currency,
            "fx_rate":     self.__fx_rate,
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
            data.get("notes", ""),
            # Backward compat: purani invoices mein ye fields nahi hongi
            data.get("currency", "USD"),
            data.get("fx_rate", 1.0),
        )

    # ── Formatted invoice print karo ─────────────────────────────
    def __str__(self):
        sym = self.currency_symbol()
        # Width adjust karen — "Rs." 3 chars hai, "$" sirf 1 hai
        price_w = 9 if sym == "$" else 11
        total_w = 10 if sym == "$" else 12

        lines = [
            f"\n  {'='*55}",
            f"  INVOICE: {self.__invoice_id}    [Currency: {self.__currency}]",
            f"  {'='*55}",
            f"  Client ID  : {self.__client_id}",
            f"  Project ID : {self.__project_id}",
            f"  Issue Date : {self.__issue_date}",
            f"  Due Date   : {self.due_date()}",
            f"  Status     : {self.__status}",
        ]
        if self.__currency != "USD":
            lines.append(f"  FX Rate    : 1 USD = {sym} {self.__fx_rate:.2f}  "
                         f"(snapshot at issue)")
        lines += [
            f"  {'-'*55}",
            f"  {'Description':<25} {'Qty':>5} {'Price':>{price_w}} {'Total':>{total_w}}",
            f"  {'-'*55}",
        ]
        for item in self.__items:
            lines.append(
                f"  {item.description:<25} {item.quantity:>5.1f} "
                f"{sym}{self.display_unit_price(item):>{price_w-1}.2f} "
                f"{sym}{self.display_item_total(item):>{total_w-1}.2f}"
            )
        lines += [
            f"  {'-'*55}",
            f"  {'Subtotal':<40} {sym}{self.display_subtotal():>11.2f}",
            f"  {'Tax (10%)':<40} {sym}{self.display_tax():>11.2f}",
            f"  {'GRAND TOTAL':<40} {sym}{self.display_total():>11.2f}",
        ]
        if self.__currency != "USD":
            lines.append(
                f"  {'(USD equivalent)':<40} ${self.grand_total():>11.2f}"
            )
        lines.append(f"  {'='*55}")
        if self.__notes:
            lines.append(f"  Notes: {self.__notes}")
        return "\n".join(lines)
