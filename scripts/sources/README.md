

# Sources – Modular Scraping Architecture

Dieses Verzeichnis enthält modulare Scraper‑Module, die HTML‑Seiten einer bestimmten Quelle parsen und standardisierte Datensätze erzeugen.



## Inhaltsverzeichnis

- [Zweck](#zweck)
- [Architekturprinzip](#architekturprinzip)
- [Dateistruktur](#dateistruktur)
- [Interface / Beispiel](#interface--beispiel)
- [Best Practices](#best-practices)
- [Testen und Validieren](#testen-und-validieren)
- [Weiterführende Links](#weiterführende-links)



## Zweck

- Modularisierung von Scraping‑Logik pro Quelltyp  
- Einheitliche Ausgabeformate zur Weiterverarbeitung (`providers.json`‑kompatibel)  
- Erleichterung von Wartung und Erweiterung



## Architekturprinzip

- Jeder Scraper ist eine eigenständige Python‑Datei (z. B. `radiologie.py`)  
- Einheitliche Schnittstelle: `extract(html: str) -> dict`  
- Fehler robust behandeln, keine Seiteneffekte (nur Rückgabewerte)  
- Ausgabe muss `scripts/validate.py` passieren können



## Dateistruktur

    sources/
        ├── radiologie.py
        ├── direktlabor.py
        ├── ...
        └── README.md



## Interface / Beispiel

```python
def extract(html: str) -> dict:
    """
    Erwartet: HTML-String der Quellseite
    Liefert: dict mit mindestens den Feldern:
      - name
      - services
      - address
      - contact (optional)
    """
    return {
        "name": "Beispiel Praxis",
        "services": {
            "dexa_body_composition": True,
            "dexa_bone_density": True,
            "blood_self_pay": False
        },
        "address": {
            "street": "Musterstraße 1",
            "zip": "12345",
            "city": "Musterstadt",
            "country": "DE"
        },
        "contact": {
            "phone": "+49 000 000000",
            "website": "https://example.de"
        }
    }
```

## Best Practices

- Keine harten Abhängigkeiten auf externe Netzwerke in `extract`(für Testbarkeit)
- Klare Fehlercodes / Exceptions definieren
- Einheitliche Feldnamen verwenden
- Unit‑Tests für jede Quelle anlegen (Fixtures)
- Dokumentation pro Scraper (Quelle, letzte Änderung, Besonderheiten)

## Testen und Validieren

- Nutze `scripts/fixtures/*.html` als Test‑Input
- Nach Extraktion: Ausgabe durch `scripts/validate.py` laufen lassen
- Bei Änderungen an der Quelle: Scraper aktualisieren und Tests anpasse



### Weiterführende Links

- ⬅️ [Zurück zurData Processing Scripts](../README.md)
- ⬅️ [Zurück zur Hauptdokumentation](../../README.md)

