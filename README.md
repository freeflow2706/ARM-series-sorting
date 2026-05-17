# ARM DVD Rip Organizer

Ein Python-Tool zur automatischen Reorganisation und Umbenennung von mit der Automatic Ripping Machine (ARM) gerippten DVD-Serien.

## Features

- ✅ Automatisches Parsing von Ordnernamen mit flexiblen Trennzeichen (Unterstriche, Bindestriche, Leerzeichen)
- ✅ Unterstützung verschiedener Season-Formate (SEASON_5, S5, Season_5, S5D1, D1 etc.)
- ✅ **E00 (Title Track) Handling** - Automatische Erkennung und Renummerierung
- ✅ **Finale Episodennummern starten immer bei E01** - auch wenn lokal mit E00 begonnen wird
- ✅ Automatische Identifikation fehlender Episoden (Main Feature Detection)
- ✅ **Flexible Main-Feature Platzierung** - Konfigurierbar als erste (E00) oder letzte Episode
- ✅ **Extras-Ordner optional** - Unterstützung für Single-Episode-Discs ohne Extras-Ordner
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

# Platzierung des Main Features, wenn E00 fehlt: first_episode oder last_episode
# first_episode: Main Feature wird als E00 vor alle anderen Episoden gesetzt
#                (für Serien mit vollständigem Titel-Track der von ARM übersprungen wurde)
# last_episode: Main Feature wird nach allen anderen Episoden als höchste Zahl gesetzt (Standard)
#               (für Serien ohne vollständigen Titel-Track oder einzelne Episoden)
MAINFEATURE_PLACEMENT=last_episode
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

| Format | Pattern | Erkannt |
|--------|---------|---------|
| `BIG_BANG_THEORY_SEASON_5_DISC_1` | SEASON/DISC Keywords | ✅ |
| `BIG-BANG-THEORY-S05-DISC-1` | SEASON/DISC Keywords | ✅ |
| `BIG BANG THEORY SEASON 5 DISC 1` | SEASON/DISC Keywords | ✅ |
| `big_bang_theory_s5_disc1` | SEASON/DISC Keywords | ✅ |
| `SHOW_S5D1` | S/D Shorthand | ✅ |
| `SHOW_S5-D1` | S/D Shorthand | ✅ |
| `SHOW_D2` | Nur D (Season optional) | ✅ |
| `SHOW_5_1` | Generische Zahlen | ✅ |
| Ungültiges Format | - | → Interaktive Eingabe |

## Episode-Dateinamen

Das Tool extrahiert die Episode-Nummer aus den letzten 2 Zeichen vor der `.mp4`-Extension:

| Dateiname | Episode-Nr. |
|-----------|------------|
| `B2_t00.mp4` | 00 (Title Track) |
| `B2_t01.mp4` | 01 |
| `C3_t07.mp4` | 07 |
| `something_99.mp4` | 99 |

**Episode 00 - Title Track (Spezialfall)**

Auf manchen DVDs ist Episode 00 der "Title Track" - eine Intro/Menü-Episode, die vor den eigentlichen Episoden abgespielt wird:

| Szenario | Input | Output |
|----------|-------|--------|
| Mit E00 | `B2_t00.mp4, B2_t01.mp4, B2_t02.mp4` | `S01_E01.mp4, S01_E02.mp4, S01_E03.mp4` |
| Ohne E00 | `B2_t01.mp4, B2_t02.mp4, B2_t03.mp4` | `S01_E01.mp4, S01_E02.mp4, S01_E03.mp4` |

**Wichtig:** Das finale Ergebnis startet **IMMER mit E01** (erste Episode der Staffel), egal ob der eingelesene Titel mit E00 oder E01 beginnt.

## Main-Feature Detection

Das Tool identifiziert automatisch, welche Episode als "Main Feature" in den Parent-Folder verschoben wurde:

**Szenario 1: Title Track vorhanden (E00), keine Lücke in E01+**
```
extras/ enthält: B2_t00.mp4, B2_t01.mp4, B2_t02.mp4
→ E00 erkannt (Title Track) → Keine fehlende Episode in E01-E02
→ Main Feature = E04 (max(E01-E02) + 1, mit +1 E00-Offset)
```

**Szenario 2: Lücke in der Sequenz (keine E00)**
```
extras/ enthält: B2_t01.mp4, B2_t03.mp4, B2_t04.mp4
→ E00 nicht vorhanden → Episode 02 fehlt → Main Feature = E02
```

**Szenario 3: Keine Lücke, höchste Nummer ist Main Feature (keine E00)**
```
extras/ enthält: B2_t01.mp4, B2_t02.mp4, B2_t03.mp4
→ E00 nicht vorhanden → Alle vorhanden → Platzierung abhängig von MAINFEATURE_PLACEMENT:
  • first_episode: Main Feature = E00
  • last_episode: Main Feature = E04 (max+1)
```

**Szenario 4: Title Track + Lücke in E01+ (Edge-Case) ⚠️**
```
extras/ enthält: B1_t00.mp4, B1_t01.mp4, ..., B1_t09.mp4
→ E00 erkannt (Title Track) → Lücke bei E10 in der Sequenz
→ Main Feature = E10 (erste fehlende Episode + E00-Offset wird automatisch berücksichtigt)
```

**Szenario 5: NUR E00 in extras (kritischer Edge-Case) 🔴**
```
extras/ enthält: B3_t00.mp4
→ E00 erkannt (Title Track) → Keine weiteren Episodes
→ Main Feature = E01 (erste Episode nach Title Track)
→ Output: E00→E01, MainFeature→E02
```

**Szenario 6: Kein extras Ordner vorhanden (Single Episode) ✅ NEU**
```
Ordner: SHOW_SEASON_3_DISC_1/
  ├── SHOW_SEASON_3_DISC_1.mp4  (Main Feature)
  └── (kein extras/ Ordner)
→ extras/ nicht gefunden → Main Feature wird als E01 verwendet
→ Output: SHOW_S03_E01.mp4
```

### MAINFEATURE_PLACEMENT Konfiguration

Die neue `MAINFEATURE_PLACEMENT` Option steuert das Verhalten, wenn:
- Der extras-Ordner existiert
- E00 fehlt in den extras
- Keine Lücke in den Episodennummern vorhanden ist

**Zwei Optionen:**

| Option | Verhalten | Beispiel | Geeignet für |
|--------|-----------|---------|---|
| `first_episode` | Main Feature wird **vor** alle Episoden als E00 platziert | extras: E01,E02,E03 → Output: E00,E01,E02,E03 | Serien mit vollständigem Titel-Track (komplette Intro) |
| `last_episode` | Main Feature wird **nach** allen Episoden als höchste Nummer platziert | extras: E01,E02,E03 → Output: E01,E02,E03,E04 | Serien ohne Titel-Track oder Standard-DVDs |

## Fehlerbehandlung

Bei Problemen werden Sie interaktiv gefragt:

1. **Ungültiger Ordnername**: Eingabe von Series Name, Season, Disc Number
2. **Zieldatei existiert**: Überschreiben, Skip, oder Rename
3. **Episode-Nummer ungültig**: Datei wird übersprungen (mit Warnung)

### Bekannte Edge-Cases und ihre Lösung

**E00 mit Lücke in E01+**

In seltenen Fällen kann eine DVD einen Title Track (E00) UND eine Lücke in den Episoden haben:
- Eingabe: `B1_t00.mp4, B1_t01-t09.mp4` (E10 fehlt)
- Früher: ❌ Bug - E10 wurde übersehen
- Jetzt: ✅ Korrekt - E10 wird als Main Feature erkannt

Dies wird durch die `HOUSE` Test-Show überprüft.

**NUR E00 in extras (kritisch)**

Falls ein Disc nur den Title Track enthält:
- Eingabe: `B3_t00.mp4` (nur Title Track, keine Episodes)
- Früher: ❌ Bug - Main Feature wurde ignoriert
- Jetzt: ✅ Korrekt - Main Feature wird E01 zugeordnet

Dies wird durch die `BREAKING_BAD Season 6 Disc 3` Test-Show überprüft.

**Kein extras Ordner vorhanden (Single Episode)**

Falls auf einer Disc kein extras-Ordner vorhanden ist (z.B. bei DVDs mit nur einer gerippten Folge):
- Eingabe: `SHOW_SEASON_3_DISC_1/` mit nur `SHOW_SEASON_3_DISC_1.mp4` im Root
- Früher: ⚠️ Warnung - "extras folder not found"
- Jetzt: ✅ Korrekt - Main Feature wird als E01 erkannt und verwendet

Dies ist nützlich für DVD-Box-Sets, bei denen manche Discs nur eine einzelne Episode enthalten.

**Main Feature Platzierung ohne E00**

Wenn E00 fehlt und keine Lücken vorhanden sind, hängt die Platzierung vom `MAINFEATURE_PLACEMENT` Setting ab:
- `first_episode`: Main Feature wird E00 (nur wenn konfiguriert)
- `last_episode`: Main Feature wird höchste Nummer (Standard)

Dies ist nützlich um zwischen Serien mit vollständigem Titel-Track (der von ARM übersprungen wurde) und Standard-DVDs zu unterscheiden.

## Testing

Für Tests ohne echte Videodateien stehen zwei Hilfsskripte zur Verfügung:

### Test-Struktur erstellen mit `.txt` Dateien

Erzeugt realistische Teststrukturen mit verschiedenen Formaten und Edge-Cases (inklusive E00-Handling):

```bash
python test/create_test_structure.py
```

Dies erstellt `test/test_input/` mit mehreren Test-Shows:
- **BIG_BANG_THEORY**: Klassisches Format mit SEASON/DISC Keywords
- **BREAKING_BAD**: Shorthand Format (S4_DISC)
- **HOUSE**: Mit E00 (Title Track) + Gap - `S3D1` Format
- **THE_OFFICE**: Alternative Formate `Season_2-D1`
- **BREAKING_BAD S06**: Kritischer Edge-Case: Nur E00 in extras - `Season_6_Disc_3` Format

### Mock-Struktur aus bestehendem Verzeichnis

Falls du bereits DVD-Rips hast, kannst du eine Mock-Struktur aus echten Dateien erstellen:

```bash
python test/create_mock_structure.py <quelle> <ziel>
```

**Beispiel:**
```bash
python test/create_mock_structure.py "Y:\unidentified" "test/test_mock"
```

Dies kopiert die **gesamte Ordnerstruktur** und konvertiert alle Dateien zu leeren `.txt` Dateien. So kannst du das Parsing und die Reorganisation testen, ohne große Mediendateien zu verschieben.

### Workflow für lokale Tests

```bash
# 1. Test-Struktur erstellen
python test/create_test_structure.py

# 2. .env für Test anpassen
# INPUT_DIR=test/test_input
# OUTPUT_DIR=test/test_output

# 3. Programm testen
python run.py

# 4. Ergebnis überprüfen
# → test/test_output/ sollte reorganisierte Struktur enthalten

# 5. Struktur verifizieren (falls Script vorhanden)
# python test/verify_output.py
```

### Test-Shows und ihre Zwecke

| Show | Besonderheit | Testet |
|------|---|---|
| BIG_BANG_THEORY | Gap + Multiple Discs | Basis-Funktionalität, Disc-Übergänge |
| BREAKING_BAD S04 | 3 Discs, Gap in Disc 2 | Multi-Disc-Handling mit Lücken |
| HOUSE | E00 Title Track + Gap | E00-Erkennung, Renummerierung, Gap-Erkennung mit E00 |
| THE_OFFICE | Alternative Ordnernamen | Flexible Regex-Parsing |
| **BREAKING_BAD S06** | **NUR E00 in extras** | **Kritischer Bug-Fix: Main Feature wenn nur Title Track vorhanden** |

## Logging

Alle Operationen werden protokolliert:
- **Console-Output**: Live-Fortschritt
- **Log-Datei**: `logs/process_YYYYMMDD_HHMMSS.log` im OUTPUT_DIR

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
