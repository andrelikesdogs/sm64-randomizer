#/bin/bash

rom_file=$1
rom_pos=$2

echo $rom_file
echo $rom_pos

# update main.asm
sed \
  -e "s@#ROM_FILE@${rom_file}@g" \
  -e "s@#ROM_POS@${rom_pos}@g" \
  asm/main.tpl.asm > asm/main.asm

../armips/build/armips -root asm/ main.asm

./3rdparty/n64cksum_mac_x64 "${rom_file}"