# APU (Audio Processing Unit)

This document describes the HUPUF2X8A (Hutech PulseForge Stereo 2x8b Analog), an Audio Synthesis Chip.

- Company: Hutech
- Series: PulseForge
- Model: HUPUF2X8A
- Release: 01-01-1987

## Overview

The APU produces an Analog Stereo Output (0-3V).
The sound generation is done by sampling and mixing multiple channels (Up to 16 depending on the chip Model).
There are two types of channels: segmented and sampled.

### Device Variants

The chip is currenlty only available with 8 Channels: 6 Segmented Channels (Quality: 2xHigh, 2xMediumA, 2xLow) and 2 Sampled Channels.

It comes in the following references:

- HUPUF2X8A-DIP20

### Packagind

DIP-20 version:

| Pin(s)   | Name             | Direction | Description                         | Usage                     |
|----------|------------------|-----------|-------------------------------------|---------------------------|
| RA0-RA3  | Register Address | In        | Register Access Address             | Exposed Registers         |
| RD0-RD7  | Register Data    | In/Out    | Register Access Data                | Exposed Registers         |
| RRW      | Register R/W     | In        | Register Access Read/Write control  | Exposed Registers         |
| RAE      | Register Enable  | In        | Register Access Enable Signal       | Exposed Registers         |
| L        | Left             | Out       | Sound Left Analog Signal            | Sound Output              |
| R        | Right            | Out       | Sound Right Analog Signal           | Sound Output              |
| CLK      | Master Clock     | In        | Master clock input                  | Clock                     |
| RST      | Reset            | In        | Reset signal                        | Boot                      |
| VSS      | Ground           | -         | Ground connection                   | Power supply              |
| VDD      | Power            | -         | Positive power supply               | Power supply              |

```
            +----------+
    Vdd  1  |~        ~|  20 Vss
    RA0  2  |>        <|  19 RD7
    RA1  3  |>        <|  18 RD6
    RA2  4  |>        <|  17 RD5
    RA3  5  |>        <|  16 RD4
    CLK  6  |>        <|  15 RD3
    RST  7 <|         <|  14 RD2
    RRW  8 <|         <|  25 RD1
    RAE  9 <|         <|  24 RD0
      L 10 <|          |> 23 R
            +----------+
```

### Electrical Characteristics

TODO

### Block Diagram

TODO

## Exposed Registers

The first 8 registers are the global APU ones:

|   Id | Name            | Description                                                              |
|------|-----------------|--------------------------------------------------------------------------|
| 0000 | Status          | Status of the APU: TBD                                                   |
| 0001 | Active Channels | ABCDEFGH : 0 means the Channel is not running (not clock signal)         |
| 0010 | Global Flags    | Global flags: MixingAvg, TBD                                             |
| 0011 | Mixing Volume A | AABBCCDD : Volume for channels 0-3 (4x2b)                                |
| 0100 | Mixing Volume B | AABBCCDD : Volume for channels 4-7 (4x2b)                                |
| 0101 | Mixing Stero L  | ABCDEFGH : Stereo Left Enabled (8x1b)                                    |
| 0110 | Mixing Stero R  | ABCDEFGH : Stereo Right Enabled (8x1b)                                   |
| 0111 | Select Exposed  | Select the exposed Channel (4b) and Segment (4b)                         |

The next 6 registers are used to control the channels, and as such, their role depends on what Channel and Segment is selected in register 0x0111.

For Segmented channels 0 and 1 (High Quality):

|   Id | Name            | Description                                                              |
|------|-----------------|--------------------------------------------------------------------------|
| 1000 | Channel Conf0   | SegmentIdShift (4b) + Flags (4b)                                         |
| 1001 | Channel Conf1   | SegmentActiveId (4b) + SegmentMaxId (4b)                                 |
| 1010 | Segment Conf0   | StepSign (1b) + StepLenght (7b hi)                                       |
| 1011 | Segment Conf1   | StepLength (8b lo)                                                       |
| 1100 | Segment Conf2   | StepHeight (8b unsigned)                                                 |
| 1101 | Segment Conf3   | StepCount                                                                |

For Segmented channels 2 and 3 (MediumA Quality):

|   Id | Name            | Description                                                              |
|------|-----------------|--------------------------------------------------------------------------|
| 1000 | Channel Conf0   | SegmentIdShift (4b) + Flags (4b)                                         |
| 1001 | Channel Conf1   | SegmentActiveId (4b) + SegmentMaxId (4b)                                 |
| 1010 | Segment Conf0   | StepSign (1b) + StepCount (7b)                                           |
| 1011 | Segment Conf1   | StepLength (8b)                                                          |
| 1100 | Segment Conf2   | StepHeight (8b unsigned)                                                 |
| 1101 | Unused          | Unused                                                                   |

For Segmented channels 4 and 5 (Low Quality), the two segments are exposed:

|   Id | Name            | Description                                                              |
|------|-----------------|--------------------------------------------------------------------------|
| 1000 | Channel Conf0   | SegmentIdShift (4b) + Flags (4b)                                         |
| 1001 | Channel Conf1   | SegmentActiveId (4b) + SegmentMaxId (4b)                                 |
| 1010 | Segment0 Conf0  | Segement0 SLLLLLLL : S=StepSign (1b), L=StepLength (7b)                  |
| 1011 | Segment0 Conf1  | Segement0 CCCCHHHH : C=StepCount (4b), H=StepHeight (4b unsigned)        |
| 1100 | Segment1 Conf0  | Segement1 SLLLLLLL : S=StepSign (1b), L=StepLength (7b)                  |
| 1101 | Segment1 Conf1  | Segement1 CCCCHHHH : C=StepCount (4b), H=StepHeight (4b unsigned)        |

For Sampled channels 6 and 7, registers 8-10 are generic, while the registers 11-13 depends on the Mode

|   Id | Name            | Description                                                              |
|------|-----------------|--------------------------------------------------------------------------|
| 1000 | Channel Conf0   | Modulation Mode (3b) + Flags (5b)                                        |
| 1001 | Channel Conf1   | BufferOffset (4b) + BufferMaxOffset (4b)                                 |
| 1010 | Channel Conf2   | BufferShift  (4b) + BufferWriteOffset (4b)                               |
| 1011 | Mode Conf0      | Mode Specific configuration                                              |
| 1100 | Mode Conf1      | Mode Specific configuration                                              |
| 1101 | Mode Conf2      | Mode Specific configuration                                              |

The last 2 registers allow to feed the Sampled Channels buffers.

|   Id | Name            | Description                                                                          |
|------|-----------------|--------------------------------------------------------------------------------------|
| 1110 | Samples BufferA | BufferWrite: when written, will write to the Buffer of the first Sampled Channel     |
| 1111 | Samples BufferB | BufferWrite: when written, will write to the Buffer of the second Sampled Channel    |

## Segmented Channels

Segmented Channels are designed to generate complex waveforms by chaining together multiple amplitude segments, with support for up to 16 segments per channel. Each segment represents a unidirectional amplitude change—rising, falling, or steady—implemented as a sequence of discrete steps. This approach enables the synthesis of a wide variety of waveforms, such as pulses, triangles, and sawtooth patterns, by precisely controlling the amplitude at each step.

A segment is defined by three key parameters:

- **Step Length**: The duration of each step, specified in clock cycles. This controls the horizontal resolution of the segment.
- **Step Height**: The amplitude increment or decrement applied at each step. This determines how sharply the amplitude changes.
- **Step Count**: The total number of steps in the segment, which sets the overall length of the segment.

By adjusting these parameters, users can construct intricate amplitude envelopes. For example:

- A triangle is made of a smoothly rising segment (e.g. +4 x 64 for 35 cycles) and a smoothly falling one (e.g. -4 x 64 for 35 cycles).
- A pulse waveform can be achieved by combining a sharp rising segment (max step height) with a sharp falling one (max step height), the length x count allowing to set the pulse frequency.
- A sawtooth is made of a slow rising segment followed by a sudden drop (there are two ways to achieve this).

The channel's quality setting determines the maximum number of segments and the granularity of control available. Higher quality settings allow for more segments and finer step resolution, enabling more detailed and expressive waveforms. Lower quality settings reduce the number of segments and step precision, which may be suitable for simpler sounds.

Segmented Channels thus provide a flexible and efficient method for generating a wide range of analog-style waveforms, making them suitable for both musical synthesis and sound effects in embedded audio applications.

### Channel Configuration

A channel cycles through its configured segments to generate a complete waveform. The `SegmentCurrentId` tracks which segment is currently active. When the current segment finishes processing, `SegmentCurrentId` is incremented. If it exceeds `SegmentMaxId` (the highest segment index to use), it wraps back to 0, creating a repeating loop of segments.

Segments can be shifted using `SegmentIdShift`, which offsets the segment indices used by the channel. This allows for flexible reuse of segment data. For example, if `SegmentMaxId` is 1, the channel cycles between segments 0 and 1. If `SegmentIdShift` is set to 2, the channel instead cycles between segments 2 and 3. This mechanism enables storing multiple sets of segments (such as different notes or waveforms) and selecting among them by adjusting the shift value.

Typical use cases include storing several waveform patterns or notes in the segment table and switching between them dynamically by changing `SegmentIdShift`.

Each channel also has a set of flags that modify its behavior:

- **TriangularDelta**: On each step, the `StepHeight` is incremented or decremented by 1 (depending on the direction), creating a triangular amplitude progression within the segment.
- **Bouncy**: Normally, if the amplitude reaches its minimum or maximum (e.g., 0 or 255), it is clamped at that value. With the Bouncy flag enabled, the sign of `StepHeight` is inverted at the limit, causing the amplitude to "bounce" back in the opposite direction.
- **FinalDrop**: When set, at the end of a segment, the amplitude is forced to the minimum (for rising segments) or maximum (for falling segments), ensuring a sharp transition.
- **Noisy**: Random noise is added to the output samples. This affects only the output, not the internal amplitude, so the overall waveform shape is preserved.

| Config            | Size | Range  | Description                                                                                   |
|-------------------|------|--------|-----------------------------------------------------------------------------------------------|
| SegmentCurrentId  |  4b  | 0-15   | Index of the currently active segment in the channel's segment sequence.                      |
| SegmentIdShift    |  4b  | 0-15   | Offset applied to segment indices, allowing selection of different segment groups.            |
| SegmentMaxId      |  4b  | 0-15   | Highest segment index to use; channel cycles from 0 to this value (after applying shift).     |
| Flags             |  4b  | field  | Bitfield for channel behavior: TriangularDelta, Bouncy, FinalDrop, Noisy (see above).         |

### Segment Configuration

Each segment is configured using the following parameters:

| Config      | Size              | Range                | Description                                          |
|-------------|-------------------|----------------------|------------------------------------------------------|
| StepSign    | 1 bit             | 0 or 1               | The direction of the segment (0=Rising, 1=Falling)   |
| StepLength  | L bits            | 1–2<sup>L</sup>      | The duration of each step (in clock cycles).         |
| StepHeight  | H bits (unsigned) | 0 to 2<sup>H</sup>–1 | The amplitude change applied at each step.           |
| StepCount   | C bits            | 1–2<sup>C</sup>      | The number of steps in the segment.                  |

The bit-widths (L, H, C) for these parameters depend on the channel's quality. Higher quality gives more detailed waveforms, but require more data (and so more operations/time) to setup.

| Quality         | Segments/Channel | StepSign | StepLength | StepHeight | StepCount | Amplitude Precision | Config Size per Segment | Total Config Size |
|-----------------|------------------|----------|------------|------------|-----------|---------------------|-------------------------|-------------------|
| **Master**      | 16               | 1 bit    | 15 bits    | 12 bits    | 12 bits   | 16 bits             | 5B                      | 80B               |
| **High**        | 16               | 1 bit    | 15 bits    | 8 bits     | 8 bits    | 12 bits             | 4B                      | 64B               |
| **Medium A**    | 8                | 1 bit    | 8 bits     | 8 bits     | 7 bits    | 8 bits              | 3B                      | 24B               |
| **Medium B**    | 4                | 1 bit    | 8 bits     | 8 bits     | 7 bits    | 8 bits              | 3B                      | 12B               |
| **Low**         | 2                | 1 bit    | 7 bits     | 4 bits     | 4 bits    | 4 bits              | 2B                      |  4B               |
| **Terrible**    | 2                | 1 bit    | 3 bits     | 2 bits     | 2 bits    | 4 bits              | 1B                      |  1B               |

## Sampled Channels

Global configuration per channel:

| Config            | Size | Range  | Description                                                                                       |
|-------------------|------|--------|---------------------------------------------------------------------------------------------------|
| BufferOffset      |  4b  | 0-15   | Current buffer Offset. Not that depending on BitsPerSample, a buffer may hold multiple samples    |
| BufferOffsetShift |  4b  | 0-15   | Offset applied to buffer offset, allowing selection of different buffer groups.                   |
| BufferMaxOffset   |  4b  | 0-15   | Highest buffer offset to use; channel cycles from 0 to this value (after applying shift).         |
| WriteOffset       |  4b  | 0-15   | Offset where the next incoming data will go. Automatically incremented on write.                  |
| ModulationType    |  4b  | 0-15   | Type of modulation (0=Amp, 1=Sign, 2=Period, 3=Noise or 4=Delta)                                  |

Buffer size depends is 16B.

### AmpMode (Amplitude Modulation)

Each sample bitfield directly sets the amplitude.

Mode Registers:

|   Id | Name            | Description                                                        |
|------|-----------------|--------------------------------------------------------------------|
| 1011 | PeriodLength_Lo | Duration of each sample in SamplingCycles                          |
| 1100 | PeriodLength_Hi | Duration of each sample                                            |
| 1101 | BitsPerSample   | Number of bits to consume for each sample (= Resolution)           |

Flags:

| Bit | Name       | Description                                                              |
|-----|------------|--------------------------------------------------------------------------|
| 0-4 |            | TDB                                                                      |

### SignMode (Delta Sign Modulation)

1-bit samples toggle delta sign; amplitude changes by fixed DeltaAmp.

Mode Registers:

|   Id | Name            | Description                                                        |
|------|-----------------|--------------------------------------------------------------------|
| 1011 | PeriodLength_Lo | Duration of each sample in SamplingCycles                          |
| 1100 | PeriodLength_Hi | Duration of each sample                                            |
| 1101 | DeltaAmplitude  | How much amplitude to add/remove on each sample                    |

Flags:

| Bit | Name       | Description                                                              |
|-----|------------|--------------------------------------------------------------------------|
| 0-4 |            | TDB                                                                      |

### PeriodMode (Period Modulation)

Alternates between MinAmp and MaxAmp; sample defines duration of the period.

Mode Registers:

|   Id | Name            | Description                                                        |
|------|-----------------|--------------------------------------------------------------------|
| 1011 | AAABBBB0        | A=BitsPerSample (3b 1-8), B=PeriodE2Scale (4b 1-2^16)              |
| 1100 | AmpMin          | Amplitude of the low sample                                        |
| 1101 | AmpMax          | Amplitude of the high sample                                       |

Flags:

| Bit | Name       | Description                                                              |
|-----|------------|--------------------------------------------------------------------------|
| 0-4 |            | TDB                                                                      |

### NoiseMode (Random Noise Modulation)

Use pseudo-random bits (LFSR) as the sample stream.

Mode Registers:

|   Id | Name            | Description                                                        |
|------|-----------------|--------------------------------------------------------------------|
| 1011 | PeriodLength    | Duration of each sample in SamplingCycles                          |
| 1100 | XorMask         | Mask to apply to each sample                                       |
| 1101 | RandomConfig    | Defines how the sample is generated from random (Taps, Transfo)    |

Flags:

| Bit | Name       | Description                                                              |
|-----|------------|--------------------------------------------------------------------------|
| 0-4 |            | TDB                                                                      |

### DeltaMode (Delta Modulation)

Each sample gives a signed delta to apply (e.g., 4-bit or 6-bit with sign).

Mode Registers:

|   Id | Name            | Description                                                        |
|------|-----------------|--------------------------------------------------------------------|
| 1011 | PeriodLength_Lo | Duration of each sample in SamplingCycles                          |
| 1100 | PeriodLength_Hi | Duration of each sample                                            |
| 1101 | BitsPerSample   | Number of bits to consume for each sample                          |

Flags:

| Bit | Name       | Description                                                              |
|-----|------------|--------------------------------------------------------------------------|
| 0-4 |            | TDB                                                                      |

## Sampling & Mixing Unit

### Sampling

- How the channels are sampled
- How the Clock affect the sampling Rate

### Mixing

### Mixing Registers and Process

The APU uses several registers to control how channel outputs are mixed into the final stereo signals:

- **0x03 Mixing Volume A**: Volume for channels 0–3 (2 bits per channel; `00` = 100%, `01` = 50%, `10` = 25%, `11` = 12.5%)
- **0x04 Mixing Volume B**: Volume for channels 4–7 (same encoding as above)
- **0x05 Mixing Stereo L**: Left channel enable (1 bit per channel; `1` = enabled, `0` = muted)
- **0x06 Mixing Stereo R**: Right channel enable (1 bit per channel; `1` = enabled, `0` = muted)
- **Global Flag: MixingAvg**: Determines the mixing output mode (see below)

**Mixing Process:**

1. **Volume Scaling:**  
    Each channel's sample is scaled according to its volume setting. This is implemented as a right bit-shift by 0–3, corresponding to the 2-bit volume value.

2. **Channel Routing:**  
    For each channel, if it is enabled for Left and/or Right output (per the enable registers), its scaled sample is added to the corresponding Left and/or Right mixing buffer.

3. **Mixing Buffer Handling:**  
    The Left and Right mixing buffers are 11 bits wide to accommodate the sum of multiple channels without overflow.

    - If the `MixingAvg` flag is **cleared** (`0`):  
      The buffer value is capped at 255 (8 bits max) before output, preventing overflow distortion.
    - If the `MixingAvg` flag is **set** (`1`):  
      The buffer value is divided by 8 (right-shifted by 3) before output, effectively averaging the mixed signal and reducing the risk of clipping.

4. **Analog Output:**  
    The processed Left and Right values are sent to the DACs, producing the final analog stereo output on the L and R pins.

This approach allows flexible per-channel volume control, selective routing to stereo outputs, and a choice between hard limiting or averaging to manage signal levels when mixing multiple channels.

## Usage

### Initialization

Upon power-up or reset, **all registers are initialized to zero**. This default state has the following effects:

- **All channels are disabled**: No audio output is generated until channels are explicitly configured and enabled.
- **Left and Right outputs are muted**: The stereo outputs remain silent until the appropriate mixing and channel enable registers are set.

**Resetting** the device (via the RST pin) will restore all registers to their default value of zero, returning the APU to its initial, inactive state.

### Setup

To begin audio output, you must configure the necessary registers to enable channels, set mixing options, and load waveform or sample data as required.

### Register Access Process

The APU is controlled via a parallel register interface using the following pins:

- **RA0–RA3**: Register Address (4 bits)
- **RD0–RD7**: Register Data (8 bits, bidirectional)
- **RRW**: Register Read/Write (1 = Read, 0 = Write)
- **RAE**: Register Access Enable (active high)
- **CLK**: Master Clock

#### General Register Write Sequence

1. **Set Address**: Place the target register address (0–15) on RA0–RA3.
2. **Set Data**: Place the data byte to write on RD0–RD7.
3. **Set RRW**: Set RRW low (0) to indicate a write operation.
4. **Enable Access**: Set RAE high (1) to enable register access.
5. **Clock Pulse**: Pulse the CLK pin to latch the data into the register.
6. **Disable Access**: Set RAE low (0) after the operation.

#### General Register Read Sequence

1. **Set Address**: Place the target register address (0–15) on RA0–RA3.
2. **Set RRW**: Set RRW high (1) to indicate a read operation.
3. **Enable Access**: Set RAE high (1).
4. **Clock Pulse**: Pulse the CLK pin; the register data will appear on RD0–RD7.
5. **Read Data**: Capture the value from RD0–RD7.
6. **Disable Access**: Set RAE low (0).

---

### Example: Configuring Audio Output

#### 1. Set Global Flags

- **Register 0x02**: Write global flags (e.g., enable MixingAvg if desired).

#### 2. Configure Mixing

- **Registers 0x03 & 0x04**: Set volume for channels 0–7 (2 bits per channel).
- **Registers 0x05 & 0x06**: Enable channels for Left/Right output (1 bit per channel).

#### 3. Enable Channels

- **Register 0x01**: Set bits for each channel to enable (1 = active).

#### 4. Select Channel and Segment

- **Register 0x07**: Write the selected channel (4 bits) and segment (4 bits) to expose for configuration.

#### 5. Configure Channel and Segment

- **Registers 0x08–0x0D**: Write channel and segment parameters (see channel type for details).
    - For segmented channels: set SegmentIdShift, Flags, StepLength, StepHeight, StepCount, etc.
    - For sampled channels: set modulation mode, buffer offsets, and mode-specific registers.

#### 6. Load Sample Data (Sampled Channels)

- **Registers 0x0E/0x0F**: Write sample data bytes to the buffer for sampled channels.

---

**Note:** Repeat steps 4–6 for each channel and segment as needed. All register accesses must follow the sequence above using the Register Access pins and clock.

### Modulation Techniques

There are several ways to modulate the sound of a channel, enabling dynamic and expressive audio effects:

- **Direct Segment Manipulation (Channels 4/5):**  
    Channels 4 and 5 expose both of their segments simultaneously, so you can adjust parameters like `StepLength` for both the rising and falling segments without switching the Select Register. This allows rapid frequency changes with just two register writes—one for each segment.

- **Using Flags for Shape Modulation:**  
    The `FinalDrop` and `Bouncy` flags can create complex waveforms using a single segment:
        - **Example 1 (Bouncy, Square Wave):**  
            With a 352.8kHz clock, set `Bouncy` and configure one segment (`sign=1`, `len=882`, `height=255`, `count=2`). The amplitude jumps to 255 after 2.5ms, then returns to 0 after another 2.5ms due to the bounce, producing a 200Hz square wave. You can change the frequency by updating just the segment's `StepLength`.
        - **Example 2 (Bouncy, Triangle Wave):**  
            With `Bouncy` enabled and a segment (`sign=1`, `len=11`, `height=3`, `count=85`), the amplitude rises and falls smoothly, generating a triangle wave at approximately 189Hz.
        - **Example 3 (FinalDrop, Sawtooth):**  
            With `FinalDrop` enabled and a segment (`sign=1`, `len=5`, `height=1`, `count=255`), the amplitude ramps up to 255 over 3.61ms, then drops instantly to 0, creating a 276Hz sawtooth wave.

- **Segment Selection via `SegmentMaxId` and `SegmentIdShift`:**  
    - Set `SegmentMaxId=0` and adjust `SegmentIdShift` to loop on a single segment (segment X). This allows you to switch waveforms instantly by changing the shift value.
    - Set `SegmentMaxId=1` and use even values for `SegmentIdShift` (0, 2, 4, ...) to loop over two consecutive segments (X and X+1), enabling quick waveform changes.
    - Note: the same logic can be used for the Sampled Channels with the Buffer configuration.

- **Real-Time Register Updates:**  
    Since any register can be modified at any time—even between waveform steps—you can achieve highly dynamic and complex modulations by carefully timing register writes.

These techniques can be combined to produce a wide variety of modulated sounds, from simple vibrato and tremolo to intricate, evolving waveforms.

## Circuit Integration

### Example 1: Typical Jack 2.5 Audio Output Circuit

To connect the APU's analog stereo outputs (L and R) to a standard 2.5mm audio jack, a simple buffer and coupling circuit is recommended. This ensures proper signal levels, impedance matching, and DC isolation for safe and clean audio output.

**Example Circuit:**

```
    +3V
     |
    [R1] 10k
     |
    +----+------------------+
    |    |                  |
  [C1] 1uF               [C2] 1uF
    |    |                  |
    |   (L)                (R)
    |    |                  |
  [R2] 100k              [R3] 100k
    |    |                  |
    +----+------------------+
          |
        (GND)
```

- **L/R**: APU analog outputs (Left/Right)
- **C1/C2**: Coupling capacitors (1µF, non-polarized) block DC offset
- **R1**: Pull-up resistor to bias the op-amp input (if needed)
- **R2/R3**: Load resistors (100kΩ) to ground
- **GND**: Audio ground

**Optional Op-Amp Buffer:**

For best performance, buffer each output with a unity-gain op-amp (e.g., TL072, LM358):

```
APU L/R ---[C1/C2]---[Op-Amp Buffer]--- Jack Tip/Ring
```

- The op-amp input is AC-coupled via C1/C2.
- The op-amp output drives the jack directly, providing low output impedance and protecting the APU from load variations.

**Jack Pinout:**

- **Tip**: Left
- **Ring**: Right
- **Sleeve**: Ground

**Notes:**

- Use non-polarized capacitors for coupling.
- Choose op-amps with rail-to-rail output if the supply is 3V.
- For mono output, sum L and R with resistors before the jack.

This circuit ensures compatibility with headphones or line-in audio devices using a standard 2.5mm jack.
### Example 2 – RCA Output

To connect the APU's analog output to a standard RCA (phono) connector for composite audio, use a similar approach as with the headphone jack, but typically buffer the signal with an op-amp to ensure proper drive capability and signal integrity.

**Typical RCA Output Circuit:**

```
    +3V
     |
    [R1] 10k
     |
    +----+------------------+
    |    |                  |
  [C1] 1uF               [C2] 1uF
    |    |                  |
    |   (L)                (R)
    |    |                  |
   [Op-Amp]             [Op-Amp]
    |    |                  |
    |    +----+        +----+
    |         |        |
   (RCA-L)  (GND)   (RCA-R)
```

- **L/R**: APU analog outputs (Left/Right)
- **C1/C2**: Coupling capacitors (1µF, non-polarized) to block DC offset
- **R1**: Pull-up resistor (10kΩ) for biasing if needed
- **Op-Amp**: Unity-gain buffer (e.g., TL072, LM358) for each channel
- **RCA-L/RCA-R**: RCA connector center pins (Left/Right)
- **GND**: RCA connector shield (ground)

**Notes:**
- Use rail-to-rail op-amps if powered at 3V.
- The op-amp buffers provide low output impedance, suitable for driving long cables or standard audio equipment.
- For mono output, sum L and R through resistors before the op-amp and connect to a single RCA jack.
- Ensure all grounds are connected to avoid hum or noise.

This configuration allows the APU to interface cleanly with consumer audio equipment via RCA composite inputs.
