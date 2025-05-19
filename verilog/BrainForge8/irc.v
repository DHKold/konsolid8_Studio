/**
 * List of Interrupts:
 *   - 0000     IRQ
 *   - 0XXX     External INT 1-7
 *   - 1000     Reset
 *   - 1001     DMA Completion
 *   - 1010     DMA Exception
 *   - 1011     Stack Overflow
 *   - 1100     Stack Underflow
 *   - 1101     Reserved
 *   - 1110     Reserved
 *   - 1111     Reserved
 */
module IRC (
    // TIMING INTERFACE
    input   wire                CLK,        // System clock

    // INTERRUPTS INTERFACE
    input   wire    [2:0]       INT,        // Interruption Indicator
    input   wire                RST,        // Reset Interrupt
    output  reg                 IRQ,        // Interrupt Request

    // EXPOSED INTERFACE
    output  reg     [3:0]       NEXT_ID,    // Next Interrupt Identifier (0-15)
    output  reg                 NEXT_ON,    // Next Interrupt Active
    output  reg                 RESET_ON,   // Reset ongoing
    input   wire                ACK,        // Acknowledge Interrupt

    // INTERNAL TRIGGER
    input   wire    [3:0]       TRIG_ID,    // Trigger Id
    input   wire                TRIG_ON     // Trigger Active
);

    reg RST_SYNC1, RST_SYNC2;
    reg DISPATCHED = 0;

    // Task to handle reset logic
    task handle_reset;
        begin
            NEXT_ID     <= 0;
            NEXT_ON     <= 0;
            RESET_ON    <= 1;
            IRQ         <= 0;
            RST_SYNC1   <= 0;
            RST_SYNC2   <= 0;
            DISPATCHED  <= 0;
        end
    endtask

    // Task to handle interrupt acknowledgment
    task handle_ack;
        begin
            NEXT_ID <= 4'b0000;
            NEXT_ON <= 0;
            IRQ     <= 0;
        end
    endtask

    // Task to handle external interrupts
    task handle_external_interrupt;
        input [2:0] int_value;
        begin
            NEXT_ID     <= {1'b0, int_value};
            NEXT_ON     <= 1;
            DISPATCHED  <= 1;
        end
    endtask

    // Task to handle internal triggers
    task handle_internal_trigger;
        input [3:0] trig_id;
        begin
            NEXT_ID <= trig_id;
            NEXT_ON <= 1;
            if (trig_id == 4'b0000) // IRQ
                IRQ <= 1;
            if (trig_id == 4'b1000) // Software triggered RESET
                handle_reset();
        end
    endtask

    // Asynchronous Reset Handling
    always @(posedge CLK or negedge RST) begin
        if (!RST) begin
            // Enter RESET MODE
            handle_reset();
        end else begin
            // Sync RESET
            RST_SYNC1 <= 1;
            RST_SYNC2 <= RST_SYNC1;

            // Reset release and normal operations
            if (RST_SYNC2 == 1) begin
                if (RESET_ON == 1) begin
                    // Stop RESET MODE
                    NEXT_ID     <= 8;
                    NEXT_ON     <= 1;
                    RESET_ON    <= 0;
                end else begin
                    // Acknowledge the current interrupt
                    if (ACK) begin
                        handle_ack();
                    end else if (!NEXT_ON) begin
                        // Handle External Interrupts
                        if (INT != 3'b000) begin
                            handle_external_interrupt(INT);
                        end
                        // Handle Internal Trigger
                        else if (TRIG_ON) begin
                            handle_internal_trigger(TRIG_ID);
                        end
                    end
                end
            end
        end
    end

    /*
     * Interrupts: Whenever an INT[2:0] pin changes, it means a new interrupt is being set. We clear the DISPATCHED flag.
     */
    always @(INT) begin
        DISPATCHED  <= 0;
    end

endmodule