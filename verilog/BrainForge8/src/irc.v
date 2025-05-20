/**
 * List of Interrupts:
 *   - 00XX     External INT 0-3
 *   - 0100     DMA Completion
 *   - 0101     DMA Exception
 *   - 0110     Stack Overflow
 *   - 0111     Stack Underflow
 *   - 1000     Reset
 *   - 1001     Software Reserved
 *   - 1010     Software Reserved
 *   - 1011     Software Reserved
 *   - 1100     Software Reserved
 *   - 1101     Software Reserved
 *   - 1110     Software Reserved
 *   - 1111     IRQ
 */
module IRC #(
    parameter INT_ID_EXT0   = 4'b0000,
    parameter INT_ID_EXT1   = 4'b0001,
    parameter INT_ID_EXT2   = 4'b0010,
    parameter INT_ID_EXT3   = 4'b0011,
    parameter INT_ID_DMAD   = 4'b0100,
    parameter INT_ID_DMAF   = 4'b0101,
    parameter INT_ID_STOF   = 4'b0110,
    parameter INT_ID_STUF   = 4'b0111,
    parameter INT_ID_RSTB   = 4'b1000,
    parameter INT_ID_SFT0   = 4'b1001,
    parameter INT_ID_SFT1   = 4'b1010,
    parameter INT_ID_SFT2   = 4'b1011,
    parameter INT_ID_SFT3   = 4'b1100,
    parameter INT_ID_SFT4   = 4'b1101,
    parameter INT_ID_SFT5   = 4'b1110,
    parameter INT_ID_IRQ0   = 4'b1111
) (
    // TIMING INTERFACE
    input   wire                CLK,        // System clock

    // INTERRUPTS INTERFACE
    input   wire    [3:0]       INT,        // Interruption Indicator
    input   wire                RST,        // Reset Interrupt
    output  reg                 IRQ,        // Interrupt Request

    // EXPOSED INTERFACE
    output  reg     [3:0]       NEXT_ID,    // Next Interrupt Identifier (0-15)
    output  reg                 NEXT_ON,    // Next Interrupt Active
    output  reg                 RESET_ON,   // Reset ongoing
    input   wire                ACK,        // Acknowledge Interrupt

    // INTERNAL TRIGGER
    input   wire                TRIG_DMAD,  // Trigger DMA Done Interrupt
    input   wire                TRIG_DMAF,  // Trigger DMA Fail Interrupt
    input   wire                TRIG_STOF,  // Trigger Stack Overflow Interrupt
    input   wire                TRIG_STUF,  // Trigger Stack Underflow Interrupt
    input   wire                TRIG_RSTB,  // Trigger Reset
    input   wire                TRIG_IRQ0   // Trigger IRQ0
);

    reg RST_SYNC1, RST_SYNC2;

    // Task to handle reset logic
    task handle_reset;
        begin
            NEXT_ID     <= 0;
            NEXT_ON     <= 0;
            RESET_ON    <= 1;
            IRQ         <= 0;
            RST_SYNC1   <= 0;
            RST_SYNC2   <= 0;
        end
    endtask

    // Task to handle interrupt acknowledgment
    task handle_ack;
        begin
            NEXT_ID <= 0;
            NEXT_ON <= 0;
            IRQ     <= 0;
        end
    endtask

    // Task to handle triggers
    task handle_trigger;
        input [3:0] trig_id;
        begin
            // Can only interrupt if no other interrupt is ongoing
            if (!NEXT_ON && !RESET_ON) begin
                NEXT_ID <= trig_id;
                NEXT_ON <= 1;
                if (trig_id == INT_ID_IRQ0)
                    IRQ <= 1;
            end
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

            // Stop RESET MODE
            if (RST_SYNC2 == 1 && RESET_ON == 1) begin
                NEXT_ID     <= INT_ID_RSTB;
                NEXT_ON     <= 1;
                RESET_ON    <= 0;
            end
        end
    end

    always @(posedge ACK) begin
        handle_ack();
    end

    always @(posedge INT[0], posedge INT[1], posedge INT[2], posedge INT[3]) begin
        casez (INT)
            4'b???1 : handle_trigger(INT_ID_EXT0);
            4'b??10 : handle_trigger(INT_ID_EXT1);
            4'b?100 : handle_trigger(INT_ID_EXT2);
            4'b1000 : handle_trigger(INT_ID_EXT3);
        endcase
    end

    always @(posedge TRIG_DMAD) begin
        handle_trigger(INT_ID_DMAD);
    end

    always @(posedge TRIG_DMAF) begin
        handle_trigger(INT_ID_DMAF);
    end

    always @(posedge TRIG_STOF) begin
        handle_trigger(INT_ID_STOF);
    end

    always @(posedge TRIG_STUF) begin
        handle_trigger(INT_ID_STUF);
    end

    always @(posedge TRIG_RSTB) begin
        handle_reset();
    end

    always @(posedge TRIG_IRQ0) begin
        handle_trigger(INT_ID_IRQ0);
    end

endmodule