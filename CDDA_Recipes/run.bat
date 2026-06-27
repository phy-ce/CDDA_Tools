@echo off
cd /d "%~dp0"
title CDDA Recipe Helper
where py >nul 2>nul
if %errorlevel%==0 goto usepy
python cdda_recipes.py
goto done
:usepy
py cdda_recipes.py
:done
if errorlevel 1 pause
