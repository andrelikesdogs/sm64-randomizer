rm -rf dist/
mkdir -p dist
set -e # exit on error
pyinstaller main-unix.spec

#mv "dist/main" "dist/SM64\ Randomizer\ Generator.app"

# pack as zip
VERSION="$(python -c 'from __version__ import __version__; print(__version__)')"
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
set +e

# save version in env variables for later build-step
echo "VERSION=${VERSION}" >> $GITHUB_ENV
