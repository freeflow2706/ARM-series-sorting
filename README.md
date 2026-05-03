# ARM DVD Rip Organizer

Ein Python-Tool zur automatischen Reorganisation und Umbenennung von mit der Automatic Ripping Machine (ARM) gerippten DVD-Serien.

## Features

- ✅ Automatisches Parsing von Ordnernamen mit flexiblen Trennzeichen (Unterstriche, Bindestriche, Leerzeichen)
- ✅ Unterstützung verschiedener Season-Formate (SEASON_5, S5, Season_5, etc.)
- ✅ Automatische Identifikation fehlender Episoden (Main Feature Detection)
- ✅ Disc-übergreifende Episode-Nummerierung
- ✅ Interaktive Fehlerbehandlung bei Parsing-Problemen
- ✅ Detailliertes Logging
- ✅ Verschiebung oder Kopie von Dateien (konfigurierbar)

## Installation

### Voraussetzungen
- Python 3.7+
- pip

### Schritt 1: Dependencies installieren

```bash
pip install -r requirements.txt
```

## Konfiguration

### .env Datei anpassen

Öffne die `.env` Datei und passe folgende Variablen an:

```ini
# Verzeichnis mit den ARM-gerippten DVD-Ordnern (Quelle)
INPUT_DIR=D:\Videos\ARM_Rips

# Zielverzeichnis für reorganisierte Serien
OUTPUT_DIR=D:\Videos\Organized_Series

# Logging Level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# Optionen: move (Standard) oder copy
FILE_OPERATION=move

# Automatisch Quell-Ordner löschen nach Verarbeitung? (True/False)
DELETE_SOURCE_AFTER_MOVE=True
```

## Verwendung

### Skript ausführen

```bash
python run.py
```

Oder direkt:

```bash
python -m src.main
```

## Folder-Struktur

### Input-Verzeichnis (INPUT_DIR)

```
INPUT_DIR/
├── BIG_BANG_THEORY_SEASON_5_DISC_1/
│   ├── BIG_BANG_THEORY_SEASON_5_DISC_1.mp4  (Main Feature)
│   └── extras/
│       ├── B2_t01.mp4
│       ├── B2_t03.mp4  (02 fehlt = Main Feature)
│       └── B2_t04.mp4
├── BIG_BANG_THEORY_SEASON_5_DISC_2/
│   ├── BIG_BANG_THEORY_SEASON_5_DISC_2.mp4
│   └── extras/
│       ├── B2_t01.mp4
│       └── B2_t02.mp4
└── ...
```

### Output-Verzeichnis (OUTPUT_DIR)

```
OUTPUT_DIR/
└── BIG_BANG_THEORY/
    └── Season_05/
        ├── BIG_BANG_THEORY_S05_E01.mp4
        ├── BIG_BANG_THEORY_S05_E02.mp4
        ├── BIG_BANG_THEORY_S05_E03.mp4
        ├── BIG_BANG_THEORY_S05_E04.mp4
        ├── BIG_BANG_THEORY_S05_E05.mp4
        └── BIG_BANG_THEORY_S05_E06.mp4
```

## Parsing-Beispiele

Das Tool erkennt automatisch diese Folder-Name-Formate:

| Format | Erkannt |
|--------|---------|
| `BIG_BANG_THEORY_SEASON_5_DISC_1` | ✅ |
| `BIG-BANG-THEORY-S05-DISC-1` | ✅ |
| `BIG BANG THEORY SEASON 5 DISC 1` | ✅ |
| `big_bang_theory_s5_disc1` | ✅ |
| Ungültiges Format | → Interaktive Eingabe |

## Episode-Dateinamen

Das Tool extrahiert die Episode-Nummer aus den letzten 2 Zeichen vor der `.mp4`-Extension:

| Dateiname | Episode-Nr. |
|-----------|------------|
| `B2_t01.mp4` | 01 |
| `C3_t07.mp4` | 07 |
| `something_99.mp4` | 99 |

## Main-Feature Detection

Das Tool identifiziert automatisch, welche Episode als "Main Feature" in den Parent-Folder verschoben wurde:

**Szenario 1: Lücke in der Sequenz**
```
extras/ enthält: B2_t01.mp4, B2_t03.mp4, B2_t04.mp4
→ Episode 02 fehlt → Main Feature = E02
```

**Szenario 2: Keine Lücke, höchste Nummer ist Main Feature**
```
extras/ enthält: B2_t01.mp4, B2_t02.mp4, B2_t03.mp4
→ Alle vorhanden → Main Feature = E04 (max+1)
```

## Fehlerbehandlung

Bei Problemen werden Sie interaktiv gefragt:

1. **Ungültiger Ordnername**: Eingabe von Series Name, Season, Disc Number
2. **Zieldatei existiert**: Überschreiben, Skip, oder Rename
3. **Episode-Nummer ungültig**: Datei wird übersprungen (mit Warnung)

## Logging

Alle Operationen werden protokolliert:
- **Console-Output**: Live-Fortschritt
- **Log-Datei**: `logs/process_YYYYMMDD_HHMMSS.log` im OUTPUT_DIR

## Beispiel-Workflow

```bash
# 1. .env anpassen mit echten Pfaden
nano .env

# 2. Ordner mit DVD-Rips in INPUT_DIR erstellen
mkdir D:\Videos\ARM_Rips
# ... DVD-Ordner hierein kopieren

# 3. Programm starten
python run.py

# 3a. Bei Parsing-Fehlern: Interaktive Eingabe beantworten
# 3b. Bei Datei-Konflikten: Aktion wählen (o/s/r/a)

# 4. Ergebnis im OUTPUT_DIR überprüfen
# 5. Bei Erfolg: INPUT_DIR leeren (falls DELETE_SOURCE_AFTER_MOVE=True)
```

## Troubleshooting

### "INPUT_DIR does not exist"
→ Pfad in `.env` überprüfen, Ordner erstellen

### "No folders found in INPUT_DIR"
→ DVD-Rip-Ordner in INPUT_DIR kopieren

### "Could not automatically parse folder"
→ Interaktiv angeben (Series Name, Season, Disc Number)

### Dateien nicht verschoben
→ Log-Datei überprüfen, Berechtigungen kontrollieren

## Struktur der Source Files

```
src/
├── __init__.py          # Package Init
├── main.py              # Haupteinstiegspunkt
├── config.py            # Konfigurationsmanagement
├── logger.py            # Logging
├── parser.py            # Parsing von Ordner- und Dateinamen
└── organizer.py         # Dateiverwaltung und Reorganisation
```

## Lizenz

Dieses Tool wird ohne Garantie bereitgestellt.

## Kontakt

Bei Fragen oder Fehlern bitte das Log überprüfen und die Ausgabe studieren.
