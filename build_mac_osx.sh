rm -rf dist/main
bin/pyinstaller --onefile --windowed --noconsole --osx-bundle-identifier "com.andremeyer.sm64-randomizer" --add-data="README.md:." --add-data="LICENSE:." main.py