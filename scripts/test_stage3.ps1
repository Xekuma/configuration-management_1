Write-Host "=== ТЕСТ: Полная проверка всех команд Этапа 3 ==="
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
python src/main.py --vfs tests/vfs_files.json --script tests/all_commands.txt