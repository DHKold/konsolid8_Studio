module BUS #(
    parameter ADDRESS_WIDTH = 16,
    parameter DATA_WIDTH = 8
) (
    // TIMING INTERFACE
    input   wire                        CLK,    // System clock
    input   wire                        RST,    // Reset

    // BUS INTERFACE
    inout   wire    [DATA_WIDTH-1:0]     D,     // Data bus
    inout   wire    [ADDRESS_WIDTH-1:0]  A,     // Address bus
    inout   wire                        RW,     // Read/Write control
    inout   wire                        IF,     // Instruction Fetch
    inout   wire                        DT,     // DMA Transfer
    output  wire                        BR,     // Bus Request
    input   wire                        BA,     // Bus Available

    // CORE INTERFACE
    inout   wire    [DATA_WIDTH-1:0]    D0_DATA, // Driver0 Data
    input   wire    [ADDRESS_WIDTH-1:0] D0_ADDR, // Driver0 Address
    input   wire                        D0_RW,   // Driver0 Read/Write
    input   wire                        D0_IF,   // Driver0 Fetch Instruction
    input   wire                        D0_BR,   // Driver0 Bus Request
    output  wire                        D0_BA,   // Driver0 OK (Signal to driver that transfer is complete)

    // DMA INTERFACE
    inout   wire    [DATA_WIDTH-1:0]    D1_DATA, // Driver1 Data
    input   wire    [ADDRESS_WIDTH-1:0] D1_ADDR, // Driver1 Address
    input   wire                        D1_RW,   // Driver1 Read/Write
    input   wire                        D1_BR,   // Driver1 Bus Request
    output  wire                        D1_BA    // Driver1 OK (Signal to driver that transfer is complete)
);

    // If any driver needs the BUS, we send the Request out
    assign BR = D0_BR | D1_BR;

    // Granting bus access with priority for Driver 0
    assign D0_BA = (BA && D0_BR);
    assign D1_BA = (BA && !D0_BR && D1_BR);

    // Data (tri-stated when no driver is active)
    assign D = (BA && D0_BR) ? D0_DATA :
               (BA && D1_BR) ? D1_DATA : {DATA_WIDTH{1'bZ}};

    // Address (tri-stated when no driver is active)
    assign A = (BA && D0_BR) ? D0_ADDR :
               (BA && D1_BR) ? D1_ADDR : {ADDRESS_WIDTH{1'bZ}};

    // Read/Write signal (tri-stated when no driver is active)
    assign RW = (BA && D0_BR) ? D0_RW :
                (BA && D1_BR) ? D1_RW : 1'bZ;

    // Fetch Instruction signal (tri-stated when no driver is active)
    assign IF = (BA && D0_BR) ? D0_IF :
                (BA && D1_BR) ? 1'b0 : 1'bZ;

    // Data Transfer signal (tri-stated when no driver is active)
    assign DT = (BA && D0_BR) ? 1'b0 :
                (BA && D1_BR) ? 1'b1 : 1'bZ;

endmodule