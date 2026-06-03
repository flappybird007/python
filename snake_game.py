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
# Fenster-Dimensionen (Breite x Höhe in Pixeln) - können mit Fullscreen geändert werden
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
# Frames Per Second - höhere Werte = flüssigeres Spiel (60 ist Standard)
FPS = 60
# Größe des Gitter-Hintergrunds (visuell, nicht spielmechanisch)
GRID_SIZE = 10
# Sicherheitsradius um Spieler beim Spawn
SPAWN_SAFETY_RADIUS = 300

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
BORDER_COLOR = (255, 0, 0)
DARK_RED = (139, 0, 0)
DEEP_SPACE = (5, 5, 20)  # Deep space blue-black
NEON_BLUE = (0, 150, 255)

# ==================== GAME STATES ====================
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    DEATH = 4
    USERNAME_INPUT = 5
    COLOR_SELECT = 6
    SETTINGS = 7

# ==================== DATA CLASSES ====================
@dataclass
class Point:
    x: float
    y: float
    
    def distance_to(self, other: 'Point') -> float:
        """Berechnet Entfernung zu anderem Point"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

# ==================== PARTICLE-KLASSE ====================
class Particle:
    """Visuelle Effekt-Partikel"""
    def __init__(self, x: float, y: float, dx: float, dy: float, lifetime: int, color: Tuple):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = color
    
    def update(self):
        """Aktualisiert Position des Partikels"""
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1
    
    def draw(self, screen: pygame.Surface):
        """Zeichnet Partikel auf Bildschirm"""
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            size = max(1, int(5 * (self.lifetime / self.max_lifetime)))
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

# ==================== ASTEROID-KLASSE ====================
class Asteroid:
    """Repräsentiert einen Asteroiden - Hindernis im Spiel"""
    def __init__(self, x: float, y: float, size: int = 15):
        self.x = x
        self.y = y
        self.size = size
        self.color = NEON_CYAN
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-5, 5)
        # Asteroiden driften langsam durch die Lobby
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.5, 0.5)
        self.destroyed = False
        self.particles = []
    
    def update(self):
        """Bewegt den Asteroiden"""
        if not self.destroyed:
            self.x += self.vx
            self.y += self.vy
            self.rotation += self.rotation_speed
            
            # Wraparound an den Grenzen
            if self.x < -50:
                self.x = WINDOW_WIDTH + 50
            if self.x > WINDOW_WIDTH + 50:
                self.x = -50
            if self.y < -50:
                self.y = WINDOW_HEIGHT + 50
            if self.y > WINDOW_HEIGHT + 50:
                self.y = -50
    
    def draw(self, screen: pygame.Surface):
        """Zeichnet den Asteroiden mit Rotation"""
        if not self.destroyed:
            # Zeichne mehrere Ringe für 3D-Effekt
            pygame.draw.circle(screen, NEON_CYAN, (int(self.x), int(self.y)), self.size)
            pygame.draw.circle(screen, DARK_GRAY, (int(self.x), int(self.y)), self.size, 2)
            pygame.draw.circle(screen, NEON_CYAN, (int(self.x), int(self.y)), int(self.size * 0.6), 1)

# ==================== ORB-KLASSE ====================
class Orb:
    """Power-up Orbs - selten, aber mächtig"""
    def __init__(self, x: float, y: float, is_special: bool = False):
        self.x = x
        self.y = y
        # Blaue normale Orbs, Lila für spezial Power-ups
        self.color = NEON_BLUE if not is_special else NEON_PINK
        self.is_special = is_special
        self.size = 8 if not is_special else 12
        self.bob_offset = 0
        self.bob_speed = 0.1
        self.rotation = 0
        self.collected = False
    
    def update(self):
        """Animiert die Orb"""
        self.bob_offset += self.bob_speed
        self.rotation += 5
    
    def draw(self, screen: pygame.Surface):
        """Zeichnet die Orb mit Animation"""
        if not self.collected:
            # Bobbing Animation
            bob_y = self.y + math.sin(self.bob_offset) * 5
            
            # Glowing Effekt
            pygame.draw.circle(screen, self.color, (int(self.x), int(bob_y)), self.size)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(bob_y)), self.size, 1)
            
            # Innerer Glanz
            if self.is_special:
                pygame.draw.circle(screen, NEON_PINK, (int(self.x - 3), int(bob_y - 3)), 2)

# ==================== SNAKE-KLASSE ====================
class Snake:
    """Repräsentiert die Spieler-Snake"""
    def __init__(self, x: float, y: float, color: Tuple, name: str = ""):
        self.body = [Point(x, y)]
        self.color = color
        self.head_color = self._get_head_color(color)
        self.direction = Point(1, 0)
        self.next_direction = Point(1, 0)
        self.name = name
        self.speed = 4.5
        self.growth_pending = 0
        self.dead = False
        self.angle = 0
        self.particles = []
        
        # Power-up Effekte
        self.powered_up = False
        self.power_up_time = 0
        self.power_up_duration = 15 * FPS  # 15 Sekunden
        self.shield_color = NEON_PINK
    
    def _get_head_color(self, color: Tuple) -> Tuple:
        """Macht Kopf-Farbe heller"""
        return tuple(min(255, int(c * 1.5)) for c in color)
    
    def add_particle_effect(self, count: int = 5):
        """Erstellt Partikel-Effekte"""
        head = self.body[0]
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            particle = Particle(head.x, head.y, dx, dy, 30, self.head_color)
            self.particles.append(particle)
    
    def update_particles(self):
        """Aktualisiert Partikel"""
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)
    
    def update_power_up(self):
        """Aktualisiert Power-up Status"""
        if self.powered_up:
            self.power_up_time -= 1
            if self.power_up_time <= 0:
                self.powered_up = False
    
    def activate_power_up(self):
        """Aktiviert den Power-up"""
        self.powered_up = True
        self.power_up_time = self.power_up_duration
        self.add_particle_effect(15)
    
    def move(self):
        """Bewegt die Snake"""
        if self.dead:
            return
        
        if self.next_direction.x != 0 or self.next_direction.y != 0:
            dot_product = self.direction.x * self.next_direction.x + self.direction.y * self.next_direction.y
            if dot_product >= 0:
                self.direction = self.next_direction
        
        head = self.body[0]
        new_head = Point(
            head.x + self.direction.x * self.speed,
            head.y + self.direction.y * self.speed
        )
        
        # Wall Bounce
        if new_head.x <= 10 or new_head.x >= WINDOW_WIDTH - 10:
            self.direction.x *= -1
            new_head.x = max(10, min(WINDOW_WIDTH - 10, new_head.x))
        
        if new_head.y <= 10 or new_head.y >= WINDOW_HEIGHT - 10:
            self.direction.y *= -1
            new_head.y = max(10, min(WINDOW_HEIGHT - 10, new_head.y))
        
        self.body.insert(0, new_head)
        
        if self.growth_pending > 0:
            self.growth_pending -= 1
        else:
            self.body.pop()
        
        self.update_particles()
    
    def grow(self, amount: int = 2):
        """Lässt Snake wachsen"""
        self.growth_pending += amount
        self.add_particle_effect(3)
    
    def set_direction(self, dx: float, dy: float):
        """Setzt Bewegungsrichtung"""
        length = math.sqrt(dx**2 + dy**2)
        if length > 0.1:
            self.next_direction = Point(dx / length, dy / length)
            self.angle = math.degrees(math.atan2(dy, dx))
    
    def get_head(self) -> Point:
        """Gibt den Kopf zurück"""
        return self.body[0]
    
    def check_self_collision(self) -> bool:
        """Überprüft Selbst-Kollision"""
        head = self.get_head()
        for segment in self.body[4:]:
            if head.distance_to(segment) < 10:
                return True
        return False
    
    def draw_direction_arrow(self, screen: pygame.Surface):
        """Zeichnet Pfeil der Bewegungsrichtung"""
        head = self.body[0]
        arrow_length = 20
        
        tip_x = head.x + math.cos(self.angle * math.pi / 180) * arrow_length
        tip_y = head.y + math.sin(self.angle * math.pi / 180) * arrow_length
        
        pygame.draw.line(screen, self.head_color, (int(head.x), int(head.y)), (int(tip_x), int(tip_y)), 3)
        
        angle_rad = self.angle * math.pi / 180
        for offset_angle in [-30, 30]:
            back_angle = angle_rad + (offset_angle + 180) * math.pi / 180
            back_x = tip_x + math.cos(back_angle) * 8
            back_y = tip_y + math.sin(back_angle) * 8
            pygame.draw.line(screen, self.head_color, (int(tip_x), int(tip_y)), (int(back_x), int(back_y)), 2)
    
    def draw(self, screen: pygame.Surface):
        """Zeichnet die Snake"""
        # Körper
        for i, segment in enumerate(self.body):
            brightness = max(0.4, 1 - i * 0.015)
            color = tuple(int(c * brightness) for c in self.color)
            pygame.draw.circle(screen, color, (int(segment.x), int(segment.y)), 6)
            pygame.draw.circle(screen, WHITE, (int(segment.x), int(segment.y)), 6, 1)
        
        # Kopf
        pygame.draw.circle(screen, self.head_color, (int(self.body[0].x), int(self.body[0].y)), 8)
        pygame.draw.circle(screen, WHITE, (int(self.body[0].x), int(self.body[0].y)), 8, 2)
        
        # Power-up Shield
        if self.powered_up:
            alpha = int(255 * (self.power_up_time / self.power_up_duration))
            shield_size = 12 + int(3 * math.sin(pygame.time.get_ticks() / 100))
            pygame.draw.circle(screen, self.shield_color, (int(self.body[0].x), int(self.body[0].y)), shield_size, 2)
        
        # Richtungs-Pfeil
        self.draw_direction_arrow(screen)
        
        # Name
        font = pygame.font.Font(None, 18)
        name_text = font.render(self.name, True, self.head_color)
        screen.blit(name_text, (int(self.body[0].x) - 20, int(self.body[0].y) - 35))

# ==================== HAUPTGAME-KLASSE ====================
class SnakeGame:
    """Hauptklasse die das ganze Spiel koordiniert"""
    def __init__(self):
        # Fenster
        self.fullscreen = False
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("🐍 SLIMY SNAKE - Next Generation")
        self.clock = pygame.time.Clock()
        
        # Schriften
        self.font_large = pygame.font.Font(None, 80)
        self.font_medium = pygame.font.Font(None, 45)
        self.font_small = pygame.font.Font(None, 28)
        self.font_tiny = pygame.font.Font(None, 20)
        
        # Spiel-Status
        self.state = GameState.MENU
        self.player_name = "Player1"
        self.player_color = GREEN
        self.available_colors = [GREEN, BLUE, ORANGE, CYAN, PURPLE, NEON_GREEN, NEON_PINK, YELLOW]
        self.color_index = 0
        
        # Sound und Musik
        self.music_loaded = False
        self.sounds = {}
        
        # Spiel-Elemente
        self.player = None
        self.asteroids = []
        self.orbs = []
        self.particles = []
        
        # Stats
        self.load_stats()
        self.load_sounds()
    
    def load_sounds(self):
        """Lädt Sound-Effekte und Musik"""
        try:
            # Versuch Assets zu laden
            if os.path.exists('assets/eat.wav'):
                self.sounds['eat'] = pygame.mixer.Sound('assets/eat.wav')
            if os.path.exists('assets/death.wav'):
                self.sounds['death'] = pygame.mixer.Sound('assets/death.wav')
            if os.path.exists('assets/asteroid.wav'):
                self.sounds['asteroid'] = pygame.mixer.Sound('assets/asteroid.wav')
            if os.path.exists('assets/powerup.wav'):
                self.sounds['powerup'] = pygame.mixer.Sound('assets/powerup.wav')
            
            # Musik
            if os.path.exists('assets/lobby_music.mp3') or os.path.exists('assets/lobby_music.wav'):
                music_file = 'assets/lobby_music.mp3' if os.path.exists('assets/lobby_music.mp3') else 'assets/lobby_music.wav'
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
                self.music_loaded = True
            
            if os.path.exists('assets/gameplay_music.mp3') or os.path.exists('assets/gameplay_music.wav'):
                self.gameplay_music = 'assets/gameplay_music.mp3' if os.path.exists('assets/gameplay_music.mp3') else 'assets/gameplay_music.wav'
        except:
            pass
    
    def play_sound(self, sound_name: str):
        """Spielt einen Sound ab"""
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                pass
    
    def load_stats(self):
        """Lädt Stats"""
        self.stats_file = Path(os.path.expanduser("~")) / ".slimy_snake_stats.json"
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    self.stats = json.load(f)
            except:
                self.stats = self._create_empty_stats()
        else:
            self.stats = self._create_empty_stats()
    
    def _create_empty_stats(self) -> dict:
        """Erstellt leere Stats"""
        return {
            "total_games": 0,
            "highest_score": 0,
            "total_food_eaten": 0,
            "best_player_name": "None",
            "games": []
        }
    
    def save_stats(self, final_length: int):
        """Speichert Stats"""
        self.stats["total_games"] += 1
        self.stats["total_food_eaten"] += max(0, final_length - 1)
        
        if final_length > self.stats["highest_score"]:
            self.stats["highest_score"] = final_length
            self.stats["best_player_name"] = self.player_name
        
        game_data = {
            "player_name": self.player_name,
            "final_length": final_length,
            "timestamp": str(pygame.time.get_ticks())
        }
        self.stats["games"].append(game_data)
        
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except:
            pass
    
    def reset_game(self):
        """Setzt Spiel zurück"""
        self.player = Snake(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, self.player_color, name=self.player_name)
        
        # Erstelle Asteroiden
        self.asteroids = []
        for _ in range(5):
            # Spawn mit Sicherheitsabstand
            safe_spawn = False
            attempts = 0
            while not safe_spawn and attempts < 10:
                ax = random.randint(100, WINDOW_WIDTH - 100)
                ay = random.randint(100, WINDOW_HEIGHT - 100)
                dist = math.sqrt((ax - self.player.get_head().x)**2 + (ay - self.player.get_head().y)**2)
                if dist > SPAWN_SAFETY_RADIUS:
                    safe_spawn = True
                attempts += 1
            
            if safe_spawn:
                size = random.randint(10, 20)
                self.asteroids.append(Asteroid(ax, ay, size))
        
        # Erstelle normale Orbs
        self.orbs = []
        self.spawn_orbs(30)
        
        # Erstelle Power-up Orbs (seltener)
        for _ in range(random.randint(1, 3)):
            self.orbs.append(Orb(random.randint(100, WINDOW_WIDTH - 100), random.randint(100, WINDOW_HEIGHT - 100), is_special=True))
        
        self.particles = []
        self.state = GameState.PLAYING
    
    def spawn_orbs(self, count: int = 1):
        """Spawnt Orbs"""
        for _ in range(count):
            self.orbs.append(Orb(
                random.randint(20, WINDOW_WIDTH - 20),
                random.randint(20, WINDOW_HEIGHT - 20),
                is_special=False
            ))
    
    def handle_mouse_movement(self):
        """Handhabe Mouse-Steuerung"""
        if self.state == GameState.PLAYING and not self.player.dead:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            head = self.player.get_head()
            
            dx = mouse_x - head.x
            dy = mouse_y - head.y
            
            length = math.sqrt(dx**2 + dy**2)
            if length > 5:
                self.player.set_direction(dx / length, dy / length)
    
    def handle_input(self):
        """Handhabe Input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.USERNAME_INPUT
                    elif event.key == pygame.K_s:
                        self.state = GameState.SETTINGS
                    elif event.key == pygame.K_r:
                        self.open_readme()
                    elif event.key == pygame.K_i:
                        self.open_anleitung()
                    elif event.key == pygame.K_q:
                        return False
                
                elif self.state == GameState.USERNAME_INPUT:
                    if event.key == pygame.K_RETURN:
                        self.state = GameState.COLOR_SELECT
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif event.unicode.isprintable() and len(self.player_name) < 15:
                        self.player_name += event.unicode
                
                elif self.state == GameState.COLOR_SELECT:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.color_index = (self.color_index - 1) % len(self.available_colors)
                        self.player_color = self.available_colors[self.color_index]
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.color_index = (self.color_index + 1) % len(self.available_colors)
                        self.player_color = self.available_colors[self.color_index]
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.reset_game()
                
                elif self.state == GameState.SETTINGS:
                    if event.key == pygame.K_f:
                        self.toggle_fullscreen()
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        self.state = GameState.MENU
                
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PAUSED
                
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_m:
                        self.state = GameState.MENU
                
                elif self.state == GameState.DEATH:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.USERNAME_INPUT
                    elif event.key == pygame.K_m:
                        self.state = GameState.MENU
        
        return True
    
    def toggle_fullscreen(self):
        """Toggle Fullscreen"""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    def open_readme(self):
        """Öffne README"""
        readme_path = Path("README.md").absolute()
        if readme_path.exists():
            webbrowser.open(f'file://{readme_path}')
    
    def open_anleitung(self):
        """Öffne Anleitung"""
        anleitung_path = Path("ANLEITUNG.md").absolute()
        if anleitung_path.exists():
            webbrowser.open(f'file://{anleitung_path}')
    
    def update(self):
        """Aktualisiere Spiel-Logik"""
        if self.state == GameState.PLAYING:
            self.handle_mouse_movement()
            
            # Bewege Snake
            self.player.move()
            self.player.update_power_up()
            
            # Update Asteroiden
            for asteroid in self.asteroids:
                asteroid.update()
            
            # Update Orbs
            for orb in self.orbs:
                orb.update()
            
            # ========== ORBS ESSEN ==========
            head = self.player.get_head()
            for orb in self.orbs[:]:
                if not orb.collected and head.distance_to(Point(orb.x, orb.y)) < 15:
                    orb.collected = True
                    
                    if orb.is_special:
                        # Power-up
                        self.player.activate_power_up()
                        self.play_sound('powerup')
                    else:
                        # Normale Orb
                        self.player.grow(2)
                        self.play_sound('eat')
                    
                    self.orbs.remove(orb)
                    self.spawn_orbs(1)
            
            # ========== ASTEROID KOLLISIONEN ==========
            for asteroid in self.asteroids:
                if head.distance_to(Point(asteroid.x, asteroid.y)) < (asteroid.size + 8):
                    if self.player.powered_up:
                        # Asteroid zerstört
                        asteroid.destroyed = True
                        self.play_sound('asteroid')
                        
                        # 45 Orbs droppen
                        for _ in range(45):
                            angle = random.uniform(0, 2 * math.pi)
                            dist = random.uniform(0, asteroid.size)
                            orb_x = asteroid.x + math.cos(angle) * dist
                            orb_y = asteroid.y + math.sin(angle) * dist
                            self.orbs.append(Orb(orb_x, orb_y, is_special=False))
                    else:
                        # Spieler stirbt
                        self.player.dead = True
                        self.save_stats(len(self.player.body))
                        self.state = GameState.DEATH
            
            # Entferne zerstörte Asteroiden
            self.asteroids = [a for a in self.asteroids if not a.destroyed]
            
            # Selbst-Kollision
            if self.player.check_self_collision():
                self.player.dead = True
                self.save_stats(len(self.player.body))
                self.state = GameState.DEATH
    
    def draw_menu(self):
        """Zeichne Hauptmenü"""
        self.screen.fill(DEEP_SPACE)
        
        # Gitter-Hintergrund
        for x in range(0, WINDOW_WIDTH, 60):
            for y in range(0, WINDOW_HEIGHT, 60):
                if (x // 60 + y // 60) % 2 == 0:
                    pygame.draw.rect(self.screen, (20, 20, 40), (x, y, 60, 60))
        
        # Border
        pygame.draw.rect(self.screen, NEON_CYAN, (20, 20, WINDOW_WIDTH - 40, WINDOW_HEIGHT - 40), 5)
        
        # Titel mit Glow-Effekt
        title = self.font_large.render("🐍 SLIMY SNAKE", True, NEON_GREEN)
        subtitle = self.font_medium.render("Next Generation", True, NEON_PINK)
        
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 50))
        self.screen.blit(subtitle, (WINDOW_WIDTH // 2 - subtitle.get_width() // 2, 150))
        
        # Menü-Tasten
        menu_items = [
            ("PRESS SPACE TO START", 300),
            ("PRESS S FOR SETTINGS", 380),
            ("PRESS R FOR README", 460),
            ("PRESS I FOR ANLEITUNG", 540),
            ("PRESS Q TO QUIT", 700),
        ]
        
        for item, y in menu_items:
            text = self.font_small.render(item, True, WHITE)
            self.screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, y))
    
    def draw_username_input(self):
        """Zeichne Username-Input"""
        self.screen.fill(DEEP_SPACE)
        pygame.draw.rect(self.screen, NEON_CYAN, (50, 50, WINDOW_WIDTH - 100, WINDOW_HEIGHT - 100), 3)
        
        title = self.font_large.render("Choose Your Name", True, NEON_GREEN)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 200))
        
        input_text = self.font_medium.render(self.player_name + "_", True, YELLOW)
        self.screen.blit(input_text, (WINDOW_WIDTH // 2 - input_text.get_width() // 2, 350))
        
        hint = self.font_small.render("Press ENTER to continue", True, WHITE)
        self.screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 480))
    
    def draw_color_select(self):
        """Zeichne Farb-Auswahl"""
        self.screen.fill(DEEP_SPACE)
        pygame.draw.rect(self.screen, NEON_CYAN, (50, 50, WINDOW_WIDTH - 100, WINDOW_HEIGHT - 100), 3)
        
        title = self.font_large.render("Choose Your Color", True, NEON_GREEN)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 100))
        
        pygame.draw.circle(self.screen, self.player_color, (WINDOW_WIDTH // 2, 250), 50)
        pygame.draw.circle(self.screen, WHITE, (WINDOW_WIDTH // 2, 250), 50, 3)
        
        colors_per_row = 4
        color_size = 60
        start_x = WINDOW_WIDTH // 2 - (colors_per_row * color_size) // 2
        
        for i, color in enumerate(self.available_colors):
            row = i // colors_per_row
            col = i % colors_per_row
            x = start_x + col * color_size + 30
            y = 380 + row * 100
            
            pygame.draw.circle(self.screen, color, (x, y), 25)
            if color == self.player_color:
                pygame.draw.circle(self.screen, WHITE, (x, y), 25, 4)
            else:
                pygame.draw.circle(self.screen, GRAY, (x, y), 25, 1)
        
        hint = self.font_small.render("← LEFT/RIGHT → to choose | ENTER to start", True, WHITE)
        self.screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 750))
    
    def draw_settings(self):
        """Zeichne Einstellungen"""
        self.screen.fill(DEEP_SPACE)
        pygame.draw.rect(self.screen, NEON_CYAN, (50, 50, WINDOW_WIDTH - 100, WINDOW_HEIGHT - 100), 3)
        
        title = self.font_large.render("⚙️ SETTINGS", True, NEON_GREEN)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 100))
        
        fullscreen_status = "ON ✓" if self.fullscreen else "OFF ✗"
        fs_text = self.font_medium.render(f"Fullscreen: {fullscreen_status}", True, YELLOW)
        self.screen.blit(fs_text, (WINDOW_WIDTH // 2 - fs_text.get_width() // 2, 250))
        
        fs_hint = self.font_small.render("Press F to toggle", True, GRAY)
        self.screen.blit(fs_hint, (WINDOW_WIDTH // 2 - fs_hint.get_width() // 2, 330))
        
        escape_text = self.font_small.render("Press ESC to return to MENU", True, WHITE)
        self.screen.blit(escape_text, (WINDOW_WIDTH // 2 - escape_text.get_width() // 2, 630))
    
    def draw_game(self):
        """Zeichne Spiel"""
        self.screen.fill(DEEP_SPACE)
        
        # Gitter
        for x in range(0, WINDOW_WIDTH, GRID_SIZE * 10):
            pygame.draw.line(self.screen, (30, 30, 60), (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE * 10):
            pygame.draw.line(self.screen, (30, 30, 60), (0, y), (WINDOW_WIDTH, y), 1)
        
        # Border
        pygame.draw.rect(self.screen, BORDER_COLOR, (5, 5, WINDOW_WIDTH - 10, WINDOW_HEIGHT - 10), 5)
        pygame.draw.rect(self.screen, DARK_RED, (3, 3, WINDOW_WIDTH - 6, WINDOW_HEIGHT - 6), 2)
        
        # Asteroiden
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)
        
        # Orbs
        for orb in self.orbs:
            orb.draw(self.screen)
        
        # Snake
        if not self.player.dead:
            self.player.draw(self.screen)
        
        # HUD
        player_length = len(self.player.body)
        player_score = self.font_small.render(f"👤 {self.player_name}: {player_length}", True, self.player_color)
        self.screen.blit(player_score, (10, 10))
        
        fps_text = self.font_tiny.render(f"FPS: {int(self.clock.get_fps())}", True, NEON_GREEN)
        self.screen.blit(fps_text, (10, 40))
        
        # Power-up Timer
        if self.player.powered_up:
            timer_text = self.font_tiny.render(f"⚡ POWERED UP: {int(self.player.power_up_time / FPS)}s", True, NEON_PINK)
            self.screen.blit(timer_text, (10, 70))
    
    def draw_pause(self):
        """Zeichne Pause-Screen"""
        self.draw_game()
        
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.font_large.render("⏸️ PAUSED", True, NEON_PINK)
        self.screen.blit(pause_text, (WINDOW_WIDTH // 2 - pause_text.get_width() // 2, 300))
        
        resume_text = self.font_medium.render("Press ESC to Resume", True, WHITE)
        self.screen.blit(resume_text, (WINDOW_WIDTH // 2 - resume_text.get_width() // 2, 420))
        
        menu_text = self.font_small.render("Press M for Menu", True, GRAY)
        self.screen.blit(menu_text, (WINDOW_WIDTH // 2 - menu_text.get_width() // 2, 520))
    
    def draw_death(self):
        """Zeichne Death-Screen"""
        self.draw_game()
        
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        death_text = self.font_large.render("💀 YOU DIED!", True, RED)
        self.screen.blit(death_text, (WINDOW_WIDTH // 2 - death_text.get_width() // 2, 150))
        
        score_text = self.font_medium.render(f"Final Length: {len(self.player.body)}", True, YELLOW)
        self.screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 300))
        
        # High Score Info
        if len(self.player.body) == self.stats["highest_score"]:
            record_text = self.font_small.render("🏆 NEW HIGH SCORE!", True, NEON_GREEN)
            self.screen.blit(record_text, (WINDOW_WIDTH // 2 - record_text.get_width() // 2, 400))
        
        retry_text = self.font_small.render("Press SPACE to Play Again", True, GREEN)
        self.screen.blit(retry_text, (WINDOW_WIDTH // 2 - retry_text.get_width() // 2, 520))
        
        menu_text = self.font_small.render("Press M for Menu", True, GRAY)
        self.screen.blit(menu_text, (WINDOW_WIDTH // 2 - menu_text.get_width() // 2, 580))
    
    def draw(self):
        """Hauptzeichnen-Funktion"""
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
        
        pygame.display.flip()
    
    def run(self):
        """Hauptgame-Loop"""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

# ==================== EINSTIEGSPUNKT ====================
if __name__ == "__main__":
    game = SnakeGame()
    game.run()
