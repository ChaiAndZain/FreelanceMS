import requests
from bs4 import BeautifulSoup

# default fx-rate, it is used when internet is lost
DEFAULT_FALLBACK_RATE = 280.0


def current_USD_2_PKR_rate() -> float:
    """
    get the current exchange rate for USD to PRK
    """
    url = "https://www.forex.pk/currency-usd-to-pkr-to-us-dollar.php"
    # sending request
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    span = soup.find("span", attrs={"id": "RATESPAN"})
    if span is None:
        raise ValueError("Specified span not found in the page")
    return float(span.text)


def get_usd_to_pkr_rate(verbose=True):
    """
    Try to get the current exchange rate for USD to PRK
    if verbose is True, print the rate and error messages
    """
    try:
        rate = current_USD_2_PKR_rate()
        if verbose:
            print(f"  ✔ Live rate fetched: 1 USD = Rs. {rate:.2f}")
        return rate
    except requests.RequestException as e:
        if verbose:
            print(f"  [!] Failed to fetch rate due to network issue: {e}")
    except ValueError as e:
        if verbose:
            print(f"  [!] Element not found: {e}")
    except Exception as e:
        if verbose:
            print(f"  [!] Unexpected error: {e}")
    return None
