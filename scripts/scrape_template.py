from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from bs4 import BeautifulSoup

USER_AGENT = "LaborsucheDACH/1.0 (yass@example.com)"


def extract_provider_from_html(html: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)


    name = (soup.find("h1") or soup.title or {}).get_text(strip=True) if (soup.find("h1") or soup.title) else "Unknown"

    def has_any(*needles: str) -> bool:
        t = text.lower()
        return any(n.lower() in t for n in needles)

    services = {
        "dexa_body_composition": has_any("body composition", "körperzusammensetzung", "viszeral"),
        "dexa_bone_density": has_any("knochendichte", "bone density", "osteodensitometrie", "dexa"),
        "blood_self_pay": has_any("selbstzahler", "ohne überweisung", "direkt beauftragen", "laborambulanz"),
    }

    return {"name": name, "services": services}


def load_fixture(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def fetch_url(url: str, timeout: int = 20) -> str:
    r = requests.get(url, headers = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json",
    "Referer": "http://localhost"
}, timeout=timeout)
    r.raise_for_status()
    return r.text


def main() -> None:
    ap = argparse.ArgumentParser(description="Generic scraper runner (fixture or url)") 
    ap.add_argument("--fixture", help="Path to local HTML fixture") 
    ap.add_argument("--url", help="URL to fetch HTML from") 
    args = ap.parse_args()
    
    args = ap.parse_args()

    if not args.fixture and not args.url:
        ap.print_help()
        return

    html = load_fixture(args.fixture) if args.fixture else fetch_url(args.url)
    result = extract_provider_from_html(html)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()