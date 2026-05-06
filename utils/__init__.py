# utils/__init__.py
from .file_handler import (load_clients,  save_clients,
                            load_projects, save_projects,
                            load_invoices, save_invoices,
                            next_id)
from .finance     import (calculate_summary, print_financial_summary,
                           monthly_earnings_report, client_earnings_report)
from .visualizer  import generate_all_charts
