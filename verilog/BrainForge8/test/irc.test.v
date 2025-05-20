module IRC_Testbench;

    // Testbench Signals
    reg         CLK;
    reg  [3:0]  INT;
    reg         RST;
    reg         ACK;
    reg         TRIG_DMAD;
    reg         TRIG_DMAF;
    reg         TRIG_STOF;
    reg         TRIG_STUF;
    reg         TRIG_RSTB;
    reg         TRIG_IRQ0;

    wire [3:0]  NEXT_ID;
    wire        NEXT_ON;
    wire        RESET_ON;
    wire        IRQ;

    // Instantiate the IRC module
    IRC dut (
        // Pins
        .CLK(CLK),
        .INT(INT),
        .RST(RST),
        .IRQ(IRQ),
        // Interface
        .NEXT_ID(NEXT_ID),
        .NEXT_ON(NEXT_ON),
        .RESET_ON(RESET_ON),
        .ACK(ACK),
        // Triggers
        .TRIG_DMAD(TRIG_DMAD),
        .TRIG_DMAF(TRIG_DMAF),
        .TRIG_STOF(TRIG_STOF),
        .TRIG_STUF(TRIG_STUF),
        .TRIG_RSTB(TRIG_RSTB),
        .TRIG_IRQ0(TRIG_IRQ0)
    );

    // Clock generation
    initial begin
        CLK = 0;
        forever #5 CLK = ~CLK;  // 10ns period
    end

    // Test Sequence
    initial begin
        // Initialize signals
        RST = 1;
        INT = 0;
        ACK = 0;
        TRIG_DMAD = 0;
        TRIG_DMAF = 0;
        TRIG_STOF = 0;
        TRIG_STUF = 0;
        TRIG_RSTB = 0;
        TRIG_IRQ0 = 0;
        #10;

        // Reset Test
        $display("[Test] Reset Handling");
        RST = 0;
        #20;
        RST = 1;
        #50;
        ACK = 1;
        #50
        ACK = 0;
        
        // External Interrupt Test (INT[2:0] = 3'b001)
        $display("[Test] External Interrupt");
        INT = 4'b0001;
        #20;
        ACK = 1;
        #10;
        ACK = 0;
        #30;

        // Internal Trigger Test (TRIG_ID = 4)
        $display("[Test] Internal Trigger");
        TRIG_DMAD = 1;
        #20;
        TRIG_DMAD = 0;
        ACK = 1;
        #10;
        ACK = 0;
        #20;

        // Test IRQ Trigger
        $display("[Test] IRQ Trigger");
        TRIG_IRQ0 = 1;
        #10;
        TRIG_IRQ0 = 0;
        #10;
        ACK = 1;
        #15
        ACK = 0;
        #15

        // Multiple Interrupts
        $display("[Test] Multiple INT Changes");
        INT = 0;
        INT = 4'b0100;
        #2;
        INT = 4'b0010;
        #3;
        INT = 4'b1110;
        #25;
        ACK = 1;
        #50;
        ACK = 0;

        // Finish Test
        #50;
        $finish;
    end

    // Monitor Outputs
    always @(posedge CLK) begin
        $display("%t - IRQ: %b, NEXT_ID: %b, NEXT_ON: %b, RESET_ON: %b", $time, IRQ, NEXT_ID, NEXT_ON, RESET_ON);
    end

endmodule