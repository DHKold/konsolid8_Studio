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