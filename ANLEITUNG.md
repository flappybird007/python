# 🐍 SLIMY SNAKE - Detaillierte Spielanleitung

Willkommen zu Slimy Snake! Diese Anleitung erklärt alles was du wissen musst um das Spiel zu meistern.

## 📋 Inhaltsverzeichnis

1. [Installation](#installation)
2. [Spiel Starten](#spiel-starten)
3. [Grundlagen](#grundlagen)
4. [Steuerung](#steuerung)
5. [Spielmechaniken](#spielmechaniken)
6. [Strategien](#strategien)
7. [Tipps & Tricks](#tipps--tricks)
8. [Häufig gestellte Fragen](#häufig-gestellte-fragen)
9. [Troubleshooting](#troubleshooting)

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
   - Terminal-Doppelklick auf `run.sh` ODER
   ```bash
   python3 snake_game.py
   ```

## 🎮 Spiel Starten

### Startbildschirm

Wenn du das Spiel startest, siehst du den **Hauptmenü-Bildschirm** mit:
- Großem Titel "🐍 SLIMY SNAKE"
- Spielanleitung
- Steuerungshinweise

**Drücke SPACE um fortzufahren!**

### Schritt 1: Username wählen

![Username Screen]

1. Es erscheint ein Bildschirm "Choose Your Name"
2. Tippe deinen gewünschten Namen (max 15 Zeichen)
3. Dein Name wird live angezeigt mit einem Cursor `_`
4. **Drücke ENTER um fortzufahren**

**Tipps für Usernames:**
- Lustige Namen: "SnakeKing", "PytonMaster", "SnakeEater"
- Kurze Namen laden schneller
- Keine Sonderzeichen

### Schritt 2: Farbe wählen

![Color Select Screen]

1. Es erscheint ein Bildschirm "Choose Your Color"
2. Es werden 8 Farben zur Auswahl angezeigt
3. Verwende **Pfeiltasten ← →** um eine Farbe zu wählen
4. Die ausgewählte Farbe wird größer angezeigt (mit weißem Kreis)
5. **Drücke ENTER um das Spiel zu starten**

**Verfügbare Farben:**
- 🟢 Grün (Classic)
- 🔵 Blau (Cool)
- 🟠 Orange (Warm)
- 🔵 Cyan (Glowing)
- 🟣 Lila (Mystisch)
- 💚 Neon Grün (Bright)
- 💗 Neon Pink (Hot)
- 🟡 Gelb (Sunny)

## 🎮 Grundlagen

### Das Spielfeld

```
┌─────────────────────────────────────────┐
│                                         │
│  🐍 Deine Snake        🤖 KI-Snakes    │
│  🟡 Essen              📊 Leaderboard  │
│                                         │
└─────────────────────────────────────────┘
```

- **Spielfeld**: 1400 x 900 Pixel
- **Rote Grenzen**: Das Spielfeld endet hier (nicht unendlich!)
- **Gelbe Punkte**: Essen - iss sie um zu wachsen!
- **Farbige Snakes**: Deine Snake und die KI-Gegner

### Deine Snake

- **Farbe**: Die Farbe die du gewählt hast
- **Kopf**: Hellere/leuchtendere Kopffarbe als der Körper
- **Nametag**: Dein Name schwebt über deiner Snake
- **Größe**: Wächst mit jedem Essen das du isst

### Die KI-Snakes

- **4 verschiedene Snakes** in verschiedenen Farben
- **Zufällige witzige Namen** wie: RoboNinja, ThunderSnake, FlameKing, etc.
- **Nametags**: Du siehst immer ihren Namen über ihrem Kopf
- **Intelligent**: Sie jagen Essen, vermeiden Gegner und verstecken sich

## 🕹️ Steuerung

### Bewegung

| Eingabe | Effekt |
|---------|--------|
| **🖱️ Mauszeiger** | Deine Snake folgt der Maus in **360°** |
| **Maus bewegen** | Snake dreht sich kontinuierlich nach Maus |

**Wichtig:** Die Maus-Steuerung ist die Hauptsteuerung! Halte deine Maus im Spielfenster.

### Tasten-Steuerung

| Taste | Aktion |
|-------|--------|
| **ESC** | Spiel pausieren / fortsetzen |
| **M** | Zurück zum Menü (nur im Pause-Screen) |
| **SPACE** | Nochmal spielen (nur nach Tod) |
| **Q** | Spiel beenden (nur im Menü) |

### Im Farb-Auswahl-Screen

| Taste | Aktion |
|-------|--------|
| **← / A** | Eine Farbe nach links |
| **→ / D** | Eine Farbe nach rechts |
| **ENTER / SPACE** | Farbe bestätigen und spielen |

## 🎮 Spielmechaniken

### Essen

```
🟡 = 1 Essen
↓
🐍 wächst um 2 Segmente
↓
🐍 wird länger und stärker
```

- **Gelbe Punkte** sind Essen
- Wenn deine **Kopf** ein Essen berührt → **+2 Länge**
- Essen wird automatisch an zufälligen Orten respawnt
- **Mehr Essen** = **Längere Snake** = **Stärker**

### Kollisionen

#### ✅ Das passiert NICHT:
- Deine Snake stirbt NICHT wenn sie gegen die Map-Grenzen stößt
- Deine Snake stirbt NICHT wenn dein Körper sich selbst berührt
- Deine Snake stirbt NICHT wenn du eine andere Snake berührst UND nicht mit dem Kopf

#### ❌ Das führt zum TOD:
- **Kopf-zu-Körper**: Dein Kopf berührt den Körper einer anderen Snake
- **Kopf-zu-Kopf**: Dein Kopf berührt den Kopf einer anderen Snake
- **Selbst-Kollision**: Dein Kopf berührt dein eigenes Schlangen-Körper (sehr schwer)

### Spawnschutz

- **KI-Snakes spawnen NICHT** in deiner Nähe
- Es gibt einen **Sicherheitsradius** um deine Startposition
- Du kannst **nicht plötzlich einfach so sterben**
- Wenn eine KI-Snake nahe deinem Spawn wäre, spawnt sie woanders

### Leaderboard

Das Leaderboard wird **oben links** angezeigt:

```
👤 DeinName: 45
🥇 RoboNinja: 78
🥈 ThunderSnake: 62
🥉 FlameKing: 51
4. DeathViper: 38
```

- **🥇 Gold**: #1 Spieler (längste Snake)
- **🥈 Silber**: #2 Spieler
- **🥉 Bronze**: #3 Spieler
- **Zahlen**: Platz 4 und danach

**Das Leaderboard updatet in Echtzeit!**

## 🎯 Strategien

### Einsteigers-Strategie

1. **Sammle Essen**: Fokussiere dich auf die gelben Punkte in der Nähe
2. **Weiche KI aus**: Halte Abstand zu den farbigen Snakes
3. **Benutze Platz**: Nutze das ganze Spielfeld, nicht nur die Mitte
4. **Wachse kontinuierlich**: Je länger du bist, desto schwerer bist du zu treffen

### Fortgeschrittene-Strategie

1. **Positioniere dich strategisch**: Versuche KI-Snakes zu "blocken" (ihnen den Weg abschneiden)
2. **Benutze deine Länge**: Eine lange Snake braucht Zeit zum Wenden - nutze das!
3. **Beobachte KI-Muster**: Die KI hat Verhaltens-Muster - lerne sie!
4. **Lenke Gegner**: Wenn eine KI dich jagt, führe sie zu anderem Essen weg

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

### 🏆 Spiel-Tipps

- **Medien vermeiden**: Vermeide die 4 KI-Snakes wenn möglich
- **Grenze nutzen**: Die Spielfeld-Grenzen sind deine Freunde - Gegner können nicht folgen
- **Länge aufbauen**: Investiere in Längenwachstum, nicht in Risiken
- **Beobachte das Leaderboard**: Sehe wem es schlecht geht und wem gut

### 💡 Leben-Retter-Tipps

- **Schnelle Kurven**: Bewege die Maus schnell für scharfe Kurven
- **In Ecken gehen**: KI hat Probleme mit Ecken
- **Länge als Schild**: Mit 30+ Länge sind viele KI-Snakes kleiner als du
- **Geduld**: Manchmal ist das beste, nichts zu tun und auf Essen zu warten

## ❓ Häufig Gestellte Fragen

### F: Meine Snake bewegt sich nicht!
**A:** Stelle sicher dass das Spielfenster aktiv ist (anklicken). Die Maus muss sich über dem Spielfenster befinden.

### F: Die KI ist zu stark!
**A:** Das ist absicht! Tipps:
- Werde größer bevor du kämpfst
- Weiche aus statt zu kämpfen
- Nutze die Spielfeld-Grenzen

### F: Warum bin ich plötzlich gestorben?
**A:** Mögliche Gründe:
- Dein Kopf hat einen Körper getroffen
- Du bist in eine Ecke gerannt und die KI hat dich erwischt
- Head-to-Head Kollision mit KI

### F: Wie viele KI-Snakes gibt es?
**A:** **4 KI-Snakes** mit zufälligen Namen. Sie haben alle unterschiedliche Strategien.

### F: Kann ich die Schwierigkeit ändern?
**A:** Bearbeite `snake_game.py` und ändere `threat_distance = 200` auf einen anderen Wert (größer = schwächer KI).

### F: Kann ich Sound einschalten?
**A:** Das Sound-System ist vorbereitet. Du kannst MP3-Dateien in den `self.sounds` Ordner kopieren.

### F: Wie speichere ich meinen High-Score?
**A:** Derzeit speichert das Spiel keine High-Scores. Das ist eine mögliche zukünftige Erweiterung!

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
2. Reduziere die Fenster-Größe (ändere WINDOW_WIDTH und WINDOW_HEIGHT in snake_game.py)
3. Stelle sicher dass Grafiktreiber aktuell sind

### Problem: Maussteuerung funktioniert nicht

**Lösung:**
1. Stelle sicher dass das Spielfenster im Fokus ist (aktiv)
2. Bewege die Maus über dem Spielfeld
3. Versuche die Maus schneller zu bewegen

### Problem: Spiel stürzt ab beim Start

**Lösung:**
1. Stelle sicher dass du Python 3.7+ hast: `python --version`
2. Installiere requirements neu: `pip install -r requirements.txt`
3. Versuche: `python -m pip install --upgrade pip`

### Problem: Fenster öffnet sich aber bleibt schwarz

**Lösung:**
1. Warte 5-10 Sekunden (Initialisierung)
2. Bewege die Maus im Fenster
3. Drücke eine Taste (SPACE)
4. Wenn nichts hilft, neustarten

## 🎉 Erfolgs-Tricks zum Gewinnen

1. **Starte klein aber sicher**: Konzentriere dich auf Essen in der Nähe
2. **Wachse kontinuierlich**: Nicht riskieren, sondern sicher wachsen
3. **Beobachte andere**: Schau was die KI macht und lerne
4. **Nutze Grenzen**: Die Map-Grenzen sind deine besten Freunde
5. **Geduld**: Langsamkeit gewinnt - überstürze nichts

**Viel Spaß und viel Glück! 🐍🏆**

---

**Noch Fragen? Erstelle einen [GitHub Issue](https://github.com/flappybird007/python/issues)!**
