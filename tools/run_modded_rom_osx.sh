#/bin/bash
# Launches Mac-Specific Mupen64 Version
../mupen64plus.app/Contents/MacOS/mupen64plus --corelib ../mupen64plus.app/Contents/MacOS/libmupen64plus.dylib --plugindir ../mupen64plus.app/Contents/MacOS --gfx mupen64plus-video-glide64mk2 "$@"