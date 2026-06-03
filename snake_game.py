import pygame
import random
import math
import os
import json
import webbrowser
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple
import sys
from pathlib import Path

# ==================== INITIALISIERUNG ====================
# Pygame initialisieren (Grafik- und Sound-Engine)
pygame.init()
# Sound-System initialisieren für Audioausgabe
pygame.mixer.init()

# ==================== KONSTANTEN ====================
# Fenster-Dimensionen (Breite x Höhe in Pixeln)
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
# Frames Per Second - höhere Werte = flüssigeres Spiel (60 ist Standard)
FPS = 60
# Größe des Gitter-Hintergrunds (visuell, nicht spielmechanisch)
GRID_SIZE = 10
# Sicherheitsradius um Spieler beim Spawn von KI-Snakes (in Pixeln)
SPAWN_SAFETY_RADIUS = 200

# ==================== FARB-DEFINITIONEN ====================
# RGB-Farben für verschiedene Spielelemente
BLACK = (10, 10, 10)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 100, 255)
YELLOW = (255, 255, 50)
PURPLE = (200, 50, 200)
CYAN = (50, 255, 255)
ORANGE = (255, 165, 50)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
NEON_GREEN = (0, 255, 100)
NEON_PINK = (255, 20, 147)
NEON_CYAN = (0, 255, 255)
BORDER_COLOR = (255, 0, 0)  # Spielfeld-Grenze (leuchtend rot)
DARK_RED = (139, 0, 0)

# ==================== KI-NAMEN ====================
# Pool mit lustigen Namen für KI-Snakes
AI_NAMES = [
    "🤖 RoboNinja", "💀 DeathViper", "⚡ ThunderSnake", "🔥 FlameKing",
    "👾 PixelMonster", "🎮 GameMaster", "⚔️ Warrior", "🌟 StarSlayer",
    "🐉 DragonFury", "🍕 PizzaHunter", "🎪 JokeySnake", "🎸 RockStar",
    "🚀 SpaceSnake", "🌈 RainbowViper", "💎 DiamondSlayer", "🏆 ChampionKing"
]

# ==================== GAME STATES (Spielzustände) ====================
# Enum-Klasse für verschiedene Spiel-Zustände
class GameState(Enum):
    # Hauptmenü
    MENU = 1
    # Aktiv spielen
    PLAYING = 2
    # Spiel pausiert
    PAUSED = 3
    # Spieler ist gestorben
    DEATH = 4
    # Username-Eingabe
    USERNAME_INPUT = 5
    # Farb-Auswahl
    COLOR_SELECT = 6
    # Neues Menü: Einstellungen (z.B. KI an/aus)
    SETTINGS = 7

# ==================== DATA CLASSES ====================
# Leichte Datenklasse für 2D-Koordinaten
@dataclass
class Point:
    # X-Koordinate (horizontal)
    x: float
    # Y-Koordinate (vertikal)
    y: float
    
    def distance_to(self, other: 'Point') -> float:
        """Berechnet Entfernung zu anderem Point mit Pythagoras-Satz"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

# ==================== PARTICLE-KLASSE ====================
class Particle:
    """Visuelle Effekt-Partikel (z.B. bei Essen/Tod)"""
    def __init__(self, x: float, y: float, dx: float, dy: float, lifetime: int, color: Tuple):
        # Startposition
        self.x = x
        self.y = y
        # Bewegungsgeschwindigkeit (delta)
        self.dx = dx
        self.dy = dy
        # Verbleibende Lebensdauer in Frames
        self.lifetime = lifetime
        # Maximale Lebensdauer (für Berechnung der Transparenz)
        self.max_lifetime = lifetime
        # Partikel-Farbe
        self.color = color
    
    def update(self):
        """Aktualisiert Position des Partikels"""
        # Bewege Partikel in Bewegungsrichtung
        self.x += self.dx
        self.y += self.dy
        # Verringere Lebensdauer um 1 Frame
        self.lifetime -= 1
    
    def draw(self, screen: pygame.Surface):
        """Zeichnet Partikel auf Bildschirm (mit Fade-Out-Effekt)"""
        if self.lifetime > 0:
            # Berechne Transparenz basierend auf verbleibender Lebensdauer
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            # Größe wird kleiner mit sinkendem Leben
            size = max(1, int(5 * (self.lifetime / self.max_lifetime)))
            # Zeichne Kreis
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

# ==================== SNAKE-KLASSE ====================
class Snake:
    """Repräsentiert eine Snake (Spieler oder KI)"""
    def __init__(self, x: float, y: float, color: Tuple, is_ai: bool = False, name: str = "", size_variation: float = 1.0):
        # Liste von Points die den Schlangen-Körper darstellen (Index 0 = Kopf)
        self.body = [Point(x, y)]
        # Farbe der Snake
        self.color = color
        # Kopf-Farbe (heller als Körper)
        self.head_color = self._get_head_color(color)
        # Aktuelle Bewegungsrichtung (normalisierter Vektor)
        self.direction = Point(1, 0)
        # Nächste Bewegungsrichtung (für smooth movement)
        self.next_direction = Point(1, 0)
        # Ist dies eine KI-Snake?
        self.is_ai = is_ai
        # Name der Snake (für Anzeige)
        self.name = name
        # Bewegungsgeschwindigkeit (Pixel pro Frame)
        self.speed = 4.5
        # Wie viele Segmente noch wachsen sollen (bei Essen)
        self.growth_pending = 0
        # Ist die Snake tot?
        self.dead = False
        # Aktuelle Rotationswinkel (für Pfeil-Anzeige)
        self.angle = 0
        # Größen-Variation für KI (für unterschiedliche Schwierigkeit)
        self.size_variation = size_variation
        # Basis-Länge für KI-Snakes
        self.base_length = int(8 * size_variation)
        
        # KI-Snakes spawnen mit unterschiedlicher Länge
        if is_ai and size_variation != 1.0:
            for _ in range(self.base_length):
                self.body.append(Point(x - _, y))
        
        # Liste von Effekt-Partikeln
        self.particles = []
        
    def _get_head_color(self, color: Tuple) -> Tuple:
        """Macht Kopf-Farbe heller und auffälliger"""
        # Multipliziere jede RGB-Komponente mit 1.5 (max 255)
        return tuple(min(255, int(c * 1.5)) for c in color)
    
    def add_particle_effect(self, count: int = 5):
        """Erstellt Partikel-Effekte um den Kopf"""
        # Hole Kopf-Position
        head = self.body[0]
        # Erstelle mehrere Partikel
        for _ in range(count):
            # Zufälliger Winkel (0 bis 2π)
            angle = random.uniform(0, 2 * math.pi)
            # Zufällige Geschwindigkeit
            speed = random.uniform(1, 3)
            # Berechne X und Y Bewegungskomponenten
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            # Erstelle Partikel mit 30-Frame Lebensdauer
            particle = Particle(head.x, head.y, dx, dy, 30, self.head_color)
            # Füge zu Partikel-Liste hinzu
            self.particles.append(particle)
    
    def update_particles(self):
        """Aktualisiert alle Partikel und entfernt tote Partikel"""
        # Aktualisiere jeden Partikel
        for particle in self.particles[:]:
            particle.update()
            # Entferne Partikel wenn Lebensdauer abgelaufen
            if particle.lifetime <= 0:
                self.particles.remove(particle)
    
    def draw_particles(self, screen: pygame.Surface):
        """Zeichnet alle Partikel auf Bildschirm"""
        for particle in self.particles:
            particle.draw(screen)
    
    def move(self):
        """Bewegt die Snake um einen Frame"""
        # Wenn Snake tot ist, bewege nicht
        if self.dead:
            return
        
        # Glätte die Richtungswechsel (verhindere 180-Grad-Umkehrungen)
        if self.next_direction.x != 0 or self.next_direction.y != 0:
            # Berechne Skalarprodukt zwischen aktueller und nächster Richtung
            dot_product = self.direction.x * self.next_direction.x + self.direction.y * self.next_direction.y
            # Nur wenn Richtung "ähnlich" ist (dot_product >= 0), wechsle
            if dot_product >= 0:
                self.direction = self.next_direction
        
        # Berechne neue Kopf-Position
        head = self.body[0]
        new_head = Point(
            head.x + self.direction.x * self.speed,
            head.y + self.direction.y * self.speed
        )
        
        # WALL BOUNCE: Wenn Snake Wand trifft, kehre Richtung um
        if new_head.x <= 10 or new_head.x >= WINDOW_WIDTH - 10:
            self.direction.x *= -1
            # Klemme Position damit Snake nicht zu weit außen ist
            new_head.x = max(10, min(WINDOW_WIDTH - 10, new_head.x))
        
        if new_head.y <= 10 or new_head.y >= WINDOW_HEIGHT - 10:
            self.direction.y *= -1
            new_head.y = max(10, min(WINDOW_HEIGHT - 10, new_head.y))
        
        # Füge neuen Kopf am Anfang ein
        self.body.insert(0, new_head)
        
        # Handhabe Wachstum
        if self.growth_pending > 0:
            # Wenn noch Wachstum ausstehend, entferne nicht das Ende
            self.growth_pending -= 1
        else:
            # Ansonsten entferne das Ende (Bewegung ohne Wachstum)
            self.body.pop()
        
        # Aktualisiere Partikel-Effekte
        self.update_particles()
    
    def grow(self, amount: int = 2):
        """Lässt Snake um 'amount' Segmente wachsen"""
        # Füge zur Wachstums-Warteschlange hinzu
        self.growth_pending += amount
        # Erstelle Partikel-Effekt
        self.add_particle_effect(3)
    
    def set_direction(self, dx: float, dy: float):
        """Setzt Bewegungsrichtung (360-Grad-Bewegung)"""
        # Berechne Länge des Richtungsvektors
        length = math.sqrt(dx**2 + dy**2)
        # Normalisiere Vektor (mache ihn zu Einheitslänge)
        if length > 0.1:
            self.next_direction = Point(dx / length, dy / length)
            # Berechne Rotationswinkel für Pfeil-Anzeige
            self.angle = math.degrees(math.atan2(dy, dx))
    
    def ai_update(self, food_points: List[Point], other_snakes: List['Snake']):
        """KI-Logik: Entscheidet wie KI-Snake sich bewegt"""
        # Wenn Snake tot oder nicht KI, tue nichts
        if self.dead or not self.is_ai:
            return
        
        # Hole Kopf-Position
        head = self.body[0]
        
        # Finde nächstes Essen
        nearest_food = None
        nearest_dist = float('inf')
        for food in food_points:
            # Berechne Entfernung zum Essen
            dist = head.distance_to(food)
            # Wenn näheres Essen gefunden, update
            if dist < nearest_dist:
                nearest_dist = dist
                nearest_food = food
        
        # Finde bedrohliche andere Snakes
        threat_distance = 250
        threats = []
        for snake in other_snakes:
            # Ignoriere eigene Snake und tote Snakes
            if snake != self and not snake.dead:
                # Berechne Entfernung zur anderen Snake
                dist = head.distance_to(snake.body[0])
                # Wenn nah genug, füge zu Bedrohungen hinzu
                if dist < threat_distance:
                    threats.append((snake.body[0], len(snake.body)))
        
        # Beste bisherige Richtung und Score
        best_direction = self.direction
        best_score = -float('inf')
        
        # Teste 16 verschiedene Richtungen (alle 23 Grad)
        # So kann KI in fast alle Richtungen denken
        for angle in range(0, 360, 23):
            # Konvertiere Grad zu Radiant
            rad = math.radians(angle)
            # Berechne X und Y Komponenten
            dx = math.cos(rad)
            dy = math.sin(rad)
            
            # Überprüfe dass Richtung nicht nach hinten ist (dot_product)
            dot_product = self.direction.x * dx + self.direction.y * dy
            if dot_product < 0.3:
                continue
            
            # Erstelle Test-Punkt 25 Einheiten voraus
            test_point = Point(
                head.x + dx * self.speed * 25,
                head.y + dy * self.speed * 25
            )
            
            # Klemme Test-Punkt in Spielfeld-Grenzen
            test_point.x = max(10, min(WINDOW_WIDTH - 10, test_point.x))
            test_point.y = max(10, min(WINDOW_HEIGHT - 10, test_point.y))
            
            # Berechne Score für diese Richtung
            score = 0
            
            # Positive: Nähe zu Essen
            if nearest_food:
                food_dist = test_point.distance_to(nearest_food)
                # Je näher zum Essen, desto höher der Score
                score += 200 - (food_dist / 6)
            
            # Negative: Bedrohungen (andere Snakes)
            for threat_pos, threat_length in threats:
                threat_dist = test_point.distance_to(threat_pos)
                # Je stärker die Bedrohung, desto mehr Straf-Punkte
                if threat_length > len(self.body):
                    score -= 600 / (threat_dist + 1)
                else:
                    score -= 150 / (threat_dist + 1)
            
            # Negative: Selbst-Kollision
            collision = False
            for segment in self.body[4:]:
                if test_point.distance_to(segment) < 15:
                    collision = True
                    break
            
            if collision:
                score -= 1200
            
            # Negative: Zu nahe an Wänden
            wall_penalty = 0
            if test_point.x < 50:
                wall_penalty += 150
            if test_point.x > WINDOW_WIDTH - 50:
                wall_penalty += 150
            if test_point.y < 50:
                wall_penalty += 150
            if test_point.y > WINDOW_HEIGHT - 50:
                wall_penalty += 150
            score -= wall_penalty
            
            # Speichere beste Richtung
            if score > best_score:
                best_score = score
                best_direction = Point(dx, dy)
        
        # Setze beste Richtung
        self.set_direction(best_direction.x, best_direction.y)
    
    def get_head(self) -> Point:
        """Gibt den Kopf der Snake zurück"""
        return self.body[0]
    
    def check_self_collision(self) -> bool:
        """Überprüft ob Snake gegen sich selbst stößt"""
        head = self.get_head()
        # Überprüfe alle Körper-Segmente (ab Index 4, um Bewegung zu erlauben)
        for segment in self.body[4:]:
            if head.distance_to(segment) < 10:
                return True
        return False
    
    def draw_direction_arrow(self, screen: pygame.Surface):
        """Zeichnet Pfeil der Bewegungsrichtung auf Kopf"""
        head = self.body[0]
        arrow_length = 20
        
        # Berechne Pfeil-Spitze
        tip_x = head.x + math.cos(self.angle * math.pi / 180) * arrow_length
        tip_y = head.y + math.sin(self.angle * math.pi / 180) * arrow_length
        
        # Zeichne Pfeil-Stab
        pygame.draw.line(screen, self.head_color, (int(head.x), int(head.y)), (int(tip_x), int(tip_y)), 3)
        
        # Zeichne Pfeil-Flügel (2 Linien nach hinten)
        angle_rad = self.angle * math.pi / 180
        for offset_angle in [-30, 30]:
            back_angle = angle_rad + (offset_angle + 180) * math.pi / 180
            back_x = tip_x + math.cos(back_angle) * 8
            back_y = tip_y + math.sin(back_angle) * 8
            pygame.draw.line(screen, self.head_color, (int(tip_x), int(tip_y)), (int(back_x), int(back_y)), 2)
    
    def draw(self, screen: pygame.Surface):
        """Zeichnet die Snake mit Gradient und Effekten"""
        # Zeichne Körper-Segmente
        for i, segment in enumerate(self.body):
            # Berechne Helligkeit (weiter hinten = dunkler)
            brightness = max(0.4, 1 - i * 0.015)
            # Multipliziere Farbe mit Helligkeit
            color = tuple(int(c * brightness) for c in self.color)
            # Zeichne Segment als Kreis
            pygame.draw.circle(screen, color, (int(segment.x), int(segment.y)), 6)
            # Weiße Umrandung für Definition
            pygame.draw.circle(screen, WHITE, (int(segment.x), int(segment.y)), 6, 1)
        
        # Zeichne helleren Kopf
        pygame.draw.circle(screen, self.head_color, (int(self.body[0].x), int(self.body[0].y)), 8)
        pygame.draw.circle(screen, WHITE, (int(self.body[0].x), int(self.body[0].y)), 8, 2)
        
        # Zeichne Richtungs-Pfeil
        self.draw_direction_arrow(screen)
        
        # Zeichne Namen über dem Kopf
        font = pygame.font.Font(None, 18)
        name_text = font.render(self.name, True, self.head_color)
        screen.blit(name_text, (int(self.body[0].x) - 20, int(self.body[0].y) - 35))

# ==================== HAUPTGAME-KLASSE ====================
class SnakeGame:
    """Hauptklasse die das ganze Spiel koordiniert"""
    def __init__(self):
        # Erstelle Spiel-Fenster
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        # Fenster-Titel
        pygame.display.set_caption("🐍 SLIMY SNAKE - Multiplayer Edition")
        # Uhr für FPS-Kontrolle
        self.clock = pygame.time.Clock()
        
        # Verschiedene Schrift-Größen
        self.font_large = pygame.font.Font(None, 80)
        self.font_medium = pygame.font.Font(None, 45)
        self.font_small = pygame.font.Font(None, 28)
        self.font_tiny = pygame.font.Font(None, 20)
        
        # Aktueller Spiel-Zustand
        self.state = GameState.MENU
        # Spieler-Name
        self.player_name = "Player1"
        # Spieler-Farbe
        self.player_color = GREEN
        # Verfügbare Farben für Auswahl
        self.available_colors = [GREEN, BLUE, ORANGE, CYAN, PURPLE, NEON_GREEN, NEON_PINK, YELLOW]
        # Index der aktuellen Farb-Auswahl
        self.color_index = 0
        
        # Sound-Status
        self.music_loaded = False
        self.eat_sound_loaded = False
        self.death_sound_loaded = False
        
        # NEUE FEATURE: KI-Status (an/aus)
        self.ai_enabled = True
        
        # Initialisiere Spiel
        self.reset_game()
        # Lade Sound-Effekte
        self.load_sounds()
        # Lade oder erstelle Stats-Datei
        self.load_stats()
    
    def load_stats(self):
        """Lädt oder erstellt die Stats-Datei im Dateipfad"""
        # Definiere Pfad für Stats-Datei (im Benutzer-Home-Verzeichnis)
        self.stats_file = Path(os.path.expanduser("~")) / ".slimy_snake_stats.json"
        
        # Versuche Stats zu laden
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    self.stats = json.load(f)
            except:
                self.stats = self._create_empty_stats()
        else:
            self.stats = self._create_empty_stats()
    
    def _create_empty_stats(self) -> dict:
        """Erstellt eine neue leere Stats-Struktur"""
        return {
            "total_games": 0,
            "highest_score": 0,
            "total_food_eaten": 0,
            "best_player_name": "None",
            "games": []
        }
    
    def save_stats(self, final_length: int, ai_killed_you: bool = False):
        """Speichert Game-Stats nach Tod"""
        # Aktualisiere Stats
        self.stats["total_games"] += 1
        self.stats["total_food_eaten"] += max(0, final_length - 1)
        
        # Update bester Score
        if final_length > self.stats["highest_score"]:
            self.stats["highest_score"] = final_length
            self.stats["best_player_name"] = self.player_name
        
        # Füge Spiel zu Geschichte hinzu
        game_data = {
            "player_name": self.player_name,
            "final_length": final_length,
            "ai_enabled": self.ai_enabled,
            "ai_killed": ai_killed_you,
            "timestamp": str(pygame.time.get_ticks())
        }
        self.stats["games"].append(game_data)
        
        # Speichere in Datei
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except:
            pass
    
    def load_sounds(self):
        """Lädt Sound-Effekte aus Assets-Ordner"""
        self.sounds = {}
        try:
            # Versuche Ess-Sound zu laden
            if os.path.exists('assets/eat.wav'):
                self.sounds['eat'] = pygame.mixer.Sound('assets/eat.wav')
                self.eat_sound_loaded = True
            # Versuche Tod-Sound zu laden
            if os.path.exists('assets/death.wav'):
                self.sounds['death'] = pygame.mixer.Sound('assets/death.wav')
                self.death_sound_loaded = True
            # Versuche Musik zu laden (MP3 oder WAV)
            if os.path.exists('assets/music.mp3') or os.path.exists('assets/music.wav'):
                music_file = 'assets/music.mp3' if os.path.exists('assets/music.mp3') else 'assets/music.wav'
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
                self.music_loaded = True
        except:
            # Ignoriere fehler beim Sound-Laden
            pass
    
    def play_sound(self, sound_name: str):
        """Spielt einen Sound ab falls verfügbar"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def is_safe_spawn_location(self, x: float, y: float, exclude_snake: 'Snake' = None) -> bool:
        """Überprüft ob Spawn-Ort sicher ist (nicht zu nahe beim Spieler)"""
        if exclude_snake:
            # Berechne Entfernung zum Spieler
            dist = exclude_snake.get_head().distance_to(Point(x, y))
            # Nur wenn weit genug weg
            return dist > SPAWN_SAFETY_RADIUS
        return True
    
    def reset_game(self):
        """Setzt Spiel zurück und spawnt neue Snakes"""
        # Erstelle Spieler-Snake in der Mitte
        self.player = Snake(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, self.player_color, 
                           is_ai=False, name=self.player_name)
        
        # Erstelle KI-Snakes
        self.ai_snakes = []
        # Farben für KI-Snakes
        ai_colors = [BLUE, ORANGE, CYAN, PURPLE, NEON_GREEN, NEON_PINK]
        
        # Nur erstelle KI-Snakes wenn aktiviert
        if self.ai_enabled:
            # Erstelle 4 KI-Snakes
            for i in range(4):
                safe_spawn = False
                attempts = 0
                # Versuche sichere Spawn-Position zu finden
                while not safe_spawn and attempts < 10:
                    spawn_x = random.randint(100, WINDOW_WIDTH - 100)
                    spawn_y = random.randint(100, WINDOW_HEIGHT - 100)
                    if self.is_safe_spawn_location(spawn_x, spawn_y, self.player):
                        safe_spawn = True
                    attempts += 1
                
                # Erstelle KI-Snake wenn sichere Position gefunden
                if safe_spawn:
                    random_name = random.choice(AI_NAMES)
                    # Variable Größe für KI (Schwierigkeit)
                    size_variation = random.uniform(0.7, 1.3)
                    self.ai_snakes.append(
                        Snake(spawn_x, spawn_y,
                              ai_colors[i % len(ai_colors)], 
                              is_ai=True, 
                              name=random_name,
                              size_variation=size_variation)
                    )
        
        # Kombiniere alle Snakes (Spieler + KI)
        self.all_snakes = [self.player] + self.ai_snakes
        # Leere Essen-Liste
        self.food_points = []
        # Spawn 35 Essen-Punkte
        self.spawn_food(35)
        
        # Setze initiale Bewegungsrichtung
        self.player.direction = Point(1, 0)
        self.player.next_direction = Point(1, 0)
        
        # Setze Zustand auf SPIELEN
        self.state = GameState.PLAYING
    
    def spawn_food(self, count: int = 1):
        """Spawnt Essen auf zufälligen Positionen"""
        for _ in range(count):
            self.food_points.append(Point(
                random.randint(20, WINDOW_WIDTH - 20),
                random.randint(20, WINDOW_HEIGHT - 20)
            ))
    
    def handle_mouse_movement(self):
        """Handhabe Mouse-Steuerung (360-Grad)"""
        if self.state == GameState.PLAYING and not self.player.dead:
            # Hole aktuelle Mouse-Position
            mouse_x, mouse_y = pygame.mouse.get_pos()
            head = self.player.get_head()
            
            # Berechne Vektor von Snake-Kopf zur Maus
            dx = mouse_x - head.x
            dy = mouse_y - head.y
            
            # Normalisiere Vektor
            length = math.sqrt(dx**2 + dy**2)
            if length > 5:
                self.player.set_direction(dx / length, dy / length)
    
    def handle_input(self):
        """Handhabe alle Nutzer-Eingaben"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                # ========== MENÜ-BILDSCHIRM ==========
                if self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
                        # SPACE = Starte Username-Eingabe
                        self.state = GameState.USERNAME_INPUT
                    elif event.key == pygame.K_s:
                        # S = Öffne Einstellungen
                        self.state = GameState.SETTINGS
                    elif event.key == pygame.K_q:
                        # Q = Beende Spiel
                        return False
                
                # ========== USERNAME-EINGABE ==========
                elif self.state == GameState.USERNAME_INPUT:
                    if event.key == pygame.K_RETURN:
                        # ENTER = Gehe zu Farb-Auswahl
                        self.state = GameState.COLOR_SELECT
                    elif event.key == pygame.K_BACKSPACE:
                        # BACKSPACE = Lösche letzten Buchstaben
                        self.player_name = self.player_name[:-1]
                    elif event.unicode.isprintable() and len(self.player_name) < 15:
                        # Eingabe = Füge Buchstabe hinzu (max 15 Zeichen)
                        self.player_name += event.unicode
                
                # ========== FARB-AUSWAHL ==========
                elif self.state == GameState.COLOR_SELECT:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        # LINKS/A = Vorherige Farbe
                        self.color_index = (self.color_index - 1) % len(self.available_colors)
                        self.player_color = self.available_colors[self.color_index]
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        # RECHTS/D = Nächste Farbe
                        self.color_index = (self.color_index + 1) % len(self.available_colors)
                        self.player_color = self.available_colors[self.color_index]
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        # ENTER/SPACE = Starte Spiel
                        self.reset_game()
                
                # ========== EINSTELLUNGEN ==========
                elif self.state == GameState.SETTINGS:
                    if event.key == pygame.K_a:
                        # A = Toggle KI an/aus
                        self.ai_enabled = not self.ai_enabled
                    elif event.key == pygame.K_r:
                        # R = Öffne README
                        self.open_readme()
                    elif event.key == pygame.K_i:
                        # I = Öffne Anleitung
                        self.open_anleitung()
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        # ESC/ENTER = Zurück zum Menü
                        self.state = GameState.MENU
                
                # ========== WÄHREND SPIELEN ==========
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        # ESC = Pausiere Spiel
                        self.state = GameState.PAUSED
                
                # ========== PAUSIERT ==========
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        # ESC = Fortsetzen
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_m:
                        # M = Zurück zum Menü
                        self.state = GameState.MENU
                
                # ========== TOD-BILDSCHIRM ==========
                elif self.state == GameState.DEATH:
                    if event.key == pygame.K_SPACE:
                        # SPACE = Nochmal spielen
                        self.state = GameState.USERNAME_INPUT
                    elif event.key == pygame.K_m:
                        # M = Zurück zum Menü
                        self.state = GameState.MENU
        
        return True
    
    def open_readme(self):
        """Öffnet README-Datei"""
        readme_path = Path("README.md").absolute()
        if readme_path.exists():
            webbrowser.open(f'file://{readme_path}')
    
    def open_anleitung(self):
        """Öffnet ANLEITUNG-Datei"""
        anleitung_path = Path("ANLEITUNG.md").absolute()
        if anleitung_path.exists():
            webbrowser.open(f'file://{anleitung_path}')
    
    def update(self):
        """Aktualisiert alle Spiel-Logik für einen Frame"""
        if self.state == GameState.PLAYING:
            # Handhabe Mouse-Bewegung
            self.handle_mouse_movement()
            
            # Bewege alle Snakes
            for snake in self.all_snakes:
                snake.move()
            
            # Aktualisiere KI
            for ai_snake in self.ai_snakes:
                ai_snake.ai_update(self.food_points, self.all_snakes)
            
            # ========== ESSEN-KOLLISION ==========
            for snake in self.all_snakes:
                if not snake.dead:
                    head = snake.get_head()
                    for food in self.food_points[:]:
                        if head.distance_to(food) < 15:
                            # Snake isst Essen
                            snake.grow(2)
                            self.food_points.remove(food)
                            self.spawn_food(1)
                            self.play_sound('eat')
            
            # ========== KOPF-ZU-KÖRPER KOLLISION ==========
            for snake in self.all_snakes:
                if not snake.dead:
                    head = snake.get_head()
                    
                    for other_snake in self.all_snakes:
                        if other_snake == snake or other_snake.dead:
                            continue
                        
                        # Überprüfe nur Körper (nicht den Kopf der anderen Snake)
                        for i in range(1, len(other_snake.body)):
                            segment = other_snake.body[i]
                            if head.distance_to(segment) < 10:
                                # Kollision! Snake stirbt
                                snake.dead = True
                                snake.add_particle_effect(10)
                                
                                # Drop Essen beim Tod
                                for _ in range(len(snake.body) // 5):
                                    self.food_points.append(Point(
                                        head.x + random.randint(-30, 30),
                                        head.y + random.randint(-30, 30)
                                    ))
                                self.play_sound('death')
                                break
                        
                        if snake.dead:
                            break
            
            # ========== SELBST-KOLLISION ==========
            for snake in self.all_snakes:
                if not snake.dead and snake.check_self_collision():
                    snake.dead = True
                    snake.add_particle_effect(10)
                    self.play_sound('death')
            
            # ========== SPIELER-TOD-ÜBERPRÜFUNG ==========
            if self.player.dead:
                # Speichere Stats bevor wir zum Death-Screen gehen
                self.save_stats(len(self.player.body))
                self.state = GameState.DEATH
    
    def draw_menu(self):
        """Zeichnet Hauptmenü"""
        # Fülle Hintergrund mit schwarz
        self.screen.fill(BLACK)
        
        # Futuristisches Gitter-Muster
        for x in range(0, WINDOW_WIDTH, 60):
            for y in range(0, WINDOW_HEIGHT, 60):
                if (x // 60 + y // 60) % 2 == 0:
                    pygame.draw.rect(self.screen, DARK_GRAY, (x, y, 60, 60))
        
        # Neon-Rahmen
        pygame.draw.rect(self.screen, NEON_CYAN, (20, 20, WINDOW_WIDTH - 40, WINDOW_HEIGHT - 40), 5)
        
        # Titel
        title = self.font_large.render("🐍 SLIMY SNAKE", True, NEON_GREEN)
        subtitle = self.font_medium.render("Multiplayer Edition", True, NEON_PINK)
        
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 50))
        self.screen.blit(subtitle, (WINDOW_WIDTH // 2 - subtitle.get_width() // 2, 150))
        
        # Anleitung
        instructions = [
            "🖱️  MOVE MOUSE to control your snake (360° movement)",
            "🍕 Eat food (dots) to grow bigger",
            "⚔️  Avoid other snakes' bodies",
            "💪 Your BODY doesn't hurt - only head-to-body collision = DEATH",
            "🏆 Become the longest snake!",
            "",
            "PRESS SPACE TO START",
            "PRESS S FOR SETTINGS",
            "PRESS Q TO QUIT"
        ]
        
        y = 300
        for instruction in instructions:
            if instruction:
                text = self.font_small.render(instruction, True, WHITE)
                self.screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, y))
            y += 50
    
    def draw_username_input(self):
        """Zeichnet Username-Eingabe-Bildschirm"""
        self.screen.fill(BLACK)
        
        # Rahmen
        pygame.draw.rect(self.screen, NEON_CYAN, (50, 50, WINDOW_WIDTH - 100, WINDOW_HEIGHT - 100), 3)
        
        # Titel
        title = self.font_large.render("Choose Your Name", True, NEON_GREEN)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 200))
        
        # Input-Text (mit Cursor)
        input_text = self.font_medium.render(self.player_name + "_", True, YELLOW)
        self.screen.blit(input_text, (WINDOW_WIDTH // 2 - input_text.get_width() // 2, 350))
        
        # Hinweis
        hint = self.font_small.render("Press ENTER to continue", True, WHITE)
        self.screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 480))
    
    def draw_color_select(self):
        """Zeichnet Farb-Auswahl-Bildschirm"""
        self.screen.fill(BLACK)
        
        # Rahmen
        pygame.draw.rect(self.screen, NEON_CYAN, (50, 50, WINDOW_WIDTH - 100, WINDOW_HEIGHT - 100), 3)
        
        # Titel
        title = self.font_large.render("Choose Your Color", True, NEON_GREEN)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 100))
        
        # Große Preview-Kreis mit aktueller Farbe
        pygame.draw.circle(self.screen, self.player_color, (WINDOW_WIDTH // 2, 250), 50)
        pygame.draw.circle(self.screen, WHITE, (WINDOW_WIDTH // 2, 250), 50, 3)
        
        # Zeige alle Farben
        colors_per_row = 4
        color_size = 60
        start_x = WINDOW_WIDTH // 2 - (colors_per_row * color_size) // 2
        
        for i, color in enumerate(self.available_colors):
            row = i // colors_per_row
            col = i % colors_per_row
            x = start_x + col * color_size + 30
            y = 380 + row * 100
            
            # Zeichne Farb-Kreis
            pygame.draw.circle(self.screen, color, (x, y), 25)
            # Markiere aktuell ausgewählte Farbe
            if color == self.player_color:
                pygame.draw.circle(self.screen, WHITE, (x, y), 25, 4)
            else:
                pygame.draw.circle(self.screen, GRAY, (x, y), 25, 1)
        
        # Hinweis
        hint = self.font_small.render("← LEFT/RIGHT → to choose | ENTER to start", True, WHITE)
        self.screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 750))
    
    def draw_settings(self):
        """Zeichnet Einstellungs-Bildschirm"""
        self.screen.fill(BLACK)
        
        # Rahmen
        pygame.draw.rect(self.screen, NEON_CYAN, (50, 50, WINDOW_WIDTH - 100, WINDOW_HEIGHT - 100), 3)
        
        # Titel
        title = self.font_large.render("⚙️ SETTINGS", True, NEON_GREEN)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 100))
        
        # AI Toggle
        ai_status = "ON ✓" if self.ai_enabled else "OFF ✗"
        ai_text = self.font_medium.render(f"AI Opponents: {ai_status}", True, YELLOW)
        self.screen.blit(ai_text, (WINDOW_WIDTH // 2 - ai_text.get_width() // 2, 250))
        
        ai_hint = self.font_small.render("Press A to toggle", True, GRAY)
        self.screen.blit(ai_hint, (WINDOW_WIDTH // 2 - ai_hint.get_width() // 2, 330))
        
        # Documentation Links
        options = [
            ("Press R to open README", 420),
            ("Press I to open ANLEITUNG", 490),
            ("", 560),
            ("Press ESC to return to MENU", 630)
        ]
        
        for option, y_pos in options:
            if option:
                opt_text = self.font_small.render(option, True, WHITE if "Press E" in option or "Press I" in option else GRAY)
                self.screen.blit(opt_text, (WINDOW_WIDTH // 2 - opt_text.get_width() // 2, y_pos))
    
    def draw_game(self):
        """Zeichnet Spiel-Bildschirm"""
        # Fülle mit schwarz
        self.screen.fill(BLACK)
        
        # Futuristisches Gitter
        for x in range(0, WINDOW_WIDTH, GRID_SIZE * 10):
            pygame.draw.line(self.screen, DARK_GRAY, (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE * 10):
            pygame.draw.line(self.screen, DARK_GRAY, (0, y), (WINDOW_WIDTH, y), 1)
        
        # Rote Spielfeld-Grenze
        pygame.draw.rect(self.screen, BORDER_COLOR, (5, 5, WINDOW_WIDTH - 10, WINDOW_HEIGHT - 10), 5)
        pygame.draw.rect(self.screen, DARK_RED, (3, 3, WINDOW_WIDTH - 6, WINDOW_HEIGHT - 6), 2)
        
        # Zeichne Essen
        for food in self.food_points:
            pygame.draw.circle(self.screen, YELLOW, (int(food.x), int(food.y)), 5)
            pygame.draw.circle(self.screen, ORANGE, (int(food.x), int(food.y)), 5, 2)
        
        # Zeichne alle Snakes
        for snake in self.all_snakes:
            if not snake.dead:
                snake.draw(self.screen)
        
        # ========== HUD (Heads-Up Display) ==========
        # Spieler-Score
        player_length = len(self.player.body)
        player_score = self.font_small.render(f"👤 {self.player_name}: {player_length}", True, self.player_color)
        self.screen.blit(player_score, (10, 10))
        
        # FPS-Zähler
        fps_text = self.font_tiny.render(f"FPS: {int(self.clock.get_fps())}", True, NEON_GREEN)
        self.screen.blit(fps_text, (10, 40))
        
        # Leaderboard
        scoreboard_y = 70
        self.screen.blit(self.font_tiny.render("LEADERBOARD", True, NEON_GREEN), (10, scoreboard_y))
        
        # Sortiere Snakes nach Länge (längste zuerst)
        sorted_snakes = sorted(self.all_snakes, key=lambda s: len(s.body), reverse=True)
        scoreboard_y += 30
        for i, snake in enumerate(sorted_snakes):
            if not snake.dead:
                # Medaillen für Top 3
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
                score_text = self.font_tiny.render(
                    f"{medal} {snake.name}: {len(snake.body)}", 
                    True, 
                    snake.head_color
                )
                self.screen.blit(score_text, (10, scoreboard_y))
                scoreboard_y += 25
    
    def draw_pause(self):
        """Zeichnet Pause-Bildschirm"""
        # Zeichne Spiel im Hintergrund
        self.draw_game()
        
        # Halbdurchsichtiges schwarzes Overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Pause-Text
        pause_text = self.font_large.render("⏸️ PAUSED", True, NEON_PINK)
        self.screen.blit(pause_text, (WINDOW_WIDTH // 2 - pause_text.get_width() // 2, 300))
        
        # Resume-Hinweis
        resume_text = self.font_medium.render("Press ESC to Resume", True, WHITE)
        self.screen.blit(resume_text, (WINDOW_WIDTH // 2 - resume_text.get_width() // 2, 420))
        
        # Menü-Hinweis
        menu_text = self.font_small.render("Press M for Menu", True, GRAY)
        self.screen.blit(menu_text, (WINDOW_WIDTH // 2 - menu_text.get_width() // 2, 520))
    
    def draw_death(self):
        """Zeichnet Tod-Bildschirm"""
        # Zeichne Spiel im Hintergrund
        self.draw_game()
        
        # Undurchsichtiges schwarzes Overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Tod-Text
        death_text = self.font_large.render("💀 YOU DIED!", True, RED)
        self.screen.blit(death_text, (WINDOW_WIDTH // 2 - death_text.get_width() // 2, 150))
        
        # Final-Score
        score_text = self.font_medium.render(f"Final Length: {len(self.player.body)}", True, YELLOW)
        self.screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 300))
        
        # Best-AI-Snake (Gewinner)
        top_snake = max((s for s in self.ai_snakes if not s.dead), key=lambda s: len(s.body), default=None)
        if top_snake:
            killer_text = self.font_small.render(f"🏆 Winner: {top_snake.name} ({len(top_snake.body)})", True, NEON_GREEN)
            self.screen.blit(killer_text, (WINDOW_WIDTH // 2 - killer_text.get_width() // 2, 400))
        
        # Replay-Hinweis
        retry_text = self.font_small.render("Press SPACE to Play Again", True, GREEN)
        self.screen.blit(retry_text, (WINDOW_WIDTH // 2 - retry_text.get_width() // 2, 520))
        
        # Menü-Hinweis
        menu_text = self.font_small.render("Press M for Menu", True, GRAY)
        self.screen.blit(menu_text, (WINDOW_WIDTH // 2 - menu_text.get_width() // 2, 580))
    
    def draw(self):
        """Haupt-Draw-Funktion (wähle was zu zeichnen ist)"""
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.USERNAME_INPUT:
            self.draw_username_input()
        elif self.state == GameState.COLOR_SELECT:
            self.draw_color_select()
        elif self.state == GameState.SETTINGS:
            self.draw_settings()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.PAUSED:
            self.draw_pause()
        elif self.state == GameState.DEATH:
            self.draw_death()
        
        # Update Fenster mit neuen Zeichnungen
        pygame.display.flip()
    
    def run(self):
        """Hauptgame-Loop"""
        running = True
        while running:
            # Handhabe Input
            running = self.handle_input()
            # Aktualisiere Logik
            self.update()
            # Zeichne alles
            self.draw()
            # Tick für FPS-Kontrolle
            self.clock.tick(FPS)
        
        # Pygame beenden
        pygame.quit()

# ==================== EINSTIEGSPUNKT ====================
if __name__ == "__main__":
    # Erstelle Spiel-Instanz
    game = SnakeGame()
    # Starte Spiel-Loop
    game.run()
