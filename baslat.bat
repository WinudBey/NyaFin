@echo off
title NyaFin - Otomatik Baslatici
cd /d "%~dp0"

echo NyaFin baslatiliyor...
echo.

if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" web.py
) else (
    echo HATA: 'venv' klasoru bulunamadi!
    echo Lutfen once sanal ortami kurun ve bagimliliklari yukleyin.
)

pause
