@echo off
echo Building Strange Tic-Tac-Toe.exe...
pyinstaller --onefile --windowed --name "Strange-TicTacToe" --icon=icon.ico game.py
echo.
echo ✅ Build complete!
echo exe file is in: dist\Strange-TicTacToe.exe
pause
