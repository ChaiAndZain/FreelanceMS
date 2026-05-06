# models/__init__.py
# Is folder ke classes ko easily import karne ke liye
from .client  import Client
from .project import Project, STATUS_OPTIONS
from .invoice import Invoice, InvoiceItem, INVOICE_STATUS
