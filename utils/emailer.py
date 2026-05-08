import os
import smtplib
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv

def _load_env():
    """
    loads environment variables from .env file
    """
    try: load_dotenv()
    except: pass


def _build_invoice_body(invoice, client):
    """
    builds the email body for the invoice
    display amounts in the invoice currency, if the currency is not USD, display the FX rate
    """
    sender = os.environ.get("SMTP_FROM_NAME", "Freelancer")

    lines = [
        f"Good Day! {client.get_name()},"
    ]

    lines += invoice.__str__().split("\n")
    lines += [
        "",
        "Thank you for your payment. If you have any questions, please reply to this email.",
        "",
        "Regards,",
        sender,
    ]

    return "\n".join(lines)


def send_invoice_email(invoice, client):
    """
    sends the invoice email to the client

    Returns: (success: bool, message: str)
    """
    _load_env()

    user       = os.environ.get("SMTP_USER", "").strip()
    password   = os.environ.get("SMTP_PASSWORD", "")
    from_name  = os.environ.get("SMTP_FROM_NAME", "Freelancer").strip()
    from_email = os.environ.get("SMTP_FROM_EMAIL", user).strip()

    # Required credentials check
    if  not user or not password or not from_email:
        return False, f"SMTP credentials are missing in the .env file"

    # validate the client email
    to_email = (client.get_email() or "").strip()
    if not to_email or "@" not in to_email:
        return False, f"Client '{client.get_name()}' does not have a valid email: '{to_email}'"


    # build the email body
    sym = invoice.currency_symbol()
    msg = EmailMessage()
    msg["Subject"] = (
        f"Invoice {invoice.get_id()} — {sym}{invoice.display_total():,.2f} "
        f"{invoice.get_currency()} (Due {invoice.due_date()})"
    )
    msg["From"] = f"{from_name} <{from_email}>" if from_name else from_email
    msg["To"] = to_email
    msg.set_content(_build_invoice_body(invoice, client))

    # send the email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", "465", timeout=30) as smtp:
            smtp.login(user, password)
            smtp.send_message(msg)
        return True, f"Email '{to_email}' was sent successfully"
    except Exception as e:
        return False, f"Failed to send email: {e}"
