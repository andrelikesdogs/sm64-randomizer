# Star Location Notes
*X, Y, Z where Z is Up/Down*
*Taken from US, Big Endian ROM using P64 Debugger*
*If not noted otherwise, hex values are 32-bit floating point numbers*

# PSS: Beat Slide in <21s
-6358.0, -4300.0, 4700.0


X: C5C6B000 (-6358) in RAM 80336414 0xF1414

Y: C5866000 (-4300) in RAM 80336417 0xF1418

Z: 4592E000 (4700) in RAM 802507CC
```
802507CC: LUI 4592
802507D0: ORI E000
```


```
DMALog 0x00001000 maps 80246000 to 80346000
```

# BOB: Koopa the Quick
3030, 4500, -4600 (STORED AS SHORT)

X 0BD6 in 0xED868 (Short)

Y 1194 in 0xED86A (Short)

Z EE08 in 0xED86C (Short)

# THI: Koopa the Quick
7100, -1300, -6000 (STORED AS SHORT)

X: 1BBC in RAM 80332878 in 0xED86C (Short)

Y: FAEC in RAM 8033287A in 0xED8BB (Short)

Z: E890 in RAM 8033286C in 0xED8CE (Short)

# THI: Wiggler
0, 2048, 0

Z: 00000000 in RAM
```
802F2BFE8 ADDIU A2, R0, 0x0000
```
X: 00000000 in RAM
```
80301FE0 MTC1 R0, F12
```
Y: 45000000 in RAM
```
80301FD8 LUI AT, 0x4500
80301FDC MTC1 AT, F14
```

# THI Piranha Plants
-6300, -1850, -6300

X: C5C4E000 in RAM 80348C54 in 0xF3C54

Z: C5C4E000 in RAM
```
8030D028 LUI A2, 0xC5C4
8030D02C ORI A2, A2, 0xE000
```
Y: C4E74000 in RAM 80348C58 in 0xF3C58


# BOB: King Bob-Omb
2000, 4500 -4500

X: 44FA0000 in RAM 
```
802A7AD4: LUI AT, 0x44FA // Rest remains 0000 :(
```
Y: 458CA000 in RAM 80337900 in 0xF2900 (Float)

Z: in RAM 802A7AE0
```
802A7AE0: LUI A2, 0xC58C
802A7AE4: ORI AR, 0xA000
```

# WF: Whomp Boss
180, 3880, 340

Y: 45728000 in RAM 80337DD0 in 0xF2DD0 (Float)

Z: 43AA0000 in RAM 802C7914
```
802C914: LUI A2, 0x43AA
```
Z: 43340000 in RAM 802C7900
```
802C7900: LUI AT, 0x4334
802C790C: MTC1, AT, F12
```

# SSL: Eyerok
0, -900, -3700

Y: C4610000 in RAM 8030EA1C
```
8030EA1C: LUI AT, 0xC461
```
Z: C56740000 in RAM:
```
8030EA28: LUI A2, 0xC567
...
8030EA30: ORI A2, A2, 0x4000
```
X: 00000000 in RAM 8030EA24
```
MTC1 R0, F12
```

# LLL: Boil the Big Bully
0, 950, -6800

Z: C5D48000 in RAM:
```
802EB96C: A2, 0xC5D4
802EB970: A2, A2, 0x8000
```
Y: 446D8000 in RAM 80348594 in F3594 (?)

X: 00000000 in RAM 802EB964
```
802EB964: MTC1 R0, F12
```

# LLL: Bully and Minions
3700, 600, -5500

X: 45674000 in RAM 80344416 in F3498

Y: 44160000 in RAM 802EBCB4
```
802EBCB4: LUI AT, 0x4416
802EBCB8: MTC1 AT, F14
```
Z: C5ABE000 in RAM
```
802EBCBC: LUI A2, 0xC5AB
...
802EBCC4: ORI A2, A2, 0xE0000
```

# CCM: Leave Slide (Slip Sliding Away)
2500, -4350, 5750

X: 411C4000 in RAM 80337A84 in 0xF2A80

Z: 45B3B000 in RAM
```
802B23AC LUI A2, 0x45B3
802B22B0 ORI A2, A2, 0xB000
```
Y: C587F000 in RAM 80337A84 in 0xF2A84

# CCM: Lil Penguin Lost
3500 (3167?), -4300, 4650 (5108?)

*Note: the spawn position between JP and US is different, numbers in parentheses are for US*

Z: 459FA000 in RAM
```
802BF120: LUI A2, 0x459F
802BF124: ORI A2, A2, 0xA000
```
Y: C5866000 in RAM 80337CC0 in 0xF2CC0

X: 4545F000 in RAM 80337CBC in 0x2FCBC

# CCM: Penguin Race
-7339, -5700, -6774 (-6934)

Y: C5B22000 in 80348D30 in 0xF3D30

X: C5E55800 in 80348D3C in 0xF3D2C

Z: C5D3B000 in RAM:
```
80312038: LUI A2, 0xC5D3
8031203C: ORI A2, A2, 0xB000
```

# CCM: Snowman Assembly
-4700, -1024, 1890

Y: C4800000 in RAM 802F14C0:
```
802F14C0: LUI AT, 0xC480
802F14C4: MTC1 AT, F14
```
X: C592E000 in RAM 80348738 in F3738

Z: 44EC4000 in RAM:
```
802F14C8: LUI A2, 0x44EC
...
802F14D0: ORI A2, A2, 0x4000
```

# JRB: 4 Treasure Chests
-1800, -2500, -1700

Z: 0xC4D48000 in RAM:
```
802F82AC LUI A2, 0xC4D4
802F82B0 ORI A2, A2, 0x800
```
X: 0xC4E1000 in RAM:
```
802F82A0: LUI AT, 0xC4E1
802F82A4: MTC1 AT, F12
```
Y: C51C4000 in RAM 8034892C in 0xF392C

# BBH: Go on a Ghost Hunt (4 Boos + Lobby Big Boo)
980, 1100, 250

X: 44750000 in RAM 
```
802C4BA4: LUI AT, 0x4475
802C4BA8: MTC1 AT, F12
```
Y: 44898000 in RAM 80337D84 in 0xF2D84

Z: 437A000 in RAM
```
802C4BB8: LUI A2, 0x437A
```

# BBH: Merry-Go-Round
-1600, -2100, 205

Y: C5034000 in 80337D88 in 0xF2D88

X: C4C80000 in RAM:
```
802C4C18: LUI AT, 0xC4C8
802C4C1C: MTC1 AT, F12
```
Z: 434D0000 in RAM:
```
802C4C2C: LUI A2, 0x434D
```

# BBH: Eye to Eye
1370, 2000, -320

X: 44AB4000 in RAM 803378E0 in 0xF2BE0

Y: 44FA0000 in RAM
```
802A644C LUI AT, 0x44FA
802A6450 MTC1 AT, F14
```
Z: C3A00000 in RAM:
```
802A6458 LUI A2, 0xC3A0
```

# BBH: Rooftop Big Boo
700, 3200, 1900

Z: 44ED8000 in RAM:
```
802C4BEC LUI A2, 0x44ED
...
802C4BF4 ORI A2, A2, 0x8000
```
X: 442F0000 in RAM:
```
802C4BDC LUI AT, 0x442F
802C4BE0 MTC1 AT, F12
```
Y: 45480000 in RAM:
```
802C4BE4 LUI AT 0x4548
802C4BE8 MTC1 AT, F14
```

# SSL: In the Talons of the Big Bird
-5550, 300, -930

X: C5AD7000 in RAM 80344396 in 0xF3D14

Y: 43960000 in RAM:
```
80311474 LUI AT, 0x4396
80311478 MTC1 AT, F14
```
Z: C4688000 in RAM:
```
8021147C LUI A2, 0xC468
...
80311484 ORI A2, A2, 0x8000
```

# DDD: 4 Treasure Chests
-1900, -4000, -1400

X: C4ED8000 in RAM 80348930 in 0xF3930

Y: C57A0000 in RAM:
```
802F8444 LUI AT, 0xC57A
802F8448 MTC1 AT, F14
```
Z: C4AF0000 in RAM:
```
802F8450 LUI A2, 0xC4AF
```

# DDD: Water Rings
3400, -3200, -500

X: 45548000 in RAM 803485E0 in 0xF2CB8 OR 0xF35E0 (?)

Y: C5480000 in RAM
```
802EC96C LUI AT, 0xC548
802EC970 MTC1 AT, F14
```
Z: C4FA0000 in RAM
```
802EC978 LUI A2, 0xC4FA
```

# DDD: Manta Rays Reward
-3180, -3600, 120

X: C546C000 in RAM 80348920 in F3920

Y: C5610000 in RAM
```
802F72D0 LUI AT, 0xC561
802F72D4 MTC1 AT, F14
```
Z: 42F00000 in RAM
```
802F72DC LUI A2, 0x42F0
```

# TTM: Mystery Monkey Cage
2500, -1200, 1300

X: C4960000 in RAM
```
802AEA20 LUI AT, 0xC496
802AEA24 MTC1 AT, F14
```
Y: 451C4000 in RAM 8033C496 in 0xF28FC

Z: 44A28000 in RAM
```
802AEA28 LUI A2, 0x44A2
...
802AEA30 ORI A2, A2, 0x8000
```

# SL: Chill with the Bully

Z: C5877800 in RAM
```
802EB950 LUI A2, 0xC587
...
802EB958 ORI A2, A2, 0x7800
```
X: 43020000 in ROM
```
802EB940 LUI AT, 0x4302
802EB944 MTC1 AT, F12
```
Y: 44C80000 in ROM
```
802EB948 LUI AT, 0x44C8
802EB94C MTC1 AT, F14
```