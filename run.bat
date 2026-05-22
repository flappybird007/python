@echo off
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting Slimy Snake...
python snake_game.py
pause
