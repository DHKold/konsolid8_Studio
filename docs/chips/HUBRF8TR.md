
Interrupt that need a nibble (4b): [9]
- S 0001 RRRR   PUSH <R>            Push register R on stack                POP:0   PUSH:1
- S 0010 RRRR   POP <R>             Pop register R from stack               POP:1   PUSH:0
- S 0011 RRRR   PEEK <R>            Peek register R from stack              POP:0   PUSH:0
- S 0100 RRRR   REFRESH <R>         Refresh register R from memory          POP:0   PUSH:0
- S 0110 RRRR   LINK <R>            Link register R to memory               POP:2   PUSH:0
- S 0101 nnnn   DROP <n>            Decrease SP by n (0-15)                 POP:n   PUSH:0
- S 0111 vvvv   INT <v>             Trigger Interrupt v                     POP:0   PUSH:3
- S 1000 FFFv   SETF <F>, <v>       Set Flag F to v                         POP:0   PUSH:0
- S 1001 FFFv   JIF <F>, <v>        Jump if flag F is v                     POP:0   PUSH:0

ALU (Arithmetic): [8]
- S 1010        ADD                 Signed sum 2 bytes                      POP:2   PUSH:1
- L 1110 0001   SUB                 Signed sub 2 bytes                      POP:2   PUSH:1
- S 1011        INC                 Increment 1 byte                        POP:1   PUSH:1
- L 1110 0010   DEC                 Decrement 1 byte                        POP:1   PUSH:1
- L 1110 0011   NEG                 Negate (2-complement) 1 byte            POP:1   PUSH:1
- L 1110 0100   CMP                 Compare 2 bytes                         POP:2   PUSH:0
- L 1110 0101   ASL                 Arithmetic Shift Left 1 byte            POP:1   PUSH:1
- L 1110 0110   ASR                 Arithmetic Shift Right 1 byte           POP:1   PUSH:1

ALU (Logic): [8]
- S 1100        AND                 Logical AND 2 bytes                     POP:2   PUSH:1
- L 1110 0111   OR                  Logical OR 2 bytes                      POP:2   PUSH:1
- S 1101        NOT                 Logical NOT 1 bytes                     POP:1   PUSH:1
- L 1110 1000   XOR                 Logical XOR 2 bytes                     POP:2   PUSH:1
- L 1110 1001   SHL                 Bit Shift Left 1 byte                   POP:1   PUSH:1
- L 1110 1010   SHR                 Bit Shift Right 1 byte                  POP:1   PUSH:1
- L 1110 1011   ROL                 Bit Rol (with Carry) Left 1 byte        POP:1   PUSH:1
- L 1110 1100   ROR                 Bit Rol (with Carry) Right 1 byte       POP:1   PUSH:1

FLOW: [9]
- S 0000        NOP                 Does nothing for one cycle              POP:0   PUSH:0
- L 1110 1101   WAIT                Wait for interrupt                      POP:0   PUSH:0
- L 1110 1110   HALT                Wait for RESET                          POP:0   PUSH:0
- L 1110 1111   CALL                Jump to function                        POP:2   PUSH:3
- L 1111 0001   RET                 Return from function/interrupt/FRM      POP:3   PUSH:0
- L 1111 0010   JUMP                Jump to address                         POP:2   PUSH:0
- L 1111 0011   LOOP                Loop to address with counter            POP:3   PUSH:0-3
- L 1111 0100   REPEAT              Repeat next instruction                 POP:1   PUSH:0
- L 1111 0101   MASK                Set the Interrupt Mask                  POP:2   PUSH:0

FRM: [4]
- L 1111 0110   CACHE0              Fill FRM0 32B from memory               POP:2   PUSH:0
- L 1111 0111   CACHE1              Fill FRM1 32B from memory               POP:2   PUSH:0
- L 1111 1000   RUN0                RUN FRM0                                POP:0   PUSH:3
- L 1111 1001   RUN1                RUN FRM1                                POP:0   PUSH:3

STACK: [6]
- L 1111 1010   DUP                 Duplicate top byte                      POP:0   PUSH:1
- L 1111 1011   SWAP                Swap two top bytes                      POP:2   PUSH:2
- L 1111 1100   PUSH <v>            Push a direct byte to stack             POP:0   PUSH:1
- L 1111 1101   PUSH $A             Push a byte from memory to stack        POP:0   PUSH:1
- L 1111 1110   POP $A              Pop a byte from stack to memory         POP:1   PUSH:0
- L 1111 1111   PEEK $A             Peek a byte from stack to memory        POP:0   PUSH:0

DMA: [1]
- L 1110 0000   COPY                Set the DMA Transfer Src/Dst/Len/0      POP:5   PUSH:0
- L 1111 0000   COPYJ               Set the DLA Transfer Src/Dst/Len/Jmp    
