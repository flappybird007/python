import pygame
import random
import math
import os
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
FPS = 60
GRID_SIZE = 10
SPAWN_SAFETY_RADIUS = 200

# Colors
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
BORDER_COLOR = (255, 0, 0)  # Bright red border
DARK_RED = (139, 0, 0)

# AI Names Pool
AI_NAMES = [
    "🤖 RoboNinja", "💀 DeathViper", "⚡ ThunderSnake", "🔥 FlameKing",
    "👾 PixelMonster", "🎮 GameMaster", "⚔️ Warrior", "🌟 StarSlayer",
    "🐉 DragonFury", "🍕 PizzaHunter", "🎪 JokeySnake", "🎸 RockStar",
    "🚀 SpaceSnake", "🌈 RainbowViper", "💎 DiamondSlayer", "🏆 ChampionKing"
]

# Game States
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    DEATH = 4
    USERNAME_INPUT = 5
    COLOR_SELECT = 6

@dataclass
class Point:
    x: float
    y: float
    
    def distance_to(self, other: 'Point') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


class Particle:
    """Visual effect particles"""
    def __init__(self, x: float, y: float, dx: float, dy: float, lifetime: int, color: Tuple):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = color
    
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1
    
    def draw(self, screen: pygame.Surface):
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            size = max(1, int(5 * (self.lifetime / self.max_lifetime)))
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)


class Snake:
    def __init__(self, x: float, y: float, color: Tuple, is_ai: bool = False, name: str = "", size_variation: float = 1.0):
        self.body = [Point(x, y)]
        self.color = color
        self.head_color = self._get_head_color(color)
        self.direction = Point(1, 0)
        self.next_direction = Point(1, 0)
        self.is_ai = is_ai
        self.name = name
        self.speed = 4.5
        self.growth_pending = 0
        self.dead = False
        self.angle = 0
        self.size_variation = size_variation  # For AI snakes variability
        self.base_length = int(8 * size_variation)  # Variable starting length
        
        # Spawn with variable length for AI snakes
        if is_ai and size_variation != 1.0:
            for _ in range(self.base_length):
                self.body.append(Point(x - _, y))
        
        self.particles = []
        
    def _get_head_color(self, color: Tuple) -> Tuple:
        """Make head color brighter and more distinctive"""
        return tuple(min(255, int(c * 1.5)) for c in color)
    
    def add_particle_effect(self, count: int = 5):
        """Create visual particle effects"""
        head = self.body[0]
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            particle = Particle(head.x, head.y, dx, dy, 30, self.head_color)
            self.particles.append(particle)
    
    def update_particles(self):
        """Update and clean up particles"""
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)
    
    def draw_particles(self, screen: pygame.Surface):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(screen)
    
    def move(self):
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
        
        # Bounce off walls
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
        """Grow faster"""
        self.growth_pending += amount
        self.add_particle_effect(3)
    
    def set_direction(self, dx: float, dy: float):
        """Smooth 360-degree movement"""
        length = math.sqrt(dx**2 + dy**2)
        if length > 0.1:
            self.next_direction = Point(dx / length, dy / length)
            self.angle = math.degrees(math.atan2(dy, dx))
    
    def ai_update(self, food_points: List[Point], other_snakes: List['Snake']):
        """Improved AI with better evasion and pathfinding"""
        if self.dead or not self.is_ai:
            return
        
        head = self.body[0]
        
        nearest_food = None
        nearest_dist = float('inf')
        for food in food_points:
            dist = head.distance_to(food)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest_food = food
        
        threat_distance = 250
        threats = []
        for snake in other_snakes:
            if snake != self and not snake.dead:
                dist = head.distance_to(snake.body[0])
                if dist < threat_distance:
                    threats.append((snake.body[0], len(snake.body)))
        
        best_direction = self.direction
        best_score = -float('inf')
        
        # Test 16 directions for better AI (360-degree movement)
        # FIX: Convert 22.5 to int for range() - it doesn't accept floats
        for angle in range(0, 360, 23):
            rad = math.radians(angle)
            dx = math.cos(rad)
            dy = math.sin(rad)
            
            dot_product = self.direction.x * dx + self.direction.y * dy
            if dot_product < 0.3:
                continue
            
            test_point = Point(
                head.x + dx * self.speed * 25,
                head.y + dy * self.speed * 25
            )
            
            test_point.x = max(10, min(WINDOW_WIDTH - 10, test_point.x))
            test_point.y = max(10, min(WINDOW_HEIGHT - 10, test_point.y))
            
            score = 0
            
            if nearest_food:
                food_dist = test_point.distance_to(nearest_food)
                score += 200 - (food_dist / 6)
            
            for threat_pos, threat_length in threats:
                threat_dist = test_point.distance_to(threat_pos)
                if threat_length > len(self.body):
                    score -= 600 / (threat_dist + 1)
                else:
                    score -= 150 / (threat_dist + 1)
            
            collision = False
            for segment in self.body[4:]:
                if test_point.distance_to(segment) < 15:
                    collision = True
                    break
            
            if collision:
                score -= 1200
            
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
            
            if score > best_score:
                best_score = score
                best_direction = Point(dx, dy)
        
        self.set_direction(best_direction.x, best_direction.y)
    
    def get_head(self) -> Point:
        return self.body[0]
    
    def check_self_collision(self) -> bool:
        head = self.get_head()
        for segment in self.body[4:]:
            if head.distance_to(segment) < 10:
                return True
        return False
    
    def draw_direction_arrow(self, screen: pygame.Surface):
        """Draw arrow indicating movement direction"""
        head = self.body[0]
        arrow_length = 20
        
        # Arrow tip
        tip_x = head.x + math.cos(self.angle * math.pi / 180) * arrow_length
        tip_y = head.y + math.sin(self.angle * math.pi / 180) * arrow_length
        
        pygame.draw.line(screen, self.head_color, (int(head.x), int(head.y)), (int(tip_x), int(tip_y)), 3)
        
        # Arrow head
        angle_rad = self.angle * math.pi / 180
        for offset_angle in [-30, 30]:
            back_angle = angle_rad + (offset_angle + 180) * math.pi / 180
            back_x = tip_x + math.cos(back_angle) * 8
            back_y = tip_y + math.sin(back_angle) * 8
            pygame.draw.line(screen, self.head_color, (int(tip_x), int(tip_y)), (int(back_x), int(back_y)), 2)
    
    def draw(self, screen: pygame.Surface):
        """Draw snake with gradient and effects"""
        for i, segment in enumerate(self.body):
            brightness = max(0.4, 1 - i * 0.015)
            color = tuple(int(c * brightness) for c in self.color)
            pygame.draw.circle(screen, color, (int(segment.x), int(segment.y)), 6)
            pygame.draw.circle(screen, WHITE, (int(segment.x), int(segment.y)), 6, 1)
        
        # Brighter head
        pygame.draw.circle(screen, self.head_color, (int(self.body[0].x), int(self.body[0].y)), 8)
        pygame.draw.circle(screen, WHITE, (int(self.body[0].x), int(self.body[0].y)), 8, 2)
        
        # Draw direction arrow
        self.draw_direction_arrow(screen)
        
        # Draw name
        font = pygame.font.Font(None, 18)
        name_text = font.render(self.name, True, self.head_color)
        screen.blit(name_text, (int(self.body[0].x) - 20, int(self.body[0].y) - 35))
        
        # Draw particles
        self.draw_particles(screen)


class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("🐍 SLIMY SNAKE - Multiplayer Edition")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 80)
        self.font_medium = pygame.font.Font(None, 45)
        self.font_small = pygame.font.Font(None, 28)
        self.font_tiny = pygame.font.Font(None, 20)
        
        self.state = GameState.MENU
        self.player_name = "Player1"
        self.player_color = GREEN
        self.available_colors = [GREEN, BLUE, ORANGE, CYAN, PURPLE, NEON_GREEN, NEON_PINK, YELLOW]
        self.color_index = 0
        
        self.music_loaded = False
        self.eat_sound_loaded = False
        self.death_sound_loaded = False
        
        self.reset_game()
        self.load_sounds()
    
    def load_sounds(self):
        """Load sound effects"""
        self.sounds = {}
        try:
            # Try to load actual sounds if they exist
            if os.path.exists('assets/eat.wav'):
                self.sounds['eat'] = pygame.mixer.Sound('assets/eat.wav')
                self.eat_sound_loaded = True
            if os.path.exists('assets/death.wav'):
                self.sounds['death'] = pygame.mixer.Sound('assets/death.wav')
                self.death_sound_loaded = True
            if os.path.exists('assets/music.mp3') or os.path.exists('assets/music.wav'):
                music_file = 'assets/music.mp3' if os.path.exists('assets/music.mp3') else 'assets/music.wav'
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
                self.music_loaded = True
        except:
            pass
    
    def play_sound(self, sound_name: str):
        """Play a sound effect safely"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def is_safe_spawn_location(self, x: float, y: float, exclude_snake: 'Snake' = None) -> bool:
        """Check if spawn location is safe"""
        if exclude_snake:
            dist = exclude_snake.get_head().distance_to(Point(x, y))
            return dist > SPAWN_SAFETY_RADIUS
        return True
    
    def reset_game(self):
        """Reset game state"""
        self.player = Snake(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, self.player_color, 
                           is_ai=False, name=self.player_name)
        
        self.ai_snakes = []
        ai_colors = [BLUE, ORANGE, CYAN, PURPLE, NEON_GREEN, NEON_PINK]
        
        for i in range(4):
            safe_spawn = False
            attempts = 0
            while not safe_spawn and attempts < 10:
                spawn_x = random.randint(100, WINDOW_WIDTH - 100)
                spawn_y = random.randint(100, WINDOW_HEIGHT - 100)
                if self.is_safe_spawn_location(spawn_x, spawn_y, self.player):
                    safe_spawn = True
                attempts += 1
            
            if safe_spawn:
                random_name = random.choice(AI_NAMES)
                # Variable AI snake sizes
                size_variation = random.uniform(0.7, 1.3)
                self.ai_snakes.append(
                    Snake(spawn_x, spawn_y,
                          ai_colors[i % len(ai_colors)], 
                          is_ai=True, 
                          name=random_name,
                          size_variation=size_variation)
                )
        
        self.all_snakes = [self.player] + self.ai_snakes
        self.food_points = []
        self.spawn_food(35)
        
        self.player.direction = Point(1, 0)
        self.player.next_direction = Point(1, 0)
        
        self.state = GameState.PLAYING
    
    def spawn_food(self, count: int = 1):
        """Spawn food on map"""
        for _ in range(count):
            self.food_points.append(Point(
                random.randint(20, WINDOW_WIDTH - 20),
                random.randint(20, WINDOW_HEIGHT - 20)
            ))
    
    def handle_mouse_movement(self):
        """Mouse-following 360-degree control"""
        if self.state == GameState.PLAYING and not self.player.dead:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            head = self.player.get_head()
            
            dx = mouse_x - head.x
            dy = mouse_y - head.y
            
            length = math.sqrt(dx**2 + dy**2)
            if length > 5:
                self.player.set_direction(dx / length, dy / length)
    
    def handle_input(self):
        """Handle user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.USERNAME_INPUT
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
    
    def update(self):
        """Update game logic"""
        if self.state == GameState.PLAYING:
            self.handle_mouse_movement()
            
            for snake in self.all_snakes:
                snake.move()
            
            for ai_snake in self.ai_snakes:
                ai_snake.ai_update(self.food_points, self.all_snakes)
            
            # Food collision
            for snake in self.all_snakes:
                if not snake.dead:
                    head = snake.get_head()
                    for food in self.food_points[:]:
                        if head.distance_to(food) < 15:
                            snake.grow(2)
                            self.food_points.remove(food)
                            self.spawn_food(1)
                            self.play_sound('eat')
            
            # Head-to-body collision (ONLY head touches other bodies)
            for snake in self.all_snakes:
                if not snake.dead:
                    head = snake.get_head()
                    
                    for other_snake in self.all_snakes:
                        if other_snake == snake or other_snake.dead:
                            continue
                        
                        # Only check body segments (skip head at index 0)
                        for i in range(1, len(other_snake.body)):
                            segment = other_snake.body[i]
                            if head.distance_to(segment) < 10:
                                snake.dead = True
                                snake.add_particle_effect(10)
                                
                                # Drop food
                                for _ in range(len(snake.body) // 5):
                                    self.food_points.append(Point(
                                        head.x + random.randint(-30, 30),
                                        head.y + random.randint(-30, 30)
                                    ))
                                self.play_sound('death')
                                break
                        
                        if snake.dead:
                            break
            
            # Self collision
            for snake in self.all_snakes:
                if not snake.dead and snake.check_self_collision():
                    snake.dead = True
                    snake.add_particle_effect(10)
                    self.play_sound('death')
            
            if self.player.dead:
                self.state = GameState.DEATH
    
    def draw_menu(self):
        """Draw elegant main menu"""
        self.screen.fill(BLACK)
        
        # Futuristic background pattern
        for x in range(0, WINDOW_WIDTH, 60):
            for y in range(0, WINDOW_HEIGHT, 60):
                if (x // 60 + y // 60) % 2 == 0:
                    pygame.draw.rect(self.screen, DARK_GRAY, (x, y, 60, 60))
        
        # Neon border
        pygame.draw.rect(self.screen, NEON_CYAN, (20, 20, WINDOW_WIDTH - 40, WINDOW_HEIGHT - 40), 5)
        
        title = self.font_large.render("🐍 SLIMY SNAKE", True, NEON_GREEN)
        subtitle = self.font_medium.render("Multiplayer Edition", True, NEON_PINK)
        
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 50))
        self.screen.blit(subtitle, (WINDOW_WIDTH // 2 - subtitle.get_width() // 2, 150))
        
        instructions = [
            "🖱️  MOVE MOUSE to control your snake (360° movement)",
            "🍕 Eat food (dots) to grow bigger",
            "⚔️  Avoid other snakes' bodies",
            "💪 Your BODY doesn't hurt - only head-to-body collision = DEATH",
            "🏆 Become the longest snake!",
            "",
            "PRESS SPACE TO START",
            "PRESS Q TO QUIT"
        ]
        
        y = 300
        for instruction in instructions:
            if instruction:
                text = self.font_small.render(instruction, True, WHITE)
                self.screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, y))
            y += 50
    
    def draw_username_input(self):
        """Draw username input screen"""
        self.screen.fill(BLACK)
        
        pygame.draw.rect(self.screen, NEON_CYAN, (50, 50, WINDOW_WIDTH - 100, WINDOW_HEIGHT - 100), 3)
        
        title = self.font_large.render("Choose Your Name", True, NEON_GREEN)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 200))
        
        input_text = self.font_medium.render(self.player_name + "_", True, YELLOW)
        self.screen.blit(input_text, (WINDOW_WIDTH // 2 - input_text.get_width() // 2, 350))
        
        hint = self.font_small.render("Press ENTER to continue", True, WHITE)
        self.screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 480))
    
    def draw_color_select(self):
        """Draw color selection screen"""
        self.screen.fill(BLACK)
        
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
    
    def draw_game(self):
        """Draw game scene"""
        self.screen.fill(BLACK)
        
        # Futuristic grid background
        for x in range(0, WINDOW_WIDTH, GRID_SIZE * 10):
            pygame.draw.line(self.screen, DARK_GRAY, (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE * 10):
            pygame.draw.line(self.screen, DARK_GRAY, (0, y), (WINDOW_WIDTH, y), 1)
        
        # Bright red border with glow effect
        pygame.draw.rect(self.screen, BORDER_COLOR, (5, 5, WINDOW_WIDTH - 10, WINDOW_HEIGHT - 10), 5)
        pygame.draw.rect(self.screen, DARK_RED, (3, 3, WINDOW_WIDTH - 6, WINDOW_HEIGHT - 6), 2)
        
        # Food with glow
        for food in self.food_points:
            pygame.draw.circle(self.screen, YELLOW, (int(food.x), int(food.y)), 5)
            pygame.draw.circle(self.screen, ORANGE, (int(food.x), int(food.y)), 5, 2)
        
        # Draw snakes
        for snake in self.all_snakes:
            if not snake.dead:
                snake.draw(self.screen)
        
        # HUD
        player_length = len(self.player.body)
        player_score = self.font_small.render(f"👤 {self.player_name}: {player_length}", True, self.player_color)
        self.screen.blit(player_score, (10, 10))
        
        # FPS in top left
        fps_text = self.font_tiny.render(f"FPS: {int(self.clock.get_fps())}", True, NEON_GREEN)
        self.screen.blit(fps_text, (10, 40))
        
        # Leaderboard
        scoreboard_y = 70
        self.screen.blit(self.font_tiny.render("LEADERBOARD", True, NEON_GREEN), (10, scoreboard_y))
        
        sorted_snakes = sorted(self.all_snakes, key=lambda s: len(s.body), reverse=True)
        scoreboard_y += 30
        for i, snake in enumerate(sorted_snakes):
            if not snake.dead:
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
                score_text = self.font_tiny.render(
                    f"{medal} {snake.name}: {len(snake.body)}", 
                    True, 
                    snake.head_color
                )
                self.screen.blit(score_text, (10, scoreboard_y))
                scoreboard_y += 25
    
    def draw_pause(self):
        """Draw pause screen"""
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
        """Draw death screen"""
        self.draw_game()
        
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        death_text = self.font_large.render("💀 YOU DIED!", True, RED)
        self.screen.blit(death_text, (WINDOW_WIDTH // 2 - death_text.get_width() // 2, 150))
        
        score_text = self.font_medium.render(f"Final Length: {len(self.player.body)}", True, YELLOW)
        self.screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 300))
        
        top_snake = max((s for s in self.ai_snakes if not s.dead), key=lambda s: len(s.body), default=None)
        if top_snake:
            killer_text = self.font_small.render(f"🏆 Winner: {top_snake.name} ({len(top_snake.body)})", True, NEON_GREEN)
            self.screen.blit(killer_text, (WINDOW_WIDTH // 2 - killer_text.get_width() // 2, 400))
        
        retry_text = self.font_small.render("Press SPACE to Play Again", True, GREEN)
        self.screen.blit(retry_text, (WINDOW_WIDTH // 2 - retry_text.get_width() // 2, 520))
        
        menu_text = self.font_small.render("Press M for Menu", True, GRAY)
        self.screen.blit(menu_text, (WINDOW_WIDTH // 2 - menu_text.get_width() // 2, 580))
    
    def draw(self):
        """Main draw function"""
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.USERNAME_INPUT:
            self.draw_username_input()
        elif self.state == GameState.COLOR_SELECT:
            self.draw_color_select()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.PAUSED:
            self.draw_pause()
        elif self.state == GameState.DEATH:
            self.draw_death()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()


if __name__ == "__main__":
    game = SnakeGame()
    game.run()
