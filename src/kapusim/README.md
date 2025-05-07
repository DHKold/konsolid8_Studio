# Audio Processing Unit (APU)

The `Apu` class is a software implementation of an Audio Processing Unit (APU) designed to process audio commands and generate audio samples. This document provides a detailed technical overview of the APU, including its commands, binary formats, and functionality.

---

## Table of Contents

1. [Overview](#overview)
2. [Initialization](#initialization)
3. [Command Execution](#command-execution)
4. [Command List and Formats](#command-list-and-formats)
5. [Audio Mixing Modes](#audio-mixing-modes)
6. [Usage](#usage)

---

## Overview

The `Apu` class processes a sequence of binary commands to control audio channels and generate audio samples. It supports multiple channels, each with configurable states and phases. The APU operates in cycles, executing commands. Channels generate samples at a fixed rate (44100Hz), and will never pause / stop. Event when a channel is muted or disabled, it still produces a default sampling (normaly 0 = no sound).

There are 8 channels (6 generic and 2 Sampled for Noise/DMC/...)
Each channel has a quality, which determines the maximum number of phases it can hold (2 to 16).

A phase is a modulation of the wave, it tell the channel what Amplitude to add (-255 to +255) to the current one, and how (using a stair/stepped progression) with the following properties:

- Step Count: 8bits (1 to 255, 0 being the same as 1). How many steps the stair will have
- Step Length: 11bits (1 to 1023, 0 being the same as 1). How many Sampling Cycles each steps will last
- Step Height: 9bits (Sign + Number, -255 to +255). How much amplitude to add at the at of each step. Final Amplitude is capped betwen 0-255.

The channel as a phase index (the Phase Active Id), which is decremented each time a phase is finished. If the index reaches 0, it goes back to the highest available id (Phase Maximum Id).

This systema allows to produce all kinds of waveform (pulse, square, triangle, sawtooth, custom ones, etc.)

---

## Command Execution

The APU processes commands using the `executeCommand` method. Each command is represented as a sequence of bytes, with the first byte containing the opcode and additional bytes encoding parameters. The `run` method executes commands over a specified number of cycles, simulating the generation of audio samples.

In a real APU, the Command Pipeline and the Channel Sampling run in individual area, each with their own flow. This idea is that the channels produce continously samples based on their configuration, while the APU runs the commands (loaded from the Audio RAM) to update the channel configuration in real time. The APU generate sounds by orchestrating the config changes with precision.

The APU global configuration can be read/written by the CPU using MMIO (Memory Mapped IO on the CPU_ADR0-2, CPU_DATA0-7, CPU_CE and CPU_RW pins).

---

## Command List and Formats

Below is a detailed list of supported commands, their binary formats, and descriptions. Each command is represented in a structured format inspired by assembly manuals.

### 1. **Wait Short**
| **Field**       | **Bits** | **Description**                     |
|-----------------|----------|-------------------------------------|
| `Opcode`        | 4 bits   | Operation code (`0b0000`).          |
| `Wait Cycles`   | 4 bits   | Number of cycles to wait (×10).     |

- **Format**: `OOOOCCCC`
    - `OOOO`: Opcode (`0b0000`).
    - `CCCC`: Wait cycles (in Sampling cycles so 1/44100s).
- **Description**: Pauses execution for a short duration. Only the APU commands are paused; the channels keep generating samples. This is meant to be used when no modification of the channels is required for a given duration.
- **Example**: `0x03` (Wait for 4 × 16 = 64 cycles).
- **KAA**: `Wait <Wait Cycles>` or `Noop` (equivalent to `Wait 0`).

---

### 2. **Wait Long**
| **Field**       | **Bits** | **Description**                     |
|-----------------|----------|-------------------------------------|
| `Opcode`        | 4 bits   | Operation code (`0b0001`).          |
| `Wait exponent` | 4 bits   | Base 2 exponent.                    |
| `Wait Mantissa` | 8 bits   | Number of cycles to wait.           |

- **Format**: `OOOOSSSS LLLLLLLL`
    - `OOOO`: Opcode (`0b0001`).
    - `EEEE`: Exponent in base 2.
    - `LLLLLLLL`: Wait cycles (in Sampling cycles so 1/44100s). Shifted by the exponent. Actual waiting time is L*2^E (1 to 8M cycles = 0.02ms to 190s)
- **Description**: Pauses execution for a long duration. Only the APU commands are paused; the channels keep generating samples. This is meant to be used when no modification of the channels is required for a given duration.
- **WARNING**: Stops execution if `waitCycles` is 0. The execution can be resumed by the CPU using MMIO.
- **Example**: `0x10 0xFF` (Wait for 255 cycles).
- **KAA**: `Wait <Mantissa>E<Exponent>` or `Stop`.

---

### 3. **Set Phase**
| **Field**         | **Bits** | **Description**                           |
|-------------------|----------|-------------------------------------------|
| `Opcode`          | 4 bits   | Operation code (`0b0010`).                |
| `Channel ID`      | 4 bits   | Target channel ID (0-7).                  |
| `Phase ID`        | 4 bits   | Phase ID to configure.                    |
| `Step Direction`  | 1 bit    | Direction of the phase (Down or Up).      |
| `Step Length`     | 11 bits  | Length of each step.                      |
| `Step Height`     | 8 bits   | Height of each step.                      |
| `Step Count`      | 8 bits   | Number of steps in the phase.             |

- **Format**: `OOOOCCCC XXXXDYYY YYYYYYYY AAAAAAAA BBBBBBBB`
    - `OOOO`: Opcode (`0b0010`).
    - `CCCC`: Channel ID.
    - `PPPP`: Phase ID.
    - `D` : Step Direction. 0 = Down, 1 = Up
    - `YYY YYYYYYYY`: Step Length
    - `AAAAAAAA` : Step Height, combined with the Step Direction to give (-255 to +255)
    - `BBBBBBBB` : Step Count
- **Description**: Configures a phase for a specific channel. Since a phase takes at least 1 cycle to load, this means it will always generate at least one sample even if Step Length or Step Count is 0.
- **Example**: `0x20 0x12 0x34 0x56 0x78` (Set phase for channel 0).
- **KAA**: `SetPhase CHAN<Channel ID>, <Phase ID>, <Step Length>, <Step Direction and Step Height combined>, <Step Count>`.

---

### 4. **Set All Channels**
#### Subcommand: Enable Channels
| **Field**         | **Bits** | **Description**                     |
|-------------------|----------|-------------------------------------|
| `Opcode`          | 4 bits   | Operation code (`0b0011`).          |
| `Subcommand`      | 4 bits   | Subcommand identifier (`1000`).     |
| `Channels Enabled`| 8 bits   | Bitmask of enabled channels.        |

- **Format**: `OOOOCCCC XXXXXXXX`
    - `OOOO`: Opcode (`0b0011`).
    - `CCCC`: Subcommand (`1000`).
    - `XXXXXXXX`: Channels enabled bitmask.
- **Example**: `0x38 0xFF` (Enable all channels).
- **KAA**: `EnableChannels <Channels Enabled>`.

#### Subcommand: Stereo Mode
| **Field**         | **Bits** | **Description**                     |
|-------------------|----------|-------------------------------------|
| `Opcode`          | 4 bits   | Operation code (`0b0011`).          |
| `Subcommand`      | 4 bits   | Subcommand identifier (`1001`).     |
| `Left Channels`   | 8 bits   | Bitmask of left channels.           |
| `Right Channels`  | 8 bits   | Bitmask of right channels.          |

- **Format**: `OOOOCCCC XXXXXXXX YYYYYYYY`
    - `OOOO`: Opcode (`0b0011`).
    - `CCCC`: Subcommand (`1001`).
    - `XXXXXXXX`: Left Enabled bitmask (LSB to MSB correspond to CHAN0 to CHAN7)
    - `YYYYYYYY`: Right Enabled bitmask (LSB to MSB correspond to CHAN0 to CHAN7)
- **Example**: `0x39 0xF0 0x0F` (Set channels 0-3 right, 4-7 left).
- **KAA**: `SetStereoMode <Left Channels>, <Right Channels>`.

---

### 5. **Set Phase IDs**
| **Field**         | **Bits** | **Description**                     |
|-------------------|----------|-------------------------------------|
| `Opcode`          | 4 bits   | Operation code (`0b0100`).          |
| `Channel ID`      | 4 bits   | Target channel Id (0-7).            |
| `Current Phase ID`| 4 bits   | Active phase Id.                    |
| `Max Phase ID`    | 4 bits   | Maximum phase Id.                   |
| `Phase Id Shift`  | 3 bits   | Shift the reference for the phases. |

- **Format**: `OOOOCCCC XXXXYYYY SSS_____`
    - `OOOO`: Opcode (`0b0100`).
    - `CCCC`: Channel Id.
    - `XXXX`: Active Phase Id.
    - `YYYY`: Maximum Phase Id.
    - `SSS`: Phase Id Shift.
- **Description**: Sets the active and maximum phase IDs for a channel. Each phase is executed by the channel from highest Id (Maximum Id) to lowest (0) then loops back.
The  Shift allow to rotate the phases to the left. For example with a Shift of 3, Phase0 to Phase15 becomes Phase3,...,Phase15,Phase0,...,Phase2. This can be used to store multipe sets of phases and run them indepently.
- **Example**: `0x40 0x12` (Set phase IDs for channel 0).
- **KAA**: `SetPhaseIds CHAN<Channel ID>, <Current Phase ID>, <Max Phase ID>, <Phase Id Shift>`.

---

### 6. **Set Loop**
| **Field**         | **Bits** | **Description**                          |
|-------------------|----------|------------------------------------------|
| `Opcode`          | 4 bits   | Operation code (`0b0101`).               |
| `Loop Count`      | 6 bits   | Number of loop iterations.               |
| `Loop Length`     | 6 bits   | Length of the loop (Number of commands). |

- **Format**: `OOOOCCCC CCLLLLLL`
    - `OOOO`: Opcode (`0b0101`).
    - `CCCCCC`: Loop Count.
    - `LLLLLL` : Loop Length.
- **Description**: Configures a loop with a specific count and length. This will execute the following 'Length' commands 'Count' times. Using a SetLoop inside an existing loop overides the existing one (no stacking is done)
- **Example**: `0x50 0x3F` (Set loop with 3 iterations and length 15).
- **KAA**: `SetLoop <Loop Count>, <Loop Length>`.

---

### 7. **Save State**
| **Field**         | **Bits** | **Description**                     |
|-------------------|----------|-------------------------------------|
| `Opcode`          | 4 bits   | Operation code (`0b0110`).          |
| `Channel ID`      | 4 bits   | Target channel ID (0-7).            |

- **Format**: `OOOOCCCC`
    - `OOOO`: Opcode (`0b0110`).
    - `CCCC`: Channel ID.
- **Description**: Saves the current state of the specified channel into its single-level save register. This is useful for temporarily pausing a channel's state to play other audio.
- **Example**: `0x60` (Save state for channel 0).
- **KAA**: `SaveState CHAN<Channel ID>`.

---

### 8. **Load State**
| **Field**         | **Bits** | **Description**                     |
|-------------------|----------|-------------------------------------|
| `Opcode`          | 4 bits   | Operation code (`0b0111`).          |
| `Channel ID`      | 4 bits   | Target channel ID (0-7).            |

- **Format**: `OOOOCCCC`
    - `OOOO`: Opcode (`0b0111`).
    - `CCCC`: Channel ID.
- **Description**: Loads the saved state from the save register of the specified channel and sets it as the current state. This is used to resume a channel's state after temporary audio playback.
- **Example**: `0x70` (Load state for channel 0).
- **KAA**: `LoadState CHAN<Channel ID>`.

---

## Audio Mixing Modes

The APU supports two audio mixing modes, controlled by the `mixerMode` attribute:

1. **Mode 0 (Capped Sum)**:
     - Combines samples by summing them and capping the result at `APU_AMPLITUDE_MAX`.

2. **Mode 1 (Average)**:
     - Combines samples by averaging their values.

---

## Usage

### Example

```python
from apu import Apu, APU_CLOCK_RATIO

# Initialize APU
apu = Apu()

# Command data (binary sequence)
data = bytes([0x03, 0x10, 0xFF, 0x20, 0x12, 0x34, 0x56, 0x78])

# Run APU for 160 cycles (using a multiple of the ratio for sampling coherence)
samples = apu.run(data, cycles=160 * APU_CLOCK_RATIO)

# Output generated samples
print(samples)
```