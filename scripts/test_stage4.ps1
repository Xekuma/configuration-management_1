Write-Host "=== ТЕСТ: Этап 4 (ls, cd, find, cal, head и обработка ошибок) ==="
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

python src/main.py --vfs tests/vfs_deep.json --script tests/test_stage4.txt