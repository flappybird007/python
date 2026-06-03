# 🐍 SLIMY SNAKE - Detaillierte Spielanleitung

Willkommen zu Slimy Snake! Diese Anleitung erklärt alles was du wissen musst um das Spiel zu meistern.

## 📋 Inhaltsverzeichnis

1. [Installation](#installation)
2. [Spiel Starten](#spiel-starten)
3. [Hauptmenü](#hauptmenü)
4. [Einstellungen](#einstellungen)
5. [Grundlagen](#grundlagen)
6. [Steuerung](#steuerung)
7. [Spielmechaniken](#spielmechaniken)
8. [Strategien](#strategien)
9. [Tipps & Tricks](#tipps--tricks)
10. [Häufig gestellte Fragen](#häufig-gestellte-fragen)
11. [Troubleshooting](#troubleshooting)

## 💻 Installation

### Windows

1. **Python installieren:**
   - Besuche [python.org](https://www.python.org/downloads/)
   - Lade Python 3.10+ herunter
   - Während der Installation: **"Add Python to PATH" ankreuzen!**

2. **Repository klonen:**
   - Öffne ein Terminal/CMD im gewünschten Ordner
   ```bash
   git clone https://github.com/flappybird007/python.git
   cd python
   ```

3. **Dependencies installieren:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Spiel starten:**
   - Doppelklick auf `startgame.py` ODER
   - Doppelklick auf `run.bat` ODER
   ```bash
   python snake_game.py
   ```

### Mac / Linux

1. **Python installieren:**
   ```bash
   # macOS mit Homebrew
   brew install python3
   
   # Linux (Debian/Ubuntu)
   sudo apt-get install python3 python3-pip
   ```

2. **Repository klonen:**
   ```bash
   git clone https://github.com/flappybird007/python.git
   cd python
   ```

3. **Dependencies installieren:**
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Spiel starten:**
   - Terminal-Doppelklick auf `startgame.py` ODER
   - Doppelklick auf `run.sh` ODER
   ```bash
   python3 snake_game.py
   ```

## 🎮 Spiel Starten

### Startbildschirm - Hauptmenü

Wenn du das Spiel startest, siehst du den **Hauptmenü-Bildschirm** mit:
- Großem leuchtenden Titel "🐍 SLIMY SNAKE"
- Spielanleitung mit Tipps
- Steuerungshinweise
- Menü-Optionen

**Verfügbare Optionen im Hauptmenü:**
- **SPACE** = Spiel starten
- **S** = Einstellungen öffnen
- **Q** = Spiel beenden

## ⚙️ Einstellungen

### Einstellungs-Bildschirm

Im Hauptmenü drücke **S** um die Einstellungen zu öffnen.

#### KI-Gegner an/aus schalten

**Drücke A** um die KI-Gegner zu togglen:

- **AI ON ✓** - Spiel mit 4 intelligenten KI-Snakes (Standard)
- **AI OFF ✗** - Nur du und Essen (Solo-Modus)

```
┌─────────────────────────┐
│ ⚙️ SETTINGS             │
│                         │
│ AI Opponents: ON ✓      │
│ Press A to toggle       │
│                         │
│ Press R to open README  │
│ Press I to open GUIDE   │
│                         │
│ Press ESC to return     │
└─────────────────────────┘
```

#### Dokumentation öffnen

- **Drücke R** - Öffne README.md (Englische Dokumentation)
- **Drücke I** - Öffne diese ANLEITUNG.md (Deutsche Anleitung)

Die Dateien öffnen sich in deinem Standard-Browser.

## 🎮 Spiel-Flow

### Schritt 1: Username wählen

Wenn du SPACE im Menü drückst:

1. Es erscheint ein Bildschirm "Choose Your Name"
2. Tippe deinen gewünschten Namen (max 15 Zeichen)
3. Dein Name wird live angezeigt mit einem Cursor `_`
4. **Drücke ENTER um fortzufahren**

**Tipps für Usernames:**
- Lustige Namen: "SnakeKing", "PythonMaster", "SnakeEater"
- Kurze Namen
- Keine Sonderzeichen

### Schritt 2: Farbe wählen

1. Es erscheint ein Bildschirm "Choose Your Color"
2. Es werden 8 Farben zur Auswahl angezeigt
3. Verwende **Pfeiltasten ← →** um eine Farbe zu wählen
4. Die ausgewählte Farbe wird größer angezeigt (mit weißem Kreis)
5. **Drücke ENTER um das Spiel zu starten**

**Verfügbare Farben:**
- 🟢 Grün (Classic)
- 🔵 Blau (Cool)
- 🟠 Orange (Warm)
- 🔷 Cyan (Glowing)
- 🟣 Lila (Mystisch)
- 💚 Neon Grün (Bright)
- 💗 Neon Pink (Hot)
- 🟡 Gelb (Sunny)

### Schritt 3: Spielen!

Das Spiel startet mit:
- Deiner farbigen Snake in der Mitte
- 4 KI-Snakes (wenn aktiviert) an zufälligen Orten
- Vielen gelben Essen-Punkten überall
- Leaderboard oben links

## 🎮 Grundlagen

### Das Spielfeld

```
┌─────────────────────────────────────────┐
│ 👤 DeinName: 45        FPS: 60          │
│ LEADERBOARD                             │
│ 🥇 RoboNinja: 78                        │
│ 🥈 DeinName: 75                         │
│ 🥉 ThunderSnake: 62                     │
│ 4. FlameKing: 51                        │
│                                         │
│     🐍 Deine Snake                      │
│     🟡 Essen                            │
│     🤖 KI-Snakes (wenn AN)              │
│                                         │
│ ◄──────────────────────────────────────►│
│ ^                                       ^
│ Rote Grenze (Spielfeld endet hier)      │
└─────────────────────────────────────────┘
```

- **Spielfeld**: 1400 x 900 Pixel
- **Rote Grenzen**: Das Spielfeld endet hier - Snakes bounten ab!
- **Gelbe Punkte**: Essen - iss sie um zu wachsen!
- **Farbige Snakes**: Deine Snake und die KI-Gegner

### Deine Snake

- **Farbe**: Die Farbe die du gewählt hast
- **Kopf**: Heller/leuchtender als der Körper mit Pfeil-Anzeige
- **Nametag**: Dein Name schwebt über deiner Snake
- **Größe**: Wächst mit jedem Essen das du isst
- **Länge**: Deine aktuelle Länge wird oben links angezeigt

### Die KI-Snakes (wenn AN)

- **4 verschiedene Snakes** in verschiedenen Farben
- **Zufällige Namen**: RoboNinja, ThunderSnake, FlameKing, DeathViper, etc.
- **Nametags**: Du siehst ihren Namen über ihrem Kopf
- **Intelligent**: Sie jagen Essen, vermeiden Gegner und navigieren strategisch
- **Variable Größe**: Jede KI-Snake hat eine andere Startgröße

## 🕹️ Steuerung

### Hauptsteuerung - Mauszeiger

| Aktion | Effekt |
|--------|--------|
| **🖱️ Maus bewegen** | Deine Snake folgt der Maus in **360°** |
| **Halte Maus ruhig** | Snake bewegt sich kontrolliert |
| **Schnelle Mausbewegung** | Snake dreht schnell |

**Wichtig:** Die Maus-Steuerung ist die Hauptsteuerung! Halte deine Maus über dem Spielfenster.

### Spiel-Tasten

| Taste | Aktion | Wann |
|-------|--------|------|
| **ESC** | Spiel pausieren / fortsetzen | Während des Spiels |
| **M** | Zurück zum Menü | Im Pause-Screen |

### Im Hauptmenü

| Taste | Aktion |
|-------|--------|
| **SPACE** | Spiel starten |
| **S** | Einstellungen öffnen |
| **Q** | Spiel beenden |

### In Einstellungen

| Taste | Aktion |
|-------|--------|
| **A** | KI an/aus schalten |
| **R** | README öffnen |
| **I** | Diese ANLEITUNG öffnen |
| **ESC** | Zurück zum Menü |

### Im Username-Screen

| Taste | Aktion |
|-------|--------|
| **Schreiben** | Buchstaben eingeben |
| **BACKSPACE** | Letzten Buchstaben löschen |
| **ENTER** | Zur Farb-Auswahl gehen |

### Im Farb-Auswahl-Screen

| Taste | Aktion |
|-------|--------|
| **← / A** | Eine Farbe nach links |
| **→ / D** | Eine Farbe nach rechts |
| **ENTER / SPACE** | Farbe bestätigen und spielen |

### Nach dem Tod

| Taste | Aktion |
|-------|--------|
| **SPACE** | Nochmal spielen |
| **M** | Zurück zum Menü |

## 🎮 Spielmechaniken

### Essen - Wachsen

```
🟡 = 1 Essen-Punkt
    ↓
🐍 wächst um 2 Segmente
    ↓
🐍 wird länger und stärker
```

- **Gelbe Punkte** sind Essen
- Wenn dein **Kopf** ein Essen berührt → **+2 Länge**
- Essen wird automatisch an zufälligen Orten respawnt
- **Mehr Essen** = **Längere Snake** = **Stärker**

### Kollisionen

#### ✅ Das passiert NICHT (Du stirbst NICHT):
- Deine Snake stößt gegen die Map-Grenzen → **Bounce ab** (nicht sterben!)
- Dein Körper berührt sich selbst → **Nichts passiert** (nicht gleich sterben!)
- Dein Körper berührt andere Snakes → **Nichts passiert** (nicht sterben!)
- Du berührst andere Snakes → **Nur wenn Kopf-zu-Körper!**

#### ❌ Das führt zum TOD:
- **Kopf-zu-Körper**: Dein Kopf berührt den Körper einer anderen Snake ☠️
- **Kopf-zu-Kopf**: Dein Kopf berührt den Kopf einer anderen Snake ☠️
- **Selbst-Kollision**: Dein Kopf berührt dein eigenes Körper-Segment (sehr schwer) ☠️

### Spawnschutz

- **KI-Snakes spawnen NICHT** in deiner Nähe zu Spielstart
- Es gibt einen **Sicherheitsradius** (200 Pixel) um deine Startposition
- Du kannst **nicht plötzlich einfach so sterben**
- KI-Snakes spawnen an sicheren Orten

### Leaderboard

Das Leaderboard wird **oben links** in Echtzeit angezeigt:

```
👤 DeinName: 45
🥇 RoboNinja: 78      ← 1. Platz (längste Snake)
🥈 ThunderSnake: 62   ← 2. Platz (Silber)
🥉 FlameKing: 51      ← 3. Platz (Bronze)
4. DeathViper: 38     ← 4. Platz
```

- **🥇 Gold**: #1 Spieler (längste Snake)
- **🥈 Silber**: #2 Spieler
- **🥉 Bronze**: #3 Spieler
- **Zahlen**: Platz 4 und danach

**Das Leaderboard updatet in Echtzeit!**

## 📊 Statistiken - Speicherung

Deine Spiel-Statistiken werden **automatisch gespeichert** in:

- **Windows**: `C:\Users\[DeinName]\.slimy_snake_stats.json`
- **Mac/Linux**: `~/.slimy_snake_stats.json`

Gespeicherte Daten:
- Gesamte Spiele gespielt
- Höchster Score (Länge)
- Insgesamt Essen gegessen
- Dein bester Spieler-Name
- Spielhistorie mit Timestamps

Du kannst die Datei öffnen um deine Fortschritte zu sehen!

## 🎯 Strategien

### Einsteigers-Strategie (mit KI)

1. **Sammle Essen**: Fokussiere dich auf die gelben Punkte in der Nähe
2. **Weiche KI aus**: Halte Abstand zu den farbigen Snakes
3. **Benutze Platz**: Nutze das ganze Spielfeld, nicht nur die Mitte
4. **Wachse kontinuierlich**: Je länger du bist, desto schwerer bist du zu treffen
5. **Nutze Grenzen**: Die roten Grenzen sind deine Freunde

### Fortgeschrittene-Strategie (mit KI)

1. **Positioniere dich strategisch**: Versuche KI-Snakes zu "blocken" (ihnen den Weg abschneiden)
2. **Benutze deine Länge**: Eine lange Snake braucht Zeit zum Wenden - nutze das!
3. **Beobachte KI-Muster**: Die KI hat Verhaltens-Muster - lerne sie!
4. **Lenke Gegner**: Wenn eine KI dich jagt, führe sie zu anderem Essen weg
5. **Grenze-Navigation**: Nutze die Ecken - KI hat dort Schwierigkeiten

### Solo-Strategie (ohne KI)

1. **Entspannen**: Keine Bedrohung - genieße das Spiel
2. **Persönliche Rekorde**: Versuche deine eigenen High-Scores zu schlagen
3. **Freeplay**: Experimentiere mit verschiedenen Taktiken
4. **Essen sammeln**: Maximal Punkte sammeln ohne Druck

### Snake-Längen-Vergleich

```
0-5:   🐍 Anfänger (Anfällig)
5-15:  🐍🐍 Mittelmäßig (Halbwegs sicher)
15-30: 🐍🐍🐍 Stark (Schwer zu treffen)
30+:   🐍🐍🐍🐍 Meister (König des Spiels)
```

## 📝 Tipps & Tricks

### 🎮 Steuerungs-Tipps

- **Halte die Maus ruhig**: Schnelle Mausbewegungen = schnelle Snake-Drehungen
- **Voraus denken**: Wende VORHER ab, nicht NACHDEM du das Essen gesehen hast
- **Maus-Beschleunigung nutzen**: Für schnelle Kurven schnell die Maus bewegen
- **Maus zentriert halten**: Bewege die Maus nicht zu schnell über den Rand

### 🏆 Spiel-Tipps (mit KI)

- **Gegner vermeiden**: Vermeide die KI-Snakes wenn möglich
- **Grenze nutzen**: Die Spielfeld-Grenzen sind deine Freunde
- **Länge aufbauen**: Investiere in Längenwachstum, nicht in Risiken
- **Beobachte das Leaderboard**: Sehe wem es schlecht geht und wem gut
- **Größer = sicherer**: Mit 30+ Länge sind die meisten KI-Snakes kleiner

### 💡 Leben-Retter-Tipps

- **Schnelle Kurven**: Bewege die Maus schnell für scharfe Kurven
- **In Ecken gehen**: KI hat Probleme mit Ecken und Kanten
- **Länge als Schild**: Mit 30+ Länge sind viele KI-Snakes kleiner als du
- **Geduld**: Manchmal ist das beste, nichts zu tun und auf Essen zu warten
- **Beobachte andere**: Beobachte wie KI-Snakes sich verhalten

## ❓ Häufig Gestellte Fragen

### F: Meine Snake bewegt sich nicht!
**A:** Stelle sicher dass:
- Das Spielfenster aktiv ist (klicke darauf)
- Deine Maus über dem Spielfeld ist
- Das Spiel nicht pausiert ist (ESC gedrückt?)

### F: Die KI ist zu stark!
**A:** Das ist absicht! Tipps:
- Werde größer bevor du kämpfst (mindestens 15 Länge)
- Weiche aus statt zu kämpfen
- Nutze die Spielfeld-Grenzen
- Drücke A in Einstellungen um KI ausschalten zu können

### F: Kann ich die KI ausschalten?
**A:** **Ja!** Im Hauptmenü:
1. Drücke **S** für Einstellungen
2. Drücke **A** um KI aus zu schalten
3. Drücke **ESC** zum Zurück
4. Drücke **SPACE** zum Spielen ohne KI

### F: Warum bin ich plötzlich gestorben?
**A:** Mögliche Gründe:
- Dein Kopf hat einen KI-Körper getroffen
- Du bist in eine Ecke gerannt und eine KI hat dich erwischt
- Head-to-Head Kollision mit KI
- Selbst-Kollision (Kopf trifft eigenen Körper)

### F: Wie viele KI-Snakes gibt es?
**A:** **4 KI-Snakes** (wenn AN) mit zufälligen Namen. Sie haben alle unterschiedliche Strategien.

### F: Wo werden meine Stats gespeichert?
**A:** In deinem Home-Verzeichnis:
- **Windows**: `C:\Users\[DeinName]\.slimy_snake_stats.json`
- **Mac/Linux**: `~/.slimy_snake_stats.json`

Du kannst die Datei in einem Text-Editor öffnen um deine Statistiken zu sehen.

### F: Kann ich die Schwierigkeit ändern?
**A:** Ja, mehrere Optionen:
- **Einfach**: KI ausschalten (Drücke A in Einstellungen)
- **Edit Code**: In `snake_game.py` den Wert `threat_distance` ändern (größer = schwächer KI)

### F: Kann ich Sound einschalten?
**A:** Das Sound-System ist vorbereitet. Wenn du Sound-Dateien hast:
1. Erstelle einen `assets/` Ordner
2. Füge Sound-Dateien hinzu:
   - `eat.wav` - Ess-Sound
   - `death.wav` - Tod-Sound
   - `music.mp3` oder `music.wav` - Hintergrund-Musik

## 🔧 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'pygame'"

**Lösung:**
```bash
pip install pygame
```

Oder für Mac/Linux:
```bash
pip3 install pygame
```

### Problem: Spiel läuft sehr langsam (unter 30 FPS)

**Lösung:**
1. Schließe andere Anwendungen
2. Reduziere die Fenster-Größe:
   - Öffne `snake_game.py` in einem Editor
   - Ändere die ersten Konstanten:
   ```python
   WINDOW_WIDTH = 1000   # War 1400
   WINDOW_HEIGHT = 700   # War 900
   ```
3. Stelle sicher dass Grafiktreiber aktuell sind

### Problem: Maussteuerung funktioniert nicht

**Lösung:**
1. Stelle sicher dass das Spielfenster aktiv ist (klicke darauf)
2. Bewege die Maus über dem Spielfeld
3. Versuche die Maus schneller zu bewegen
4. Starte das Spiel neu

### Problem: Spiel stürzt ab beim Start

**Lösung:**
1. Stelle sicher dass du Python 3.7+ hast: `python --version`
2. Installiere requirements neu:
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```
3. Versuche:
   ```bash
   python -m pip install --upgrade pip
   ```

### Problem: Fenster öffnet sich aber bleibt schwarz

**Lösung:**
1. Warte 5-10 Sekunden (Initialisierung)
2. Bewege die Maus im Fenster
3. Drücke eine Taste (SPACE)
4. Wenn nichts hilft, neustarten

### Problem: "Permission denied" beim Starten

**Windows**: Rechtsklick auf `startgame.py` → "Run with Python"

**Mac/Linux**: 
```bash
chmod +x startgame.py
./startgame.py
```

## 🎉 Erfolgs-Tricks zum Gewinnen

1. **Starte klein aber sicher**: Konzentriere dich auf Essen in der Nähe
2. **Wachse kontinuierlich**: Nicht riskieren, sondern sicher wachsen
3. **Beobachte andere**: Schau was die KI macht und lerne
4. **Nutze Grenzen**: Die Map-Grenzen sind deine besten Freunde
5. **Geduld**: Langsamkeit gewinnt - überstürze nichts
6. **Kenne die Taktiken**: Jede KI-Snake hat ein Muster
7. **Lerne aus Fehlern**: Jeder Tod ist eine Lektion

## 📚 Weitere Ressourcen

- **README.md** - Technische Details und allgemeine Info
- **snake_game.py** - Der Quellcode mit allen Kommentaren
- **GitHub Issues** - Für Bugs und Feature-Requests

## 🎮 Neue Features in diesem Update

✅ **Hauptmenü-System** - Starte mit dem Menü, nicht direkt im Spiel  
✅ **Einstellungs-Screen** - Toggle KI-Gegner und öffne Dokumentation  
✅ **KI an/aus** - Spielbare ein und ausschalten  
✅ **Statistik-Speicherung** - Deine Scores werden automatisch gespeichert  
✅ **Dokumentation-Viewer** - Öffne README und ANLEITUNG aus dem Spiel  
✅ **Code-Kommentare** - Der ganze Code ist ausführlich kommentiert  

---

**Viel Spaß und viel Glück! 🐍🏆**

---

**Noch Fragen?** Erstelle einen [GitHub Issue](https://github.com/flappybird007/python/issues)!
