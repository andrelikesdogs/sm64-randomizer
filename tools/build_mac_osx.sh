rm -rf dist/main
bin/pyinstaller main.spec

mv dist/main.app dist/SM64\ Randomizer.app
mv dist/main dist/SM64\ Randomizer\ CLI

# prepare release folder
mkdir -p ./release

# pack as zip
VERSION="$(python -c 'from __version__ import __version__; print(__version__)')"
rm release/sm64-randomizer-${VERSION}-mac-osx.zip
cp ./README.md ./dist
cp ./LICENSE ./dist
mkdir -p ./dist/3rdparty
mkdir -p ./dist/Data
cp -v ./3rdparty/*mac* ./dist/3rdparty
cp -vr ./Data ./dist
cp -v ./3rdparty/LICENSE* ./dist/3rdparty
cp -v ./3rdparty/README* ./dist/3rdparty
cd ./dist
zip -r ../release/sm64-randomizer-${VERSION}-mac-osx.zip SM64* README.md LICENSE 3rdparty Data
cd -;