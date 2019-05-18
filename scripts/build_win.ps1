# Some notes to make this work for you:
# Install 7z (if you don't install it in the default folder or not on C:/, change the last line)
# Install Python 3.7.x (newest minor) both 32 and 64 bit. If you only require one and not the other, feel free to remove/comment out the other.
# Make sure Python is installed in the default folder in your Users Directory

# setup (read version file, create folders)
$env:Path = ";$home\AppData\Local\Programs\Python\Python37-32"
$env:Path += ";$home\AppData\Local\Programs\Python\Python37-32\Scripts"

$RandoVersion = python -c 'from __version__ import __version__; print(__version__)'

mkdir ./release -ErrorAction SilentlyContinue

$env:Path = ";$home\AppData\Local\Programs\Python\Python37-32"
$env:Path += ";$home\AppData\Local\Programs\Python\Python37-32\Scripts"
# 32 bit
pip install -r .\requirements.txt
Remove-Item ./dist/ -Recurse
Remove-Item ./release/*.exe
pyinstaller --noconfirm --onefile --add-data="README.md;." --add-data="LICENSE;." --add-data="favicon.ico;." --add-data="Data;." -i "favicon.ico" main.py
mv "dist/main.exe" "dist/SM64 Randomizer CLI.exe"
pyinstaller --noconfirm --noconsole --onefile --add-data="README.md;." --add-data="LICENSE;." --add-data="favicon.ico;." --add-data="Data;." --add-data="3rdparty/LICENSE;3rdparty/." --add-data="3rdparty/README.md;3rdparty/." -i "favicon.ico" main.py
mv "dist/main.exe" "dist/SM64 Randomizer GUI.exe"

mkdir ./dist/3rdparty -ErrorAction SilentlyContinue

cp 3rdparty/*win* ./dist/3rdparty
cp 3rdparty/LICENSE ./dist/3rdparty
cp 3rdparty/README.md ./dist/3rdparty
cp Data ./dist

$ArchiveName = "release/sm64-randomizer-$RandoVersion-win32.zip"
del $ArchiveName -ErrorAction SilentlyContinue
cd dist
& 'C:\Program Files\7-Zip\7z.exe' -tzip a ../$ArchiveName ./*.exe 3rdparty/* *.md LICENSE
cd ..

# 64 bit
$env:Path = ";$home\AppData\Local\Programs\Python\Python37"
$env:Path += ";$home\AppData\Local\Programs\Python\Python37\Scripts"

pip install -r .\requirements.txt
Remove-Item ./dist/ -Recurse
Remove-Item ./release/*.exe
pyinstaller --noconfirm --onefile --add-data="README.md;." --add-data="LICENSE;." --add-data="favicon.ico;." --add-data="Data;." -i "favicon.ico" main.py
mv "dist/main.exe" "dist/SM64 Randomizer CLI.exe"
pyinstaller --noconfirm --noconsole --onefile --add-data="README.md;." --add-data="LICENSE;." --add-data="favicon.ico;." --add-data="Data;." --add-data="3rdparty/LICENSE;3rdparty/." --add-data="3rdparty/README.md;3rdparty/." -i "favicon.ico" main.py
mv "dist/main.exe" "dist/SM64 Randomizer GUI.exe"

mkdir ./dist/3rdparty -ErrorAction SilentlyContinue

cp 3rdparty/*win* ./dist/3rdparty
cp 3rdparty/LICENSE ./dist/3rdparty
cp 3rdparty/README.md ./dist/3rdparty
cp Data ./dist

$ArchiveName = "release/sm64-randomizer-$RandoVersion-win64.zip"
del $ArchiveName -ErrorAction SilentlyContinue
cd dist
& 'C:\Program Files\7-Zip\7z.exe' -tzip a ../$ArchiveName ./*.exe 3rdparty/* *.md LICENSE
cd ..