#!/usr/bin/env python3
"""
🐍 Slimy Snake - Main Launcher
Double-click this file to start the game!
"""

import subprocess
import sys
import os

def main():
    """Install dependencies and start the game"""
    print("🐍 Slimy Snake - Launching...")
    print("-" * 50)
    
    # Check if pygame is installed
    try:
        import pygame
        print("✓ Pygame is already installed!")
    except ImportError:
        print("📦 Installing pygame...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame==2.5.2"])
        print("✓ Pygame installed successfully!")
    
    print("-" * 50)
    print("🎮 Starting Slimy Snake...")
    print("-" * 50)
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    game_file = os.path.join(script_dir, "snake_game.py")
    
    # Run the game
    try:
        subprocess.run([sys.executable, game_file], check=True)
    except subprocess.CalledProcessError:
        print("\n❌ Error running the game!")
        input("Press Enter to close...")
    except FileNotFoundError:
        print(f"\n❌ Game file not found at: {game_file}")
        input("Press Enter to close...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("Press Enter to close...")

if __name__ == "__main__":
    main()
