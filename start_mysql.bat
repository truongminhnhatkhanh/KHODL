@echo off
echo ========================================================
echo DANG KHOI DONG DICH VU MYSQL80...
echo ========================================================
net start MYSQL80
if %errorlevel% equ 0 (
    echo [OK] MySQL80 da duoc bat thanh cong!
) else (
    echo [LOI] Vui long chuot phai vao file nay va chon 'Run as administrator'!
)
pause
