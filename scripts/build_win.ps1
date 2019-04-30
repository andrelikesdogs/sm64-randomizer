Remove-Item ./dist/ -Recurse
pyinstaller --noconfirm --onefile --add-data="README.md;." --add-data="LICENSE;." --add-data="favicon.ico;." -i "favicon.ico" main.py
ren "dist/main.exe" "SM64 Randomizer CLI.exe"
pyinstaller --noconfirm --noconsole --onefile --add-data="README.md;." --add-data="LICENSE;." --add-data="favicon.ico;." -i "favicon.ico" main.py
ren "dist/main.exe" "SM64 Randomizer GUI.exe"
$Version = python -c 'from __version__ import __version__; print(__version__)'
"C:\Program Files\7-Zip\7z.exe"