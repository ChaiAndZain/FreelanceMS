# ================================================================
# utils/emailer.py
# SMTP ke zariye client ko invoice email bhejne ka kaam yahan hota hai
# Credentials .env file mein hote hain (project root mein)
# ================================================================

import os
import smtplib
import ssl
from email.message import EmailMessage


# Project root mein .env file ka path
_ENV_PATH = os.path.join(os.path.dirname(__file__), "..", ".env")


def _load_env():
    """
    .env file se environment variables load karo.
    python-dotenv installed ho toh wo use karo, warna manual parse.
    """
    try:
        from dotenv import load_dotenv
        load_dotenv(_ENV_PATH, override=False)
        return
    except ImportError:
        pass

    # Manual fallback — agar python-dotenv install nahi hai
    if not os.path.exists(_ENV_PATH):
        return
    try:
        with open(_ENV_PATH, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                # Already-set env vars ko override mat karo
                os.environ.setdefault(key, value)
    except Exception as e:
        print(f"  [Warning] .env padhne mein masla hua: {e}")


def _build_invoice_body(invoice, client):
    """
    Email ke liye plain-text invoice body banao.
    Invoice ki currency (USD ya PKR) ke hisaab se amounts dikhayi jaati hain.
    """
    sender = os.environ.get("SMTP_FROM_NAME", "Freelancer")
    sym = invoice.currency_symbol()
    cur = invoice.get_currency()

    lines = [
        f"As-salamu alaykum {client.get_name()},",
        "",
        f"Aapki invoice {invoice.get_id()} neeche di gayi hai. "
        f"Baraye meherbani due date se pehle payment kar dein.",
        "",
        f"Invoice ID  : {invoice.get_id()}",
        f"Issue Date  : {invoice.get_issue_date()}",
        f"Due Date    : {invoice.due_date()}",
        f"Status      : {invoice.get_status()}",
        f"Currency    : {cur}",
    ]
    if cur != "USD":
        lines.append(
            f"FX Rate     : 1 USD = {sym} {invoice.get_fx_rate():.2f} "
            f"(snapshot at issue)"
        )
    lines += [
        "",
        "-" * 60,
        f"{'Description':<28} {'Qty':>6} {'Price':>11} {'Total':>13}",
        "-" * 60,
    ]
    for item in invoice.get_items():
        lines.append(
            f"{item.description:<28} {item.quantity:>6.1f} "
            f"{sym}{invoice.display_unit_price(item):>10.2f} "
            f"{sym}{invoice.display_item_total(item):>12.2f}"
        )
    lines += [
        "-" * 60,
        f"{'Subtotal':<46} {sym}{invoice.display_subtotal():>13.2f}",
        f"{'Tax (10%)':<46} {sym}{invoice.display_tax():>13.2f}",
        f"{'GRAND TOTAL':<46} {sym}{invoice.display_total():>13.2f}",
    ]
    if cur != "USD":
        lines.append(
            f"{'(USD equivalent)':<46} ${invoice.grand_total():>13.2f}"
        )
    lines.append("=" * 60)

    if invoice.get_notes():
        lines += ["", f"Notes: {invoice.get_notes()}"]
    lines += [
        "",
        "Payment ka shukriya. Koi sawal ho toh is email ka jawab de dein.",
        "",
        "Regards,",
        sender,
    ]
    return "\n".join(lines)


def send_invoice_email(invoice, client):
    """
    Client ke email pe invoice bhejo.

    Returns: (success: bool, message: str)
    """
    _load_env()

    host       = os.environ.get("SMTP_HOST", "").strip()
    port_str   = os.environ.get("SMTP_PORT", "587").strip()
    user       = os.environ.get("SMTP_USER", "").strip()
    password   = os.environ.get("SMTP_PASSWORD", "")
    from_name  = os.environ.get("SMTP_FROM_NAME", "Freelancer").strip()
    from_email = os.environ.get("SMTP_FROM_EMAIL", user).strip()
    use_tls    = os.environ.get("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes", "on")

    # Required credentials check
    missing = [k for k, v in {
        "SMTP_HOST": host,
        "SMTP_USER": user,
        "SMTP_PASSWORD": password,
        "SMTP_FROM_EMAIL": from_email,
    }.items() if not v]
    if missing:
        return False, f"SMTP credentials adhoori hain (.env mein set karein): {', '.join(missing)}"

    # Client ka email valid hai?
    to_email = (client.get_email() or "").strip()
    if not to_email or "@" not in to_email:
        return False, f"Client '{client.get_name()}' ka email valid nahi hai: '{to_email}'"

    try:
        port = int(port_str)
    except ValueError:
        return False, f"SMTP_PORT galat hai: '{port_str}'"

    sym = invoice.currency_symbol()
    msg = EmailMessage()
    msg["Subject"] = (
        f"Invoice {invoice.get_id()} — {sym}{invoice.display_total():,.2f} "
        f"{invoice.get_currency()} (Due {invoice.due_date()})"
    )
    msg["From"]    = f"{from_name} <{from_email}>" if from_name else from_email
    msg["To"]      = to_email
    msg.set_content(_build_invoice_body(invoice, client))

    try:
        # Port 465 ka matlab SSL, baaki STARTTLS ya plain
        if port == 465:
            ctx = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, context=ctx, timeout=30) as smtp:
                smtp.login(user, password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=30) as smtp:
                smtp.ehlo()
                if use_tls:
                    ctx = ssl.create_default_context()
                    smtp.starttls(context=ctx)
                    smtp.ehlo()
                smtp.login(user, password)
                smtp.send_message(msg)
        return True, f"Email '{to_email}' pe successfully bhej di gayi."

    except smtplib.SMTPAuthenticationError:
        return False, ("SMTP authentication fail. Username/password galat hain. "
                       "Gmail use kar rahe hain toh App Password lazmi hai.")
    except smtplib.SMTPConnectError as e:
        return False, f"SMTP server se connect nahi ho saka: {e}"
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {e}"
    except (OSError, TimeoutError) as e:
        return False, f"Network error: {e}"
