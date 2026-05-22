import pygame
import random
import math
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60
GRID_SIZE = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 100, 255)
YELLOW = (255, 255, 50)
PURPLE = (200, 50, 200)
CYAN = (50, 255, 255)
ORANGE = (255, 165, 50)
GRAY = (100, 100, 100)

# Game States
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    DEATH = 4

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
        self.direction = Point(1, 0)  # Moving right
        self.next_direction = Point(1, 0)
        self.is_ai = is_ai
        self.name = name
        self.speed = 4
        self.growth_pending = 0
        self.dead = False
        
    def move(self):
        if self.dead:
            return
            
        # Update direction
        self.direction = self.next_direction
        
        # Calculate new head position
        head = self.body[0]
        new_head = Point(
            head.x + self.direction.x * self.speed,
            head.y + self.direction.y * self.speed
        )
        
        # Wrap around screen
        new_head.x = new_head.x % WINDOW_WIDTH
        new_head.y = new_head.y % WINDOW_HEIGHT
        
        self.body.insert(0, new_head)
        
        # Handle growth
        if self.growth_pending > 0:
            self.growth_pending -= 1
        else:
            self.body.pop()
    
    def grow(self, amount: int = 1):
        self.growth_pending += amount
    
    def set_direction(self, dx: float, dy: float):
        # Prevent 180-degree turns
        if (dx, dy) != (-self.direction.x, -self.direction.y):
            self.next_direction = Point(dx, dy)
    
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
        threat_distance = 150
        threats = []
        for snake in other_snakes:
            if snake != self and not snake.dead:
                dist = head.distance_to(snake.body[0])
                if dist < threat_distance:
                    threats.append(snake.body[0])
        
        # AI Decision making
        best_direction = self.direction
        best_score = -float('inf')
        
        # Test 4 directions
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            # Prevent reversing
            if (dx, dy) == (-self.direction.x, -self.direction.y):
                continue
            
            # Calculate test position
            test_point = Point(
                head.x + dx * self.speed * 20,
                head.y + dy * self.speed * 20
            )
            test_point.x = test_point.x % WINDOW_WIDTH
            test_point.y = test_point.y % WINDOW_HEIGHT
            
            score = 0
            
            # Attraction to food
            if nearest_food:
                food_dist = test_point.distance_to(nearest_food)
                score += 100 - (food_dist / 10)
            
            # Repulsion from threats
            for threat in threats:
                threat_dist = test_point.distance_to(threat)
                score -= 200 / (threat_dist + 1)
            
            # Bonus for not hitting own body
            collision = False
            for segment in self.body[4:]:  # Check from 4 segments back
                if test_point.distance_to(segment) < 15:
                    collision = True
                    break
            
            if collision:
                score -= 500
            
            if score > best_score:
                best_score = score
                best_direction = Point(dx, dy)
        
        self.set_direction(best_direction.x, best_direction.y)
    
    def get_head(self) -> Point:
        return self.body[0]
    
    def check_self_collision(self) -> bool:
        head = self.get_head()
        for segment in self.body[4:]:
            if head.distance_to(segment) < 12:
                return True
        return False
    
    def draw(self, screen: pygame.Surface):
        # Draw body
        for i, segment in enumerate(self.body):
            # Fade color slightly for tail
            brightness = max(0.3, 1 - i * 0.02)
            color = tuple(int(c * brightness) for c in self.color)
            pygame.draw.circle(screen, color, (int(segment.x), int(segment.y)), 5)
        
        # Draw head
        pygame.draw.circle(screen, self.color, (int(self.body[0].x), int(self.body[0].y)), 6)
        
        # Draw name above head if AI
        if self.is_ai:
            font = pygame.font.Font(None, 20)
            name_text = font.render(self.name, True, self.color)
            screen.blit(name_text, (int(self.body[0].x) - 15, int(self.body[0].y) - 25))


class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("🐍 Slimy Snake - Like Slither.io!")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 60)
        self.font_medium = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 25)
        self.font_tiny = pygame.font.Font(None, 18)
        
        self.state = GameState.MENU
        self.reset_game()
    
    def reset_game(self):
        # Player snake
        self.player = Snake(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, GREEN, is_ai=False, name="YOU")
        
        # AI snakes
        self.ai_snakes = [
            Snake(random.randint(100, WINDOW_WIDTH - 100),
                  random.randint(100, WINDOW_HEIGHT - 100),
                  BLUE, is_ai=True, name="Bot-Red"),
            Snake(random.randint(100, WINDOW_WIDTH - 100),
                  random.randint(100, WINDOW_HEIGHT - 100),
                  ORANGE, is_ai=True, name="Bot-Orange"),
            Snake(random.randint(100, WINDOW_WIDTH - 100),
                  random.randint(100, WINDOW_HEIGHT - 100),
                  CYAN, is_ai=True, name="Bot-Cyan"),
        ]
        
        self.all_snakes = [self.player] + self.ai_snakes
        self.food_points = []
        self.spawn_food(20)  # Initial food
        
        self.state = GameState.PLAYING
    
    def spawn_food(self, count: int = 1):
        for _ in range(count):
            self.food_points.append(Point(
                random.randint(20, WINDOW_WIDTH - 20),
                random.randint(20, WINDOW_HEIGHT - 20)
            ))
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        return False
                
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PAUSED
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.player.set_direction(0, -1)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.player.set_direction(0, 1)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.player.set_direction(-1, 0)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.player.set_direction(1, 0)
                
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_m:
                        self.state = GameState.MENU
                
                elif self.state == GameState.DEATH:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                    elif event.key == pygame.K_m:
                        self.state = GameState.MENU
        
        return True
    
    def update(self):
        if self.state == GameState.PLAYING:
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
                            snake.grow(1)
                            self.food_points.remove(food)
                            self.spawn_food(1)
            
            # Check snake collisions (head-to-body)
            for snake in self.all_snakes:
                if not snake.dead:
                    head = snake.get_head()
                    
                    # Check collision with other snakes
                    for other_snake in self.all_snakes:
                        if other_snake == snake or other_snake.dead:
                            continue
                        
                        for i, segment in enumerate(other_snake.body):
                            if i == 0:  # Skip head (head-to-head is both die)
                                continue
                            if head.distance_to(segment) < 12:
                                snake.dead = True
                                # Drop points where snake died
                                for _ in range(len(snake.body) // 5):
                                    self.food_points.append(Point(
                                        head.x + random.randint(-30, 30),
                                        head.y + random.randint(-30, 30)
                                    ))
                                break
            
            # Head-to-head collisions (both die)
            for i, snake1 in enumerate(self.all_snakes):
                for snake2 in self.all_snakes[i+1:]:
                    if not snake1.dead and not snake2.dead:
                        if snake1.get_head().distance_to(snake2.get_head()) < 15:
                            snake1.dead = True
                            snake2.dead = True
            
            # Check self collision
            for snake in self.all_snakes:
                if not snake.dead and snake.check_self_collision():
                    snake.dead = True
            
            # Check if player is dead
            if self.player.dead:
                self.state = GameState.DEATH
    
    def draw_menu(self):
        self.screen.fill(BLACK)
        
        title = self.font_large.render("🐍 SLIMY SNAKE", True, GREEN)
        subtitle = self.font_medium.render("Like Slither.io!", True, YELLOW)
        
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 100))
        self.screen.blit(subtitle, (WINDOW_WIDTH // 2 - subtitle.get_width() // 2, 180))
        
        # Instructions
        instructions = [
            "ARROW KEYS or WASD to move",
            "Eat food (yellow dots) to grow",
            "Avoid other snakes' bodies",
            "Head-to-head collisions = both die!",
            "Grow larger to become stronger",
            "ESC to pause during game",
            "",
            "PRESS SPACE TO START",
            "PRESS Q TO QUIT"
        ]
        
        y = 300
        for instruction in instructions:
            if instruction:
                text = self.font_tiny.render(instruction, True, WHITE)
                self.screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, y))
            y += 40
    
    def draw_game(self):
        self.screen.fill(BLACK)
        
        # Draw grid background
        for x in range(0, WINDOW_WIDTH, GRID_SIZE * 5):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE * 5):
            pygame.draw.line(self.screen, GRAY, (0, y), (WINDOW_WIDTH, y), 1)
        
        # Draw food
        for food in self.food_points:
            pygame.draw.circle(self.screen, YELLOW, (int(food.x), int(food.y)), 3)
        
        # Draw snakes
        for snake in self.all_snakes:
            if not snake.dead:
                snake.draw(self.screen)
        
        # Draw HUD
        player_length = len(self.player.body)
        player_score = self.font_small.render(f"LENGTH: {player_length}", True, GREEN)
        self.screen.blit(player_score, (10, 10))
        
        fps_text = self.font_tiny.render(f"FPS: {int(self.clock.get_fps())}", True, WHITE)
        self.screen.blit(fps_text, (10, 40))
        
        # Draw other snakes' lengths
        y_offset = 70
        for ai_snake in self.ai_snakes:
            if not ai_snake.dead:
                color_text = self.font_tiny.render(
                    f"{ai_snake.name}: {len(ai_snake.body)}", 
                    True, 
                    ai_snake.color
                )
                self.screen.blit(color_text, (10, y_offset))
                y_offset += 25
    
    def draw_pause(self):
        self.draw_game()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.font_large.render("PAUSED", True, YELLOW)
        self.screen.blit(pause_text, (WINDOW_WIDTH // 2 - pause_text.get_width() // 2, 300))
        
        resume_text = self.font_medium.render("Press ESC to Resume", True, WHITE)
        self.screen.blit(resume_text, (WINDOW_WIDTH // 2 - resume_text.get_width() // 2, 400))
        
        menu_text = self.font_small.render("Press M for Menu", True, GRAY)
        self.screen.blit(menu_text, (WINDOW_WIDTH // 2 - menu_text.get_width() // 2, 480))
    
    def draw_death(self):
        self.draw_game()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Find killer
        killer = "Unknown"
        for snake in self.ai_snakes:
            if not snake.dead:
                killer = snake.name
                break
        
        death_text = self.font_large.render("YOU DIED! ☠️", True, RED)
        self.screen.blit(death_text, (WINDOW_WIDTH // 2 - death_text.get_width() // 2, 200))
        
        score_text = self.font_medium.render(f"Final Length: {len(self.player.body)}", True, YELLOW)
        self.screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 320))
        
        killer_text = self.font_small.render(f"Killed by: {killer}", True, WHITE)
        self.screen.blit(killer_text, (WINDOW_WIDTH // 2 - killer_text.get_width() // 2, 400))
        
        retry_text = self.font_small.render("Press SPACE to Play Again", True, GREEN)
        self.screen.blit(retry_text, (WINDOW_WIDTH // 2 - retry_text.get_width() // 2, 480))
        
        menu_text = self.font_small.render("Press M for Menu", True, GRAY)
        self.screen.blit(menu_text, (WINDOW_WIDTH // 2 - menu_text.get_width() // 2, 530))
    
    def draw(self):
        if self.state == GameState.MENU:
            self.draw_menu()
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
