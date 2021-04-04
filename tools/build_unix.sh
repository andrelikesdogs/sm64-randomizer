rm -rf dist/main
set -e # exit on error
pyinstaller main-osx.spec

mv dist/main dist/SM64\ Randomizer\ Generator

# prepare release folder
mkdir -p ./release

# pack as zip
VERSION="$(python -c 'from __version__ import __version__; print(__version__)')"
rm -f ../release/sm64-randomizer-${VERSION}-unix.zip
cp ./README.md ./dist
cp ./LICENSE ./dist
mkdir -p ./dist/3rdparty
mkdir -p ./dist/Data
cp -v ./3rdparty/*mac* ./dist/3rdparty
cp -vr ./Data ./dist
cp -vr ./Config ./dist
cp -vr ./Assets ./dist
cp -v ./3rdparty/LICENSE* ./dist/3rdparty
cp -v ./3rdparty/README* ./dist/3rdparty
cd ./dist
zip -r ../release/sm64-randomizer-${VERSION}-unix.zip SM64* README.md LICENSE 3rdparty Data Config Assets
cd -;
set +e

# save filename in env variables for later build-step
echo "RELEASE_FILENAME=sm64-randomizer-${VERSION}-unix.zip" >> $GITHUB_ENV
