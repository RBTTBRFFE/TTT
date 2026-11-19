@echo off
chcp 65001 >nul
title Proverka servera variant 23 (port 3623)
echo.
echo === Variant 23, PZ.07: proverka servera ===
echo.
echo 1) Glavnaya stranica (200):
curl.exe -s -o nul -w "    kod otveta: %%{http_code}\n" http://localhost:3623/
echo.
echo 2) Pravilnye dannye, JSON (200):
curl.exe -s -w "\n    kod otveta: %%{http_code}\n" -X POST http://localhost:3623/%%D0%%BE%%D0%%BF%%D1%%80%%D0%%BE%%D1%%81 -H "Content-Type: application/json" --data-binary @data\ok.json
echo.
echo 3) Pustye dannye (400):
curl.exe -s -o nul -w "    kod otveta: %%{http_code}\n" -X POST http://localhost:3623/%%D0%%BE%%D0%%BF%%D1%%80%%D0%%BE%%D1%%81 -H "Content-Type: application/json" --data-binary @data\empty.json
echo.
echo 4) Nevernyi adres (404):
curl.exe -s -o nul -w "    kod otveta: %%{http_code}\n" http://localhost:3623/%%D0%%BD%%D0%%B5%%D0%%B2%%D0%%B5%%D1%%80%%D0%%BD%%D1%%8B%%D0%%B9-%%D0%%B0%%D0%%B4%%D1%%80%%D0%%B5%%D1%%81
echo.
echo 5) Nevernyi metod, GET na /opros (405):
curl.exe -s -o nul -w "    kod otveta: %%{http_code}\n" http://localhost:3623/%%D0%%BE%%D0%%BF%%D1%%80%%D0%%BE%%D1%%81
echo.
echo 6) Telo ne v formate obmena, dannye formy (415):
curl.exe -s -o nul -w "    kod otveta: %%{http_code}\n" -X POST http://localhost:3623/%%D0%%BE%%D0%%BF%%D1%%80%%D0%%BE%%D1%%81 -d "tema=a&ocenka=5"
echo.
echo Ozidali: 200, 200, 400, 404, 405, 415
echo.
pause
