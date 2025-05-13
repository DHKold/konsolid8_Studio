# CPU - W65C02S

## Features

## List of PINS

| Pin(s)   | Name         | Direction | Description                         | Usage                     |
|----------|--------------|-----------|-------------------------------------|---------------------------|
| A0-A15   | Address      | Out       | Address bus                         | CPU Memory Bus            |
| D0-D7    | Data         | I/O       | Data bus                            | CPU Memory Bus            |
| R/W      | Read/Write   | Out       | Read/Write control signal           | CPU Memory Bus            |
| BE       | Bus Enable   | In        | Bus enable signal                   | CPU Memory Bus            |
| Ø2       | Clock        | In        | Phase 2 clock input                 | Clock                     |
| RESB     | Reset        | In        | Reset signal                        | Boot                      |
| IRQB     | Interrupt    | In        | Interrupt request                   | Handles interrupts        |
| NMIB     | Interrupt    | In        | Non-maskable interrupt request      | Handles interrupts        |
| VPB      | Vector Pull  | Out       | Vector pull signal                  |                           |
| MLB      | Memory Lock  | Out       | Memory lock signal                  |                           |
| SOB      | Set Overflow | In        | Set overflow flag                   |                           |
| SYNC     | Sync         | Out       | Indicates opcode fetch              |                           |
| PHI1O    | Phi 1 Out    | Out       | Phase 1 clock output                |                           |
| PHI2O    | Phi 2 Out    | Out       | Phase 2 clock output                |                           |
| RDY      | Ready        | In        | Ready signal to pause the processor |                           |
| NC       | Not Connected| -         | No internal connection              |                           |
| VSS      | Ground       | -         | Ground connection                   | Power supply              |
| VDD      | Power        | -         | Positive power supply               | Power supply              |

## Packaging

```
            +--------------+
    VPB  1 <| o           <|  40 RESB
    RDY  2  |>             |> 39 PHI2O
  PHI1O  3 <|             <|  38 SOB
   IRQB  4  |>            <|  37 PHI2
    MLB  5 <|             <|  36 BE
   NMIB  6  |>             |  35 NC
   SYNC  7 <|              |> 34 RWB
    VDD  8  |~            <|> 33 D0
    A0   9 <|             <|> 32 D1
    A1  10 <|             <|> 31 D2
    A2  11 <|             <|> 30 D3
    A3  12 <|             <|> 29 D4
    A4  13 <|             <|> 28 D5
    A5  14 <|             <|> 27 D6
    A6  15 <|             <|> 26 D7
    A7  16 <|              |> 25 A15
    A8  17 <|              |> 24 A14
    A9  18 <|              |> 23 A13
    A10 19 <|              |> 22 A12
    A11 20 <|             ~|  21 VSS
            +--------------+
```

## Quirks