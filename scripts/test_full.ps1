[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Write-Host "=== ТЕСТ 3: Запуск со всеми параметрами ==="
python src/main.py --vfs test_fs.tar --script tests/start.txt