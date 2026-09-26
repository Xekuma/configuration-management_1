[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Write-Host "=== ТЕСТ 2: Запуск только с параметром --script ==="
Set-Content -Path "scripts/test_start.txt" -Value "conf-dump`nls -l`ncd ..`ncd`nexit" -Encoding UTF8
python src/main.py --script tests/start.txt