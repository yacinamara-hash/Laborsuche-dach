
from __future__ import annotations

import argparse
import json
import re
from typing import Any, Dict, List, Tuple


ALLOWED_CATEGORIES = {"DEXA", "BLOOD_LAB"}

REQUIRED_PROVIDER_FIELDS = [
    "id",
    "region_id",
    "name",
    "category",
    "services",
    "self_pay",
    "address",
    "location",
    "contact",
    "last_verified",
    "sources",
]


def is_iso_date(s: str) -> bool:
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", s))


def validate_provider(p: Dict[str, Any], region_ids: set) -> List[str]:
    errs: List[str] = []
    pid = p.get("id", "<missing id>")

   
    for k in REQUIRED_PROVIDER_FIELDS:
        if k not in p:
            errs.append(f"{pid}: missing field '{k}'")

    # category
    cat = p.get("category")
    if cat not in ALLOWED_CATEGORIES:
        errs.append(f"{pid}: category must be one of {sorted(ALLOWED_CATEGORIES)} (got {cat})")

    # region_id 
    rid = p.get("region_id")
    if region_ids and rid not in region_ids:
        errs.append(f"{pid}: region_id '{rid}' not found in regions[]")

    # services 
    services = p.get("services") or {}
    for key in ("dexa_body_composition", "dexa_bone_density", "blood_self_pay"):
        if key not in services:
            errs.append(f"{pid}: services missing '{key}'")
        elif not isinstance(services.get(key), bool):
            errs.append(f"{pid}: services.{key} must be boolean")

    # address
    addr = p.get("address") or {}
    for k in ("street", "zip", "city", "country"):
        if k not in addr or not str(addr.get(k, "")).strip():
            errs.append(f"{pid}: address.{k} missing/empty")

    # location
    loc = p.get("location") or {}
    lat = loc.get("lat")
    lng = loc.get("lng")
    if not isinstance(lat, (int, float)) or not (-90 <= lat <= 90):
        errs.append(f"{pid}: invalid location.lat '{lat}'")
    if not isinstance(lng, (int, float)) or not (-180 <= lng <= 180):
        errs.append(f"{pid}: invalid location.lng '{lng}'")

    # contact
    contact = p.get("contact") or {}
    if not contact.get("phone"):
        errs.append(f"{pid}: contact.phone missing/empty")
    if not contact.get("email"):
        errs.append(f"{pid}: contact.email missing/empty")

    # last_verified
    lv = p.get("last_verified")
    if not isinstance(lv, str) or not is_iso_date(lv):
        errs.append(f"{pid}: last_verified must be YYYY-MM-DD (got {lv})")

    # prices 
    prices = p.get("prices")
    if prices is not None:
        if not isinstance(prices, dict):
            errs.append(f"{pid}: prices must be null or object")
        else:
            ptype = prices.get("type")
            if ptype not in ("range", "from"):
                errs.append(f"{pid}: prices.type must be 'range' or 'from'")
            cur = prices.get("currency")
            if cur not in ("EUR", "CHF", "USD", "GBP") and cur is not None:
                errs.append(f"{pid}: prices.currency looks wrong (got {cur})")
            if not prices.get("source_url"):
                errs.append(f"{pid}: prices.source_url missing/empty")

            if ptype == "range":
                if not isinstance(prices.get("min"), (int, float)) or not isinstance(prices.get("max"), (int, float)):
                    errs.append(f"{pid}: prices.range needs numeric min/max")
            if ptype == "from":
                if not isinstance(prices.get("value"), (int, float)):
                    errs.append(f"{pid}: prices.from needs numeric value")

    # sources
    sources = p.get("sources")
    if not isinstance(sources, list) or not sources:
        errs.append(f"{pid}: sources must be a non-empty list")
    else:
        for i, s in enumerate(sources):
            if not isinstance(s, dict):
                errs.append(f"{pid}: sources[{i}] must be object")
                continue
            if not s.get("type") or not s.get("url"):
                errs.append(f"{pid}: sources[{i}] needs type+url")

    return errs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default="providers.json", help="Path to providers.json")
    args = ap.parse_args()

    with open(args.path, "r", encoding="utf-8") as f:
        data = json.load(f)

    regions = data.get("regions") or []
    region_ids = {r.get("id") for r in regions if isinstance(r, dict) and r.get("id")}

    providers = data.get("providers") or []
    errors: List[str] = []

   
    seen = set()
    for p in providers:
        pid = p.get("id")
        if pid in seen:
            errors.append(f"Duplicate provider id: {pid}")
        seen.add(pid)

    
    for p in providers:
        if not isinstance(p, dict):
            errors.append("Provider entry is not an object")
            continue
        errors.extend(validate_provider(p, region_ids))

    if errors:
        print(f"FAIL ({len(errors)} issues):")
        for e in errors:
            print(" -", e)
        raise SystemExit(1)

    print(f"OK: {len(providers)} providers validated in {args.path}")


if __name__ == "__main__":
    main()