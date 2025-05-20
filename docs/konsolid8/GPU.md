### Pinout (ASIC)

DIP-32

- Using ASIC, embedded DACs means RGB555 -> Analog RGB -12 pins

| Pin(s)   | Name             | Direction | Description                         | Usage                     |
|----------|------------------|-----------|-------------------------------------|---------------------------|
| A0-A3    | Address          | In/Out    | BUS Address                         | Memory BUS                |
| A4-A11   | Address          | Out       | BUS Address             (12b = 4KB) | Memory BUS                |
| D0-D7    | Data             | In/Out    | BUS Data                (8b Data)   | Memory BUS                |
| BRW      | 0-Read/1-Write   | In/Out    | BUS Operation                       | Memory BUS                |
| BA       | BUS Available    | In        | BUS Available for use flag          | Memory BUS                |
| BU       | BUS Used         | Out       | BUS Used by the chip flag           | Memory BUS                |
| R        | Red              | Out       | Pixel Red Analog Signal             | Pixel Output              |
| G        | Green            | Out       | Pixel Green Analog Signal           | Pixel Output              |
| B        | Blue             | Out       | Pixel Blue Analog Signal            | Pixel Output              |
| VBL      | VBlanking Signal | Out       | Vertical Blanking Signal            | Picture Timing            |
| HBL      | HBlanking Signal | Out       | Horizontal Blanking Signal          | Picture Timing            |
| CLK      | Master Clock     | In        | Master clock input                  | Clock                     |
| RST      | Reset            | In        | Reset signal                        | Boot                      |
| VSS      | Ground           | -         | Ground connection                   | Power supply              |
| VDD      | Power            | -         | Positive power supply               | Power supply              |

```
            +----------+
    Vdd  1  |~        ~|  32 Vss
     A0  2 <|>        <|> 31 BRW
     A1  3 <|>        <|> 30 BA
     A2  4 <|>        <|  29 BU
     A3  5 <|>         |> 28 R
     A4  6 <|          |> 27 G
     A5  7 <|          |> 26 B
     A6  8 <|         <|  25 CLK
     A7  9 <|         <|> 24 D7
     A8 10 <|         <|> 23 D6
     A9 11 <|         <|> 22 D5
    A10 12 <|         <|> 21 D4
    A11 13 <|         <|> 20 D3
    VBL 14 <|         <|> 19 D2
    HBL 15 <|         <|> 18 D1
    RST 16  |>        <|> 17 D0
            +----------+
```
