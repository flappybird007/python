# 🐍 Slimy Snake - Like Slither.io!

A fun and entertaining Snake game with AI bots, built in Python using Pygame. Compete against intelligent AI opponents, eat food to grow, and become the longest snake!

## 🎮 Features

- **Multiplayer AI Gameplay** - Compete against 3 intelligent AI bots with adaptive behavior
- **Smart AI Bots** - They hunt food, avoid threats, and react to your movements
- **Progressive Growth** - Eat yellow food dots to grow your snake
- **Death Mechanics** - When a snake dies, it drops food for others to collect
- **Head-to-Head Collisions** - Both snakes die if they collide head-first
- **Complete Menu System** - Start screen, pause menu, and death screen
- **Live Scoreboard** - Track your length and all bot lengths in real-time
- **Smooth Gameplay** - 60 FPS smooth snake movement
- **Wrap-Around Map** - Screen wrapping for continuous play

## 🕹️ Controls

| Key | Action |
|-----|--------|
| **↑ ↓ ← →** | Move your snake |
| **W A S D** | Alternative movement |
| **ESC** | Pause/Resume game |
| **SPACE** | Start game / Play again |
| **M** | Return to menu |
| **Q** | Quit game |

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/flappybird007/python.git
   cd python
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the game:**
   ```bash
   python snake_game.py
   ```

## 🎯 How to Play

1. **Start the game** - Press SPACE on the menu screen
2. **Move your snake** - Use arrow keys or WASD to navigate
3. **Eat food** - Collect yellow dots to grow longer and gain points
4. **Avoid enemies** - Don't hit other snakes' bodies or yourself
5. **Survive** - Last as long as possible and try to become the longest snake!

### Scoring
- Each food eaten = 1 length increase
- Dead snakes drop food at their death location
- Your final score is your snake's length when you die

## 🤖 AI Opponents

The game includes 3 intelligent AI bots:
- **Bot-Red** (Blue) - Aggressive food hunter
- **Bot-Orange** (Orange) - Balanced strategy
- **Bot-Cyan** (Cyan) - Defensive player

They each use decision-making algorithms to:
- Hunt the nearest food
- Avoid other snakes
- Avoid their own body segments
- Make tactical decisions based on threats

## 🎨 Game Screens

### Menu Screen
- Game title and instructions
- Press SPACE to start
- Press Q to quit

### Gameplay
- Your green snake in the center
- 3 colorful AI snakes
- Yellow food dots scattered around
- Live length counter for all snakes
- FPS counter

### Pause Screen
- Game continues in background
- Press ESC to resume
- Press M to return to menu

### Death Screen
- Your final length
- Which AI bot killed you
- Press SPACE to play again
- Press M to return to menu

## 📦 Project Structure

```
python/
├── snake_game.py       # Main game file
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🛠️ Technical Details

### Built With
- **Pygame** - Game engine and rendering
- **Python 3** - Game logic and AI

### Key Classes
- `Point` - Represents coordinates in the game world
- `Snake` - Represents a snake (player or AI)
- `SnakeGame` - Main game controller and renderer
- `GameState` - Enum for game states (menu, playing, paused, death)

### Game Loop
- Input handling
- Game state updates
- Collision detection
- AI decision-making
- Rendering at 60 FPS

## 🐛 Troubleshooting

### "pygame not found" error
```bash
pip install pygame
```

### Game runs slowly
- Close other applications to free up system resources
- Check your Python version (3.7+ recommended)
- Ensure pygame is properly installed

### Can't move the snake
- Make sure the game window is in focus
- Try using WASD instead of arrow keys
- Check if the game is paused (ESC)

## 📝 Tips & Tricks

1. **Stay in the center** - More maneuvering room
2. **Plan ahead** - Don't rush into corners
3. **Use wrapping** - Go off-screen to escape threats
4. **Block bots** - Position yourself to cut off AI paths
5. **Grow strategically** - A longer snake is harder to hit

## 🎮 Game Settings

You can customize the game by editing `snake_game.py`:

```python
WINDOW_WIDTH = 1200      # Game window width
WINDOW_HEIGHT = 800      # Game window height
FPS = 60                 # Frames per second
```

## 📄 License

Feel free to use and modify this game for personal or educational purposes!

## 👨‍💻 Author

Created with 🐍 and ❤️ for fun Python gaming!

## 🎉 Have Fun!

Enjoy playing Slimy Snake and competing against the AI bots. Good luck becoming the longest snake! 🏆

---

**Questions or suggestions?** Feel free to open an issue or create a pull request!
