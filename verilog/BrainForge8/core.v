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
module BrainForge8 (
    // BUS INTERFACE
    inout   wire    [7:0]   D,      // Data bus
    inout   wire    [15:0]  A,      // Address bus
    inout   wire            RW,     // Read/Write control
    inout   wire            FI,     // Fetch Instruction
    inout   wire            DT,     // Data Transfer
    output  wire            BR,     // Bus Request
    input   wire            BA,     // Bus Available

    // INTERRUPT INTERFACE
    input   wire    [2:0]   INT,    // Interrupt request
    input   wire            RST,    // Reset
    output  wire            IRQ,    // External request

    // FLOW INTERFACE
    input   wire            CLK,    // System clock
    input   wire            HLD,    // Hold
    input   wire            STP,    // Step
    input   wire            TRA     // Trace
);

    // Interrupt Unit
    IRC interruptController (
        // TIMING
        .CLK(CLK),  // Master Clock

        // INT
        .RST(RST),  // Reset
        .INT(INT),  // Interrupts (0-7, 0 is inactive, 7 is NMI)
        .IRQ(IRQ)   // Interrupt Request

        // EXPOSED
        .NEXT_ID(x),
        .NEXT_ON(x),
        .RESET_ON(x),
        .ACK(x),

        // TRIGGER
        .TRIG_ID(x),
        .TRIG_ON(x)
    );

    // DMA Unit
    DMA dma (
        // TODO
    );

    // BUS Unit
    BUS bus (
        // BUS
        .D(D),      // Data bus
        .A(A),      // Address bus
        .RW(RW),    // Read/Write control
        .FI(FI),    // Fetch Instruction
        .DT(DT),    // Data Transfer
        .BR(BR),    // Bus Request
        .BA(BA),    // Bus Available

        // Driver0 : Core
        .D0_DATA(core.BUS_DATA),
        .D0_ADDR(core.BUS_ADDR),
        .D0_RW(core.BUS_RW),
        .D0_IF(core.BUS_IF),
        .D0_RQ(core.BUS_RQ),
        .D0_OK(core.BUS_OK),

        // Driver1 : DMA
        .D1_DATA(dma.BUS_DATA),
        .D1_ADDR(dma.BUS_ADDR),
        .D1_RW(dma.BUS_RW),
        .D1_RQ(dma.BUS_RQ),
        .D1_OK(dma.BUS_OK)
    );

    // Orchestration Unit
    ORCHESTRATOR orchestrator (
        .clk(CLK),  // System clock
        .HLD(HLD),  // Hold
        .STP(STP),  // Step
        .TRA(TRA)   // Trace
    );

    // Instruction Unit
    CORE core (
        // BUS
        // ...
    );

endmodule