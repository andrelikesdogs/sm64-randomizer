rm -rf dist/main
bin/pyinstaller --noconfirm --onefile --windowed --noconsole --osx-bundle-identifier "com.andremeyer.sm64-randomizer" --add-data="README.md:." --add-data="LICENSE:." --i "favicon.icns" main.py

# prepare release folder
rm -rf ./release
mkdir ./release

mv dist/main.app release/SM64\ Randomizer.app
mv dist/main release/SM64\ Randomizer\ CLI

# pack as zip
VERSION="$(python -c 'from __version__ import __version__; print(__version__)')"
rm dist/sm64-randomizer-${VERSION}-mac-osx.zip
cp ./README.md ./release
cp ./LICENSE ./release
mkdir ./release/3rdparty
cp -v ./3rdparty/*mac* ./release/3rdparty
cp -v ./3rdparty/LICENSE* ./release/3rdparty
cp -v ./3rdparty/README* ./release/3rdparty
cd ./release
zip -r ../dist/sm64-randomizer-${VERSION}-mac-osx.zip SM64* README.md LICENSE
cd -;
rm -rf ./release