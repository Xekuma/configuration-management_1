Write-Host "=== ТЕСТ: Запуск VFS с глубокой вложенностью ==="
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
python src/main.py --vfs tests/vfs_deep.json --script tests/start.txt