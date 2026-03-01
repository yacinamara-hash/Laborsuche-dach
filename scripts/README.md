
# Data Processing Scripts – Laborsuche DACH

Dieses Verzeichnis enthält Hilfsskripte zur:

- Geokodierung von Adressen  
- Validierung der JSON‑Datenstruktur  
- Demonstration eines skalierbaren Scraping‑Ansatzes

Diese Tools sind optional, zeigen aber eine skalierbare Architektur.



## Inhaltsverzeichnis

- [Übersicht](#übersicht)
- [Geocoding](#geocoding)
- [Datenvalidierung](#datenvalidierung)
- [Scraping Template](#scraping-template)
- [Docker Setup](#docker-setup)
- [Weiterführende Links](#weiterführende-links)




## Übersicht

| Script | Zweck |
|-:|:--|
| `geocode.py` | Wandelt Adresse → Lat/Lng um |
| `validate.py` | Prüft Struktur & Pflichtfelder in `providers.json` |
| `scrape_template.py` | Beispiel für skalierbares Scraping |



## Geocoding

### Zweck

Adressen aus `providers.json` werden automatisch in Koordinaten (lat/lng) umgewandelt, damit sie auf der Karte angezeigt werden können.

### Wie es funktioniert
Das Skript nutzt den öffentlichen Geocoding‑Dienst Photon (basierend auf OpenStreetMap‑Daten):
- `PHOTON_URL` ist die API‑Adresse, an die die Anfrage geschickt wird.
- `USER_AGENT` identifiziert dein Skript, damit die API die Anfrage nicht blockiert.
Photon durchsucht die OSM‑Datenbank und liefert passende Koordinaten zurück.

### Nutzung

#### Einzeladresse testen:
```bash
python3 scripts/geocode.py "Nordstraße 44, 40477 Düsseldorf, DE"
```

#### Komplette Datei geocoden:

``` bash
python3 scripts/geocode.py --file docker/web/providers.json --out scripts/providers.geocoded.json
```
Ablauf:
- Datei wird geladen
- Anbieter ohne Koordinaten werden ergänzt
- Fehler werden dokumentiert
- Ergebnis wird in einer neuen Datei gespeichert
### Adressanforderungen
Für zuverlässiges Geocoding müssen folgende Felder vorhanden sein:
```json
"address": {
  "street": "Nordstraße 44",
  "zip": "40477",
  "city": "Düsseldorf",
  "country": "DE"
}
Fehlt etwas, kann keine Koordinate erzeugt werden.
```
### Ergebnis
Das Skript nimmt eine Adresse aus deiner `providers.json` und liefert Koordinaten, die später für die Karte gebraucht werden.
Das Endergebnis sieht immer so aus:
```json
"location": {
  "lat": 51.2277,
  "lng": 6.7735
}

```
## Datenvalidierung
### Zweck

Prüft die Struktur und Vollständigkeit der `providers.json`.

Validiert unter anderem:

- Pflichtfelder vorhanden?
- Kategorie gültig?
- Services korrekt gesetzt?
- Website vorhanden?
- Struktur konsistent?


### Nutzung
```bash
python3 scripts/validate.py providers.json
```

Beispielausgabe bei Fehlern:
```bash
FAIL (2 issues):
 - de-muc-dexa: contact.website missing
 - de-haj-labor: address.zip missing
```

Beispiel bei Erfolg:
```bash
OK – no issues found
```
### Geprüfte Pflichtfelder
- id
- region_id
- name
- category
- services
- address.street
- address.zip
- address.city
- location.lat
- location.lng
- last_verified

## Scraping Template
### Zweck

Demonstriert, wie ein skalierbares Scraping-System strukturiert werden kann.

Dieses Script ist ein Architekturbeispiel, kein produktives Scraping-Tool.


### Nutzung mit Test-HTML
```bash 
- python3 scripts/scrape_template.py --fixture scripts/fixtures/sample.html
- python3 scripts/sources/radiologie.py --fixture scripts/fixtures/sample_radiologie.html
```
Beispielausgabe:
```json
{
  "name": "Beispiel Praxis Hannover",
  "services": {
    "dexa_body_composition": true,
    "dexa_bone_density": true,
    "blood_self_pay": false
  }
}
```

### Skalierbarer Ansatz

Empfohlene Architektur bei Erweiterung:

    scripts/
    ├── sources/
    │   ├── radiologie.py
    │   ├── direktlabor.py
    │   ├── orthopaedie.py
    │   └── ...
    ├── geocode.py
    ├── validate.py
    └── scrape_template.py



### Empfohlener Workflow

1. Anbieter manuell recherchieren
2. Adresse vollständig erfassen
3. Geocoding ausführen
4. JSON validieren
5. Map testen

## Docker Setup

Die Anwendung kann optional per Docker gestartet werden.

### Voraussetzungen

- Docker installiert

### Start

Im Projektordner ausführen:

```bash
docker-compose up -d
```
Anschließend im Browser öffnen:
```bash
http://localhost:8000
```
Stoppen
```bash
docker-compose down
```


### Weiterführende Links

- ➡️ [Modulare Scraper](sources/README.md) — Scraper‑Module und Interface.  
- ⬅️ [Zurück zur Hauptdokumentation](../README.md)

