$RandoVersion = python -c 'from __version__ import __version__; print(__version__)'
echo "Randomizer Version: $RandoVersion"

# 32 bit
pip install -r .\requirements.txt
Remove-Item ./dist/ -Recurse -ErrorAction SilentlyContinue
pyinstaller main-win.spec
mv "dist/main.exe" "dist/SM64 Randomizer Generator.exe"

mkdir ./dist/3rdparty -ErrorAction SilentlyContinue

Copy-Item 3rdparty/*.exe -Destination dist/3rdparty
Copy-Item 3rdparty/LICENSE -Destination dist/3rdparty
Copy-Item 3rdparty/README.md -Destination dist/3rdparty
Copy-Item ./Config -Destination ./dist -Recurse -Force
Copy-Item ./Data -Destination ./dist -Recurse -Force
Copy-Item ./Assets -Destination ./dist -Recurse -Force

# output version as env var for other build steps
#echo "VERSION=$RandoVersion" >> $GITHUB_ENV
Write-Host "::set-output name=version::${$RandoVersion}"