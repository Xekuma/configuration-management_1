[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Write-Host "=== ТЕСТ 2: Запуск только с параметром --script ==="
python src/main.py --script tests/start.txt