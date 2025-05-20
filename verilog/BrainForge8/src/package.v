/*
 * BrainForge8 - A simple 8-bit microprocessor
 * 
 * This file is part of the BrainForge8 project.
 * 
 * The BrainForge8 project is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * The BrainForge8 project is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with the BrainForge8 project. If not, see <http://www.gnu.org/licenses/>.
 */
module PACKAGE (
    // BUS INTERFACE
    inout   wire    [7:0]   D,      // Data bus
    inout   wire    [15:0]  A,      // Address bus
    inout   wire            RW,     // Read/Write control
    inout   wire            IF,     // Instruction Fetch
    inout   wire            DT,     // DMA Transfer
    output  wire            BR,     // Bus Request
    input   wire            BA,     // Bus Available

    // INTERRUPT INTERFACE
    input   wire    [3:0]   INT,    // Interrupt request
    input   wire            RST,    // Reset
    output  wire            IRQ,    // External request

    // FLOW INTERFACE
    input   wire            CLK,    // System clock
    input   wire            HLD,    // Hold
    input   wire            STP     // Step
);

    // Common wiring : Interrupts
    wire            RSTB;                       // Global RSTB signal (hardware + software)

    wire [3:0]      INT_ID;                     // Interrupts: active interrupt ID
    wire            INT_ON;                     // Interrupts: active interrupt ongoing
    wire            INT_ACK;                    // Interrupts: acknowledge (clear active interrupt)

    wire            TRIG_DMAD;                  // Interrupts: Trigger DMA Done Interrupt
    wire            TRIG_DMAE;                  // Interrupts: Trigger DMA Error Interrupt
    wire            TRIG_STOF;                  // Interrupts: Trigger Stack Overflow Interrupt
    wire            TRIG_STUF;                  // Interrupts: Trigger Stack Underflow Interrupt
    wire            TRIG_RSTB;                  // Interrupts: Trigger Reset
    wire            TRIG_IRQ0;                  // Interrupts: Trigger IRQ0

    // Common wiring : DMA
    wire            DMA_RUN;
    wire [15:0]     DMA_SRC;
    wire [15:0]     DMA_DST;
    wire [7:0]      DMA_LEN;
    wire [7:0]      DMA_INC;

    wire [7:0]      DMA_BUS_D;
    wire [15:0]     DMA_BUS_A;
    wire            DMA_BUS_RW;
    wire            DMA_BUS_BR;
    wire            DMA_BUS_BA;

    wire            DMA_BUSY;

    // Common wiring : Core
    wire [7:0]      CORE_BUS_D;
    wire [15:0]     CORE_BUS_A;
    wire            CORE_BUS_RW;
    wire            CORE_BUS_IF;
    wire            CORE_BUS_BR;
    wire            CORE_BUS_BA;

    // Interrupt Unit
    IRC irc (
        // TIMING
        .CLK(CLK),  // Master Clock

        // INT
        .RST(RST),  // Reset
        .INT(INT),  // Interrupts Inputs
        .IRQ(IRQ),  // Interrupt Request Output

        // EXPOSED
        .NEXT_ID(INT_ID),
        .NEXT_ON(INT_ON),
        .RESET_ON(RSTB),
        .ACK(INT_ACK),

        // TRIGGER
        .TRIG_DMAD(TRIG_DMAD),
        .TRIG_DMAE(TRIG_DMAE),
        .TRIG_STOF(TRIG_STOF),
        .TRIG_STUF(TRIG_STUF),
        .TRIG_RSTB(TRIG_RSTB),
        .TRIG_IRQ0(TRIG_IRQ0)
    );

    // DMA Unit
    DMA dma (
        // Control
        .RST(RSTB),
        .CLK(CLK),
        .HLD(HLD),
        .STP(STP),

        .RUN(DMA_RUN),
        .SRC(DMA_SRC),
        .DST(DMA_DST),
        .LEN(DMA_LEN),
        .INC(DMA_INC),

        // BUS
        .D(DMA_BUS_D),
        .A(DMA_BUS_A),
        .RW(DMA_BUS_RW),
        .BR(DMA_BUS_BR),
        .BA(DMA_BUS_BA),

        // INT
        .TRIG_DMAD(TRIG_DMAD),
        .TRIG_DMAE(TRIG_DMAE),

        // STATE
        .BUSY(DMA_BUSY)
    );

    // BUS Unit
    BUS bus (
        // Control
        .RST(RSTB),
        .CLK(CLK),

        // BUS
        .D(D),      // Data bus
        .A(A),      // Address bus
        .RW(RW),    // Read/Write control
        .IF(IF),    // Fetch Instruction
        .DT(DT),    // Data Transfer
        .BR(BR),    // Bus Request
        .BA(BA),    // Bus Available

        // Driver0 : Core
        .D0_DATA(CORE_BUS_D),
        .D0_ADDR(CORE_BUS_A),
        .D0_RW(CORE_BUS_RW),
        .D0_IF(CORE_BUS_IF),
        .D0_BR(CORE_BUS_BR),
        .D0_BA(CORE_BUS_BA),

        // Driver1 : DMA
        .D1_DATA(DMA_BUS_D),
        .D1_ADDR(DMA_BUS_A),
        .D1_RW(DMA_BUS_RW),
        .D1_BR(DMA_BUS_BR),
        .D1_BA(DMA_BUS_BA)
    );

    // Instruction Unit
    CORE core (
        // Control
        .RST(RSTB),
        .CLK(CLK),
        .HLD(HLD),
        .STP(STP),

        // BUS
        .BUS_D(CORE_BUS_D),
        .BUS_A(CORE_BUS_A),
        .BUS_RW(CORE_BUS_RW),
        .BUS_IF(CORE_BUS_IF),
        .BUS_BR(CORE_BUS_BR),
        .BUS_BA(CORE_BUS_BA)

        // INT
        .INT_ID(INT_ID),
        .INT_ON(INT_ON),
        .INT_ACK(INT_ACK),
        .TRIG_RSTB(TRIG_RSTB),
        .TRIG_IRQ0(TRIG_IRQ0)

        // DMA
        .DMA_RUN(DMA_RUN),
        .DMA_SRC(DMA_SRC),
        .DMA_DST(DMA_DST),
        .DMA_LEN(DMA_LEN),
        .DMA_INC(DMA_INC),
        .DMA_BUSY(DMA_BUSY)
    );

endmodule