// DMA.v
// Simple DMA controller for BrainForge8 (task-based refactoring with reset and busy signal)

module DMA (
    // Control
    input  wire        CLK,            // System clock
    input  wire        RST,            // Asynchronous active-low reset
    input  wire        RUN,            // RUN transfer
    input  wire [15:0] SRC,            // Source address
    input  wire [15:0] DST,            // Destination address
    input  wire [7:0]  LEN,            // Byte count
    input  wire [7:0]  INC,            // Destination increment value

    // Bus interface
    inout  wire [7:0]  D,              // Data bus
    output reg  [15:0] A,              // Address bus
    output reg         RW,             // Read/Write (1=read, 0=write)
    output wire        BR,             // Bus Request (derived)
    input  wire        BA,             // Bus Acknowledge

    // Interrupt outputs
    output reg         TRIG_DMAD,      // Pulse when transfer completes
    output reg         TRIG_DMAE,      // Pulse on erroneous RUN

    // Status
    output wire        BUSY           // High when transfer in progress
);

    // State encoding
    localparam [2:0]
        S_IDLE     = 3'd0,
        S_REQ_BUS  = 3'd1,
        S_READ     = 3'd2,
        S_WRITE    = 3'd3,
        S_COMPLETE = 3'd4,
        S_CLEANUP  = 3'd6;

    // Internal registers
    reg [2:0]  state;
    reg [15:0] src, dst;
    reg [7:0]  len, inc;
    reg [7:0]  data_buf;

    // Derived signals
    assign BR   = (state == S_REQ_BUS || state == S_READ || state == S_WRITE);
    assign BUSY = (state != S_IDLE);
    assign D    = (state == S_WRITE) ? data_buf : 8'bz;

    //------------------------------------------------------------------------------
    // Tasks for each state (with descriptions)
    //------------------------------------------------------------------------------

    // IDLE state: wait for 'RUN', load parameters, then request bus
    task task_idle; begin
        RW <= 1'b1;  // default to read
        if (RUN) begin
            src     <= SRC;           // initialize source pointer
            dst     <= DST;           // initialize destination pointer
            len     <= LEN;           // byte count
            inc     <= INC;           // destination increment
            state   <= S_REQ_BUS;     // request bus next
        end
    end endtask

    // REQ_BUS state: hold BR, wait for BA, decide next state
    task task_req_bus; begin
        if (BA) begin
            if (len == 8'd0)
                state <= S_COMPLETE;  // done immediately if zero length
            else begin
                RW    <= 1'b1;        // prepare for read
                A     <= src;         // source address
                state <= S_READ;      // capture data next
            end
        end
    end endtask

    // READ state: capture data from bus, prepare for write
    task task_read; begin
        data_buf <= D;            // latch data from bus
        RW       <= 1'b0;         // prepare for write
        A        <= dst;          // destination address
        state    <= S_WRITE;      // perform write next
    end endtask

    // WRITE state: send data, update pointers/count, loop or finish
    task task_write; begin
        if (BA) begin
            src   <= src + 1;      // advance source pointer
            dst   <= dst + inc;    // advance destination pointer
            len   <= len - 1;      // decrement counter
            state <= S_REQ_BUS;    // request next byte
        end
    end endtask

    // COMPLETE state: signal done, then cleanup
    task task_complete; begin
        TRIG_DMAD <= 1'b1;        // pulse done interrupt
        state <= S_CLEANUP;       // move to cleanup
    end endtask

    // CLEANUP state: reset registers, return to IDLE
    task task_cleanup; begin
        src   <= 16'b0;           // clear source pointer
        dst   <= 16'b0;           // clear destination pointer
        len   <= 8'b0;            // clear byte count
        inc   <= 8'b0;            // clear increment
        RW    <= 1'b1;            // default to read
        state <= S_IDLE;          // go idle
    end endtask

    //------------------------------------------------------------------------------
    // Main FSM with asynchronous reset
    //------------------------------------------------------------------------------
    always @(posedge CLK or negedge RST) begin
        if (!RST) begin
            // asynchronous reset: go to idle state
            TRIG_DMAD  <= 1'b0;
            TRIG_DMAE  <= 1'b0;
            task_cleanup();
        end else begin
            // Clear pulses and detect erroneous RUN
            TRIG_DMAD <= 1'b0;
            TRIG_DMAE <= (RUN && state != S_IDLE);

            // Cancel
            if (RUN && LEN == 0) begin
                task_cleanup();
            end

            // State Machine
            case (state)
                S_IDLE:     task_idle();
                S_REQ_BUS:  task_req_bus();
                S_READ:     task_read();
                S_WRITE:    task_write();
                S_COMPLETE: task_complete();
                S_CLEANUP:  task_cleanup();
                default:    task_cleanup();
            endcase
        end
    end

endmodule