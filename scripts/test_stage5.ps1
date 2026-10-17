Write-Host "=== ТЕСТ: Этап 5 (mkdir, rmdir и модификация VFS в памяти) ==="
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

python src/main.py --vfs tests/vfs_deep.json --script tests/test_stage5.txt