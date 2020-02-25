# Some notes to make this work for you:
# Install 7z (if you don't install it in the default folder or not on C:/, change the last line)
# Install Python 3.7.x (newest minor) both 32 and 64 bit. If you only require one and not the other, feel free to remove/comment out the other.
# Make sure Python is installed in the default folder in your Users Directory

$RandoVersion = python -c 'from __version__ import __version__; print(__version__)'
echo "Randomizer Version: $RandoVersion"

mkdir ./release -ErrorAction SilentlyContinue

# 32 bit
pip install -r .\requirements.txt
Remove-Item ./dist/ -Recurse -ErrorAction SilentlyContinue
Remove-Item ./release/*.exe
pyinstaller main-win.spec
mv "dist/main.exe" "dist/SM64 Randomizer Generator.exe"

mkdir ./dist/3rdparty -ErrorAction SilentlyContinue

Copy-Item 3rdparty/*.exe -Destination dist/3rdparty
Copy-Item 3rdparty/LICENSE -Destination dist/3rdparty
Copy-Item 3rdparty/README.md -Destination dist/3rdparty
Copy-Item ./Config -Destination ./dist -Recurse -Force
Copy-Item ./Data -Destination ./dist -Recurse -Force
Copy-Item ./Assets -Destination ./dist -Recurse -Force

$ArchiveName = "release/sm64-randomizer-$RandoVersion-win32.zip"
del $ArchiveName -ErrorAction SilentlyContinue
cd dist
& 'C:\Program Files\7-Zip\7z.exe' -tzip a ../$ArchiveName ./*.exe 3rdparty/* *.md LICENSE ./Data ./Config ./Assets
cd ..
