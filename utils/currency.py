# ================================================================
# utils/currency.py
# USD ↔ PKR conversion rate yahan se aata hai
# Internet se live rate scrape karte hain forex.pk se
# ================================================================

import requests
from bs4 import BeautifulSoup


# Default fallback rate — sirf tab use hota hai jab user offline ho
# aur manually bhi rate na de
DEFAULT_FALLBACK_RATE = 280.0


def current_USD_2_PKR_rate() -> float:
    """
    Live USD to PKR exchange rate forex.pk se fetch karo.
    Network fail ho ya parsing fail ho toh exception throw hogi.
    """
    url = "https://www.forex.pk/currency-usd-to-pkr-to-us-dollar.php"
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    span = soup.find("span", attrs={"id": "RATESPAN"})
    if span is None:
        raise ValueError("Page mein RATESPAN nahi mila — site ka format change ho gaya hoga")
    return float(span.text)


def get_usd_to_pkr_rate(verbose=True):
    """
    Live rate fetch karne ki koshish karo. Fail ho toh None return karo.
    UI layer (main.py) decide karega ke manually rate maange ya cancel kare.

    Returns: float rate ya None
    """
    try:
        rate = current_USD_2_PKR_rate()
        if verbose:
            print(f"  ✔ Live rate mil gaya: 1 USD = Rs. {rate:.2f}")
        return rate
    except requests.RequestException as e:
        if verbose:
            print(f"  [!] Rate fetch nahi ho saka (network issue): {e}")
    except ValueError as e:
        if verbose:
            print(f"  [!] Rate parse nahi hua: {e}")
    except Exception as e:
        if verbose:
            print(f"  [!] Unexpected error: {e}")
    return None
