[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Write-Host "=== ТЕСТ 1: Запуск только с параметром --vfs ==="
python src/main.py --vfs my_archive.zip