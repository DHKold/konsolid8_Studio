# MMU - HUMMUxxx

16bits addressing:

General: RRRBBAAA AAAAAAAA : R=Region(3b = 8) x B=Bank(2b = 4) x A=Address(11b = 2KB)           = 65KB
MMIO   : FFFFFFFF TTTTAAAA : T=Target (4b = 16)  x A=Address(4b = 16)                           = 256B

Regions:
```
- R=000 : CRAM1 (CPU-RAM-1) 8KB
    - B=00 : WRAM (RW CPU Working RAM)
    - B=01 : TCRAM0 (CPU Trusted Code RAM)
    - B=10 : TCRAM1 (CPU Trusted Code RAM)
    - B=11 : TCRAM2 (CPU Trusted Code RAM)
- R=001 : CRAM2 (CPU-RAM-2) 8KB
    - B=00 : TCRAM3 (CPU Trusted Code RAM)
    - B=01 : TCRAM4 (CPU Trusted Code RAM)
    - B=10 : TCRAM5 (CPU Trusted Code RAM)
    - B=11 : TCRAM6 (CPU Trusted Code RAM)
- R=010 : GRAM (GPU-RAM) 8KB
    - B=00 : GRAM0 (GPU RAM)
    - B=01 : GRAM1 (GPU RAM)
    - B=10 : GRAM2 (GPU RAM)
    - B=11 : GRAM3 (GPU RAM)
- R=011 : GROM (GPU-ROM: BIOS graphics) 8KB
    - B=00 : GROM0 (BIOS GROM)
    - B=01 : GROM1 (BIOS GROM)
    - B=10 : GROM2 (BIOS GROM)
    - B=11 : GROM3 (BIOS GROM)
- R=100 : CROM (CPU-ROM) 8KB
    - B=00 : CROM0 (BIOS CROM)
    - B=01 : CROM1 (BIOS CROM)
    - B=10 : CROM2 (BIOS CROM)
    - B=11 : CROM3 (BIOS CROM)
- R=101 : ESU (Expansion Slot Unit)
    - B=00 : EXP0 (Expansion RAM/ROM)
    - B=01 : EXP1 (Expansion RAM/ROM)
    - B=10 : EXP2 (Expansion RAM/ROM)
    - B=11 : EXP3 (Expansion RAM/ROM)
- R=110 : CSU (Cartridge Slot Unit)
    - B=00 : CART0 (Cartridge RAM/ROM)
    - B=01 : CART1 (Cartridge RAM/ROM)
    - B=10 : CART2 (Cartridge RAM/ROM)
    - B=11 : CART3 (Cartridge RAM/ROM)
- R=111 : MMIO
    - B=00 : Unused
    - B=01 : Unused
    - B=10 : Unused
    - B=11 : General MMIO
        -T=0000 : MMU (Memmory Management Unit)
            -A=0000 : TBD
            -A=0001 : TBD
            -A=0010 : TBD
            -A=0011 : TBD
            -A=0100 : TBD
            -A=0101 : TBD
            -A=0110 : TBD
            -A=0111 : TBD
            -A=1000 : TBD
            -A=1001 : TBD
            -A=1010 : TBD
            -A=1011 : TBD
            -A=1100 : TBD
            -A=1101 : TBD
            -A=1110 : TBD
            -A=1111 : TBD
        -T=0001 : TCU (Transfer Control Unit)
            -A=0000 : SourceId
            -A=0001 : TargetId
            -A=0010 : SourceStartAddress (8b lo)
            -A=0011 : SourceStartAddress (8b hi)
            -A=0100 : TargeStarttAddress (8b lo)
            -A=0101 : TargeStarttAddress (8b hi)
            -A=0110 : Size (8b lo)
            -A=0111 : Size (8b hi)
            -A=1000 : Flags
            -A=1001 : Flags
            -A=1010 : TBD
            -A=1011 : TBD
            -A=1100 : TBD
            -A=1101 : TBD
            -A=1110 : TBD
            -A=1111 : TBD
        -T=0010 : ESU (Expansion Slot Unit) -> Customizable per Expansion
        -T=0011 : CSU (Cartridge Slot Unit) -> Customizable per Game
        -T=0100 : Unused
        -T=0101 : Unused
        -T=0110 : Unused
        -T=0111 : Unused
        -T=1000 : APU (Audio Processing Unit) - See APU documentation
        -T=1001 : GPU (Graphical Processing Unit) - See GPU documentation
        -T=1010 : SSU (Save Slot Unit)
            -A=00XX : Card Size (4bytes, 0-4GB)
            -A=01XX : Address (4bytes, 0-4GB)
            -A=1000 : Command (Read, Write, ...)
            -A=1001 : Data (Read/Write)
            -A=1010 : Unused
            -A=1011 : Unused
            -A=1100 : Unused
            -A=1101 : Unused
            -A=1110 : Unused
            -A=1111 : Unused
        -T=1011 : PSU (Peripherals Slots Unit)
            -A=0000 : TBD (probably status)
            -A=0001 : TBD (probably flags)
            -A=0010 : Unused
            -A=0011 : Unused
            -A=0100 : Unused
            -A=0101 : Unused
            -A=0110 : Unused
            -A=0111 : Unused
            -A=1000 : TBD Slot0.State
            -A=1001 : TBD Slot1.State
            -A=1010 : TBD Slot2.State
            -A=1011 : TBD Slot3.State
            -A=1100 : TBD Slot4.State
            -A=1101 : TBD Write.Slot
            -A=1110 : TBD Write.Command
            -A=1111 : TBD Write.xxx
        -T=1100 : Unused
        -T=1101 : Unused
        -T=1110 : Unused
        -T=1111 : ICU (Interrupt Controller Unit)
            -A=0000 : Interrupt Mask
            -A=0001 : Interrupt Flags
            -A=0010 : Next Interrupt SourceId
            -A=0011 : Interrupt Counter
            -A=0100 : Unused
            -A=0101 : Unused
            -A=0110 : Unused
            -A=0111 : Unused
            -A=1010 : NMI_VEC (lo) (Non Maskable Interrupt)
            -A=1011 : NMI_VEC (hi) (Non Maskable Interrupt)
            -A=1100 : RST_VEC (lo) (Reset Interrupt)
            -A=1101 : RST_VEC (hi) (Reset Interrupt)
            -A=1110 : IRQ_VEC (lo) (Maskable Interrupt)
            -A=1111 : IRQ_VEC (hi) (Maskable Interrupt)
```

## Features

### MMIO Controller

Since both CPU, EXT and DMA can use MMIO, there needs to be a controller to orchestrate, and also check authorization (EXT has restricted access).

The MMIO BUS has 17 lines:
- T0-T3: 4b identifying the TargetId
- A0-A3: 4b identifying the TargetRegisterId
- OP   : 1b setting the direction (RW)
- D0-D7: 8b data input/output



Recevies MasterSelect (1b), Operation (1b=RW), TargetId (4b) and outputs the Safe Flag.

MMIO Controller pins:
- MS        : MasterSelect (CPU=0, EXT=1)
- OPA       : Master0 Operation (READ=0, WRITE=1)
- TA0-TA3   : Master0 TargetId
- OPB       : Master1 Operation (READ=0, WRITE=1)
- TB0-TB3   : Master1 TargetId
- > SF : Safe Floag (SAFE=0, UNSAFE=1)

### Memory Controller

| Unit    | WRAM | TCRAM | GRAM | EXT | CROM | GROM | CART | MMIO |
|---------| ---- | ----- | ---- | --- | ---- | ---- | ---- | ---- |
| **CPU** | R/W  | R/X   | R/W  | R/W | R/X  | -    | -    | R/W  |
| **GPU** | -    | -     | R    | -   | -    | R    | -    | -    |
| **EXT** | -    | -     | -    | -   | -    | -    | -    | R/W  |
| **DMA** | W    | W     | W    | R/W | -    | -    | R    | R/W  |

- Routing: Responsible for outputing the CS signal to the authorized Chip
- Security: Acknoledge if the access is authorized (Based on RW+SYNC+REGION)

Pins (10 pins):
- R0-R4: needs the higher address bit to check for region rights (granularity is 2KB regions)
- OP0-OP1: needs to know the operation (R/W/X)
- M0-M1: needs to know the source (CPU, EXT, DMA)
- > SF: output Safe Flag

Needed 3 times: CPU, EXT, DMA

### Serial Transfer Controller (~DMA)

- Handles transfer between regions
- Security: Acknoledge if the transfered data is trusted (Based on #SRC + #DST + KEY)