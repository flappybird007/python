import pygame
import random
import math
import os
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
FPS = 60
GRID_SIZE = 10
SPAWN_SAFETY_RADIUS = 200  # Safe spawn distance

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
BORDER_COLOR = (200, 50, 50)

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


class Snake:
    def __init__(self, x: float, y: float, color: Tuple, is_ai: bool = False, name: str = ""):
        self.body = [Point(x, y)]  # List of points from head to tail
        self.color = color
        self.head_color = self._get_head_color(color)  # Different color for head
        self.direction = Point(1, 0)  # Moving right
        self.next_direction = Point(1, 0)
        self.is_ai = is_ai
        self.name = name
        self.speed = 5
        self.growth_pending = 0
        self.dead = False
        self.angle = 0  # For 360-degree movement
        
    def _get_head_color(self, color: Tuple) -> Tuple:
        """Make head color brighter/different from body"""
        return tuple(min(255, int(c * 1.3)) for c in color)
        
    def move(self):
        if self.dead:
            return
            
        # Update direction - IMPORTANT: only update if next_direction changed
        if self.next_direction.x != 0 or self.next_direction.y != 0:
            # Check that we're not doing a 180-degree turn
            dot_product = self.direction.x * self.next_direction.x + self.direction.y * self.next_direction.y
            if dot_product >= 0:  # Not a 180-degree turn
                self.direction = self.next_direction
        
        # Calculate new head position
        head = self.body[0]
        new_head = Point(
            head.x + self.direction.x * self.speed,
            head.y + self.direction.y * self.speed
        )
        
        # CLAMP to map boundaries (NOT WRAPPING - BOUNDED MAP)
        new_head.x = max(10, min(WINDOW_WIDTH - 10, new_head.x))
        new_head.y = max(10, min(WINDOW_HEIGHT - 10, new_head.y))
        
        self.body.insert(0, new_head)
        
        # Handle growth (grow faster)
        if self.growth_pending > 0:
            self.growth_pending -= 1
        else:
            self.body.pop()
    
    def grow(self, amount: int = 2):  # Grow faster
        self.growth_pending += amount
    
    def set_direction(self, dx: float, dy: float):
        """Set direction only if it's significantly different"""
        length = math.sqrt(dx**2 + dy**2)
        if length > 0.1:  # Only if movement is significant
            # Normalize
            self.next_direction = Point(dx / length, dy / length)
    
    def ai_update(self, food_points: List[Point], other_snakes: List['Snake']):
        if self.dead or not self.is_ai:
            return
        
        head = self.body[0]
        
        # Find nearest food
        nearest_food = None
        nearest_dist = float('inf')
        for food in food_points:
            dist = head.distance_to(food)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest_food = food
        
        # Find threats (other snake heads nearby)
        threat_distance = 200
        threats = []
        for snake in other_snakes:
            if snake != self and not snake.dead:
                dist = head.distance_to(snake.body[0])
                if dist < threat_distance:
                    threats.append((snake.body[0], len(snake.body)))
        
        # AI Decision making - improved
        best_direction = self.direction
        best_score = -float('inf')
        
        # Test 8 directions (360-degree movement)
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            dx = math.cos(rad)
            dy = math.sin(rad)
            
            # Prevent reversing
            dot_product = self.direction.x * dx + self.direction.y * dy
            if dot_product < 0.5:  # More lenient to allow U-turns in tight spaces
                continue
            
            # Calculate test position
            test_point = Point(
                head.x + dx * self.speed * 25,
                head.y + dy * self.speed * 25
            )
            
            # Clamp to bounds
            test_point.x = max(10, min(WINDOW_WIDTH - 10, test_point.x))
            test_point.y = max(10, min(WINDOW_HEIGHT - 10, test_point.y))
            
            score = 0
            
            # Attraction to food
            if nearest_food:
                food_dist = test_point.distance_to(nearest_food)
                score += 150 - (food_dist / 8)
            
            # Strong repulsion from threats (especially larger ones)
            for threat_pos, threat_length in threats:
                threat_dist = test_point.distance_to(threat_pos)
                # Only fear snakes that are longer
                if threat_length > len(self.body):
                    score -= 500 / (threat_dist + 1)
                else:
                    score -= 100 / (threat_dist + 1)
            
            # Bonus for not hitting own body
            collision = False
            for segment in self.body[4:]:
                if test_point.distance_to(segment) < 15:
                    collision = True
                    break
            
            if collision:
                score -= 1000
            
            # Bonus for staying away from walls
            wall_penalty = 0
            if test_point.x < 50:
                wall_penalty += 100
            if test_point.x > WINDOW_WIDTH - 50:
                wall_penalty += 100
            if test_point.y < 50:
                wall_penalty += 100
            if test_point.y > WINDOW_HEIGHT - 50:
                wall_penalty += 100
            score -= wall_penalty
            
            if score > best_score:
                best_score = score
                best_direction = Point(dx, dy)
        
        self.set_direction(best_direction.x, best_direction.y)
    
    def get_head(self) -> Point:
        return self.body[0]
    
    def check_self_collision(self) -> bool:
        head = self.get_head()
        # Only check body segments that are at least 4 segments away
        for segment in self.body[4:]:
            if head.distance_to(segment) < 10:
                return True
        return False
    
    def draw(self, screen: pygame.Surface):
        # Draw body with smooth gradient
        for i, segment in enumerate(self.body):
            brightness = max(0.4, 1 - i * 0.015)
            color = tuple(int(c * brightness) for c in self.color)
            pygame.draw.circle(screen, color, (int(segment.x), int(segment.y)), 6)
            # Add outline for better visibility
            pygame.draw.circle(screen, WHITE, (int(segment.x), int(segment.y)), 6, 1)
        
        # Draw head with bright color
        pygame.draw.circle(screen, self.head_color, (int(self.body[0].x), int(self.body[0].y)), 7)
        pygame.draw.circle(screen, WHITE, (int(self.body[0].x), int(self.body[0].y)), 7, 2)
        
        # Draw name above head
        font = pygame.font.Font(None, 18)
        name_text = font.render(self.name, True, self.head_color)
        screen.blit(name_text, (int(self.body[0].x) - 20, int(self.body[0].y) - 30))


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
        
        self.reset_game()
        self.load_sounds()
    
    def load_sounds(self):
        """Load sound effects"""
        self.sounds = {}
        try:
            pass
        except:
            pass
    
    def play_sound(self, sound_name: str):
        """Play a sound effect safely"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def is_safe_spawn_location(self, x: float, y: float, exclude_snake: 'Snake' = None) -> bool:
        """Check if spawn location is safe (not too close to player)"""
        if exclude_snake:
            dist = exclude_snake.get_head().distance_to(Point(x, y))
            return dist > SPAWN_SAFETY_RADIUS
        return True
    
    def reset_game(self):
        # Player snake with custom name and color
        self.player = Snake(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, self.player_color, 
                           is_ai=False, name=self.player_name)
        
        # AI snakes with random names - SAFE SPAWN
        self.ai_snakes = []
        ai_colors = [BLUE, ORANGE, CYAN, PURPLE, NEON_GREEN, NEON_PINK]
        for i in range(4):  # 4 AI snakes
            # Keep trying to find safe spawn location
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
                self.ai_snakes.append(
                    Snake(spawn_x, spawn_y,
                          ai_colors[i % len(ai_colors)], 
                          is_ai=True, 
                          name=random_name)
                )
        
        self.all_snakes = [self.player] + self.ai_snakes
        self.food_points = []
        self.spawn_food(30)  # More food on map
        
        # Default direction is right
        self.player.direction = Point(1, 0)
        self.player.next_direction = Point(1, 0)
        
        self.state = GameState.PLAYING
    
    def spawn_food(self, count: int = 1):
        for _ in range(count):
            self.food_points.append(Point(
                random.randint(20, WINDOW_WIDTH - 20),
                random.randint(20, WINDOW_HEIGHT - 20)
            ))
    
    def handle_mouse_movement(self):
        """Make snake follow mouse cursor"""
        if self.state == GameState.PLAYING and not self.player.dead:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            head = self.player.get_head()
            
            # Calculate direction to mouse
            dx = mouse_x - head.x
            dy = mouse_y - head.y
            
            # Normalize
            length = math.sqrt(dx**2 + dy**2)
            if length > 5:  # Only update if mouse is far enough
                self.player.set_direction(dx / length, dy / length)
    
    def handle_input(self):
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
        if self.state == GameState.PLAYING:
            # Handle mouse movement for smooth control
            self.handle_mouse_movement()
            
            # Move snakes
            for snake in self.all_snakes:
                snake.move()
            
            # Update AI
            for ai_snake in self.ai_snakes:
                ai_snake.ai_update(self.food_points, self.all_snakes)
            
            # Check food collision
            for snake in self.all_snakes:
                if not snake.dead:
                    head = snake.get_head()
                    for food in self.food_points[:]:
                        if head.distance_to(food) < 15:
                            snake.grow(2)  # Grow faster
                            self.food_points.remove(food)
                            self.spawn_food(1)
                            self.play_sound('eat')
            
            # Check snake collisions - CRITICAL FIX: Only head-to-body collisions
            for snake in self.all_snakes:
                if not snake.dead:
                    head = snake.get_head()
                    
                    # Check collision with other snakes' bodies ONLY
                    for other_snake in self.all_snakes:
                        if other_snake == snake or other_snake.dead:
                            continue
                        
                        # ONLY check body segments (skip index 0 which is head)
                        # Start from index 1 to skip the head
                        for i in range(1, len(other_snake.body)):
                            segment = other_snake.body[i]
                            collision_dist = head.distance_to(segment)
                            
                            # STRICT collision detection
                            if collision_dist < 10:  # Stricter threshold
                                snake.dead = True
                                # Drop food where snake died
                                for _ in range(len(snake.body) // 5):
                                    self.food_points.append(Point(
                                        head.x + random.randint(-30, 30),
                                        head.y + random.randint(-30, 30)
                                    ))
                                self.play_sound('death')
                                break
                        
                        if snake.dead:
                            break
            
            # Check self collision - VERY STRICT
            for snake in self.all_snakes:
                if not snake.dead and snake.check_self_collision():
                    snake.dead = True
                    self.play_sound('death')
            
            # Check if player is dead
            if self.player.dead:
                self.state = GameState.DEATH
    
    def draw_menu(self):
        # Fancy background
        self.screen.fill(BLACK)
        
        # Draw decorative background pattern
        for x in range(0, WINDOW_WIDTH, 50):
            for y in range(0, WINDOW_HEIGHT, 50):
                if (x + y) % 100 == 0:
                    pygame.draw.rect(self.screen, DARK_GRAY, (x, y, 50, 50))
        
        title = self.font_large.render("🐍 SLIMY SNAKE", True, NEON_GREEN)
        subtitle = self.font_medium.render("Multiplayer Edition", True, NEON_PINK)
        
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 50))
        self.screen.blit(subtitle, (WINDOW_WIDTH // 2 - subtitle.get_width() // 2, 150))
        
        # Instructions with better styling
        instructions = [
            "🖱️  MOVE MOUSE to control your snake",
            "🍕 Eat food (dots) to grow bigger",
            "⚔️  Avoid other snakes' bodies",
            "💪 Your BODY doesn't hurt - only hitting bodies = DEATH",
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
        self.screen.fill(BLACK)
        
        title = self.font_large.render("Choose Your Name", True, NEON_GREEN)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 200))
        
        input_text = self.font_medium.render(self.player_name + "_", True, YELLOW)
        self.screen.blit(input_text, (WINDOW_WIDTH // 2 - input_text.get_width() // 2, 350))
        
        hint = self.font_small.render("Press ENTER to continue", True, WHITE)
        self.screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 480))
    
    def draw_color_select(self):
        self.screen.fill(BLACK)
        
        title = self.font_large.render("Choose Your Color", True, NEON_GREEN)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 100))
        
        # Display color preview
        pygame.draw.circle(self.screen, self.player_color, (WINDOW_WIDTH // 2, 250), 50)
        pygame.draw.circle(self.screen, WHITE, (WINDOW_WIDTH // 2, 250), 50, 3)
        
        # Display all colors
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
        self.screen.fill(BLACK)
        
        # Draw decorative grid background
        for x in range(0, WINDOW_WIDTH, GRID_SIZE * 10):
            pygame.draw.line(self.screen, DARK_GRAY, (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE * 10):
            pygame.draw.line(self.screen, DARK_GRAY, (0, y), (WINDOW_WIDTH, y), 1)
        
        # Draw map border (BOUNDED MAP)
        pygame.draw.rect(self.screen, BORDER_COLOR, (5, 5, WINDOW_WIDTH - 10, WINDOW_HEIGHT - 10), 3)
        
        # Draw food with glow effect
        for food in self.food_points:
            pygame.draw.circle(self.screen, YELLOW, (int(food.x), int(food.y)), 4)
            pygame.draw.circle(self.screen, ORANGE, (int(food.x), int(food.y)), 4, 1)
        
        # Draw snakes
        for snake in self.all_snakes:
            if not snake.dead:
                snake.draw(self.screen)
        
        # Draw HUD / Scoreboard
        player_length = len(self.player.body)
        player_score = self.font_small.render(f"👤 {self.player_name}: {player_length}", True, self.player_color)
        self.screen.blit(player_score, (10, 10))
        
        # Draw scoreboard
        scoreboard_y = 50
        self.screen.blit(self.font_tiny.render("LEADERBOARD", True, NEON_GREEN), (10, scoreboard_y))
        
        # Sort snakes by length
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
        
        fps_text = self.font_tiny.render(f"FPS: {int(self.clock.get_fps())}", True, GRAY)
        self.screen.blit(fps_text, (10, WINDOW_HEIGHT - 30))
    
    def draw_pause(self):
        self.draw_game()
        
        # Semi-transparent overlay
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
        self.draw_game()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        death_text = self.font_large.render("💀 YOU DIED!", True, RED)
        self.screen.blit(death_text, (WINDOW_WIDTH // 2 - death_text.get_width() // 2, 150))
        
        score_text = self.font_medium.render(f"Final Length: {len(self.player.body)}", True, YELLOW)
        self.screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 300))
        
        # Find top killer
        top_snake = max((s for s in self.ai_snakes if not s.dead), key=lambda s: len(s.body), default=None)
        if top_snake:
            killer_text = self.font_small.render(f"🏆 Winner: {top_snake.name} ({len(top_snake.body)})", True, NEON_GREEN)
            self.screen.blit(killer_text, (WINDOW_WIDTH // 2 - killer_text.get_width() // 2, 400))
        
        retry_text = self.font_small.render("Press SPACE to Play Again", True, GREEN)
        self.screen.blit(retry_text, (WINDOW_WIDTH // 2 - retry_text.get_width() // 2, 520))
        
        menu_text = self.font_small.render("Press M for Menu", True, GRAY)
        self.screen.blit(menu_text, (WINDOW_WIDTH // 2 - menu_text.get_width() // 2, 580))
    
    def draw(self):
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
