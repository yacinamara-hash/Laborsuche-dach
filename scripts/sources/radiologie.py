# radiologie.py (korrigiert, lauffähig, minimal)
from bs4 import BeautifulSoup
from datetime import date
import re
import sys
import json
import argparse

RADIOLOGY_KEYWORDS = ("radiologie", "radiologe", "radiologin")
TECH_KEYWORDS = ("röntgen", "mrt", "ct")
OFFER_KEYWORDS = ("wir bieten", "angebot", "leistungen", "wir führen", "wir bitten")


def has_word(text: str, word: str) -> bool:
    """Wortgrenzen-Check (case-insensitive)."""
    return re.search(rf"\b{re.escape(word)}\b", text, flags=re.IGNORECASE) is not None


def contains_any(text: str, keywords) -> bool:
    """Case-insensitive substring check for any keyword in keywords."""
    text_l = text.lower()
    return any(k.lower() in text_l for k in keywords)


def extract(html: str) -> dict:
    """
    Minimaler Scraper: erkennt Radiologie-Seiten und liefert ein Provider-Dict.
    Gibt {} zurück, wenn die Seite nicht als Radiologie erkannt wird.
    """
    soup = BeautifulSoup(html, "html.parser")

    name_el = soup.select_one("h1") or soup.select_one(".provider-name")
    name = name_el.get_text(strip=True) if name_el else "Unbenannter Anbieter"

    text = soup.get_text(" ", strip=True)
    text_l = text.lower()

    # Services / Flags
    services = {
        "dexa_body_composition": "body composition" in text_l or "körperzusammensetzung" in text_l,
        "dexa_bone_density": "knochendichte" in text_l or "bone density" in text_l,
        "blood_self_pay": "selbstzahler" in text_l and "blut" in text_l,
        # radiologe-Flag: radiologie-Keywords OR technische Keywords
        "radiologe": contains_any(text, RADIOLOGY_KEYWORDS) or contains_any(text, TECH_KEYWORDS),
    }

    # Radiologie-Erkennung: direkte Keywords OR technische Keywords OR Angebotsformulierung + radiologie
    is_radiologie = (
        services["radiologe"]
        or any(has_word(text, k) for k in RADIOLOGY_KEYWORDS)
        or (contains_any(text, OFFER_KEYWORDS) and contains_any(text, RADIOLOGY_KEYWORDS))
    )

    if not is_radiologie:
        # Keine Radiologie-Seite: nichts zurückgeben
        return {}

    # Adresse (einfach)
    addr_el = soup.select_one("address") or soup.select_one(".address")
    street = zipc = city = None
    if addr_el:
        addr = addr_el.get_text(" ", strip=True)
        m = re.search(r"(\d{5})\s+([A-Za-zÄÖÜäöüß\-\s]+)$", addr)
        if m:
            zipc = m.group(1)
            city = m.group(2).strip()
            street = addr[:m.start()].strip().rstrip(",")
        else:
            street = addr

    # Kontakt (Telefon / Website)
    contact = {}
    tel_el = soup.select_one("a[href^='tel:']")
    if tel_el and tel_el.has_attr("href"):
        contact["phone"] = tel_el["href"].replace("tel:", "").strip()
    else:
        # Suche nach Telefonnummer-Text fallback
        m_tel = re.search(r"(\+?\d[\d\s\-/()]{6,}\d)", text)
        if m_tel:
            contact["phone"] = m_tel.group(1).strip()

    site_el = soup.select_one("a[href^='http']")
    if site_el and site_el.has_attr("href"):
        contact["website"] = site_el["href"].strip()

    result = {
        "name": name,
        "category": "RADIOLOGIE",
        "services": services,
        "self_pay": services.get("blood_self_pay", False),
        "address": {"street": street, "zip": zipc, "city": city, "country": "DE"},
        "location": {},  # geocode.py ergänzt lat/lng
        "contact": contact,
        "last_verified": date.today().isoformat(),
    }
    return result


def load_fixture(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def fetch_url(url: str) -> str:
    try:
        import requests
    except ImportError:
        raise RuntimeError("requests ist nicht installiert. Installiere es mit: pip install requests")
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.text


def main() -> None:
    ap = argparse.ArgumentParser(description="Minimaler Radiologie-Scraper (fixture or url)")
    ap.add_argument("--fixture", help="Path to local HTML fixture")
    ap.add_argument("--url", help="URL to fetch HTML from")
    args = ap.parse_args()

    if not args.fixture and not args.url:
        ap.print_help()
        return

    try:
        html = load_fixture(args.fixture) if args.fixture else fetch_url(args.url)
    except Exception as e:
        print(f"Error loading HTML: {e}", file=sys.stderr)
        sys.exit(1)

    result = extract(html)
    # Wenn keine Radiologie erkannt wurde, geben wir ein leeres Objekt zurück (oder nichts)
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # keine Ausgabe für Nicht-Radiologie; Exit-Code 0
        print("")


if __name__ == "__main__":
    main()
