<#
    Проверка сервера варианта 23 (УП.05, ПЗ.07)
    Запуск:  powershell -ExecutionPolicy Bypass -File .\check-server.ps1
             (папку с node server.js открыть в другом окне PowerShell)
    Эмуляция: .\check-server.ps1 -base http://localhost:3624
#>

param(
    [string]$base = 'http://localhost:3623'
)

# Кириллические адреса передаём в процентном виде — так их понимает любой клиент
$route    = '/%D0%BE%D0%BF%D1%80%D0%BE%D1%81'                                              # /опрос
$notFound = '/%D0%BD%D0%B5%D0%B2%D0%B5%D1%80%D0%BD%D1%8B%D0%B9-%D0%B0%D0%B4%D1%80%D0%B5%D1%81' # /неверный-адрес

function Invoke-Check {
    param(
        [string]$Number,
        [string]$Title,
        [string]$Method,
        [string]$Path,
        [string]$BodyFile,
        [int]$Expected
    )

    $params = @{
        Uri         = "$base$Path"
        Method      = $Method
        TimeoutSec  = 10
        ErrorAction = 'Stop'
    }
    if ($BodyFile) {
        # отправляем байты UTF-8 — иначе PowerShell 5.1 может испортить кириллицу в JSON
        $params.Body        = [System.IO.File]::ReadAllBytes($BodyFile)
        $params.ContentType = 'application/json; charset=utf-8'
    }

    try {
        $r    = Invoke-WebRequest @params -UseBasicParsing
        $code = [int]$r.StatusCode
        $text = $r.Content
    }
    catch {
        $resp = $_.Exception.Response
        if ($null -ne $resp) {
            $code = [int]$resp.StatusCode
            $stream = $resp.GetResponseStream()
            $text   = (New-Object System.IO.StreamReader($stream, [System.Text.Encoding]::UTF8)).ReadToEnd()
        }
        else {
            $code = 0
            $text = $_.Exception.Message
        }
    }

    if ($code -eq $Expected) {
        Write-Host ("[ OK ] {0}. {1} -> код {2}" -f $Number, $Title, $code) -ForegroundColor Green
    }
    else {
        Write-Host ("[ОШИБКА] {0}. {1} -> ожидали {2}, получили {3}" -f $Number, $Title, $Expected, $code) -ForegroundColor Red
    }
    if ($text) {
        $short = ($text -replace '\s+', ' ')
        if ($short.Length -gt 150) { $short = $short.Substring(0, 150) + '...' }
        Write-Host ("         ответ: {0}" -f $short) -ForegroundColor DarkGray
    }
}

Write-Host ''
Write-Host 'Проверка сервера варианта 23 (порт 3623)' -ForegroundColor Cyan
Write-Host ('=' * 60)

# 0. Сервер вообще запущен?
try {
    Invoke-WebRequest -Uri "$base/" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop | Out-Null
}
catch {
    Write-Host 'Сервер не отвечает. Откройте второе окно PowerShell и выполните:' -ForegroundColor Yellow
    Write-Host '    cd УП.05_ПЗ.07_вариант-23' -ForegroundColor Yellow
    Write-Host '    node server.js' -ForegroundColor Yellow
    exit 1
}

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Invoke-Check '1' 'Главная страница      ' 'GET'  '/'        $null                      200
Invoke-Check '2' 'Правильные данные     ' 'POST' $route     "$here\data\ok.json"       200
Invoke-Check '3' 'Пустые данные         ' 'POST' $route     "$here\data\empty.json"    400
Invoke-Check '4' 'Неверный адрес        ' 'GET'  $notFound  $null                      404
Invoke-Check '5' 'Неверный метод        ' 'GET'  $route     $null                      405
Invoke-Check '6' 'Оценка вне 1-5 (доп.) ' 'POST' $route     "$here\data\bad-score.json" 400

Write-Host ('=' * 60)
Write-Host 'Если все строки зелёные — сервер работает правильно.'
Write-Host 'Эмуляция проверяется так же, но с -base http://localhost:3624 (см. Readme.txt).'
