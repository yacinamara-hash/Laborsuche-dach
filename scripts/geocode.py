

from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import requests


PHOTON_URL = "https://photon.komoot.io/api/"
USER_AGENT = "LaborsucheDACH/1.0 (yass@example.com)"

@dataclass
class GeocodeResult:
    lat: float
    lng: float
    display_name: str
    importance: float
    osm_type: str
    osm_id: str


def geocode_address(query: str, *, timeout: int = 20) -> GeocodeResult:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    params = {"q": query, "limit": 1}
    r = requests.get(PHOTON_URL, params=params, headers=headers, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    feats = data.get("features", [])
    if not feats:
        raise ValueError(f"No geocoding result for: {query}")

    f = feats[0]
    lng, lat = f["geometry"]["coordinates"]
    props = f.get("properties", {})
    return GeocodeResult(
        lat=float(lat),
        lng=float(lng),
        display_name=str(props.get("name", "")),
        importance=float(props.get("importance", 0.0) or 0.0),
        osm_type=str(props.get("osm_type", "")),
        osm_id=str(props.get("osm_id", "")),
    )


def build_query_from_provider(p: Dict[str, Any]) -> str:
    a = p.get("address") or {}
    parts = [
        a.get("street", ""),
        a.get("zip", ""),
        a.get("city", ""),
        a.get("country", ""),
    ]
    return ", ".join([x for x in parts if x])


def geocode_providers_file(in_path: str, out_path: str, *, sleep_s: float = 1.1) -> None:
    with open(in_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    providers = data.get("providers", [])
    updated = 0
    skipped = 0
    failed = 0

    for p in providers:
        # Skip if already has usable lat/lng
        loc = p.get("location") or {}
        if isinstance(loc.get("lat"), (int, float)) and isinstance(loc.get("lng"), (int, float)):
            skipped += 1
            continue

        q = build_query_from_provider(p)
        if not q:
            failed += 1
            p.setdefault("geocode", {})
            p["geocode"]["error"] = "Missing address fields"
            continue

        try:
            res = geocode_address(q)
            p["location"] = {"lat": res.lat, "lng": res.lng, "accuracy": "street"}
            p.setdefault("geocode", {})
            p["geocode"].update(
                {
                    "query": q,
                    "display_name": res.display_name,
                    "importance": res.importance,
                    "provider": "nominatim",
                    "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }
            )
            updated += 1
        except Exception as e:
            failed += 1
            p.setdefault("geocode", {})
            p["geocode"]["query"] = q
            p["geocode"]["error"] = f"{type(e).__name__}: {e}"

        time.sleep(sleep_s)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Done. updated={updated} skipped={skipped} failed={failed} -> {out_path}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("address", nargs="?", help="Single address string to geocode")
    ap.add_argument("--file", help="Input providers.json to geocode missing locations")
    ap.add_argument("--out", help="Output file (default: providers.geocoded.json)")
    args = ap.parse_args()

    if args.address:
        res = geocode_address(args.address)
        print(f"lat={res.lat} lng={res.lng}")
        print(res.display_name)
        return

    if args.file:
        out = args.out or "providers.geocoded.json"
        geocode_providers_file(args.file, out)
        return

    ap.print_help()


if __name__ == "__main__":
    main()