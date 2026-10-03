Write-Host "=== ТЕСТ: Запуск VFS с несколькими файлами ==="
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
python src/main.py --vfs tests/vfs_files.json --script tests/start.txt