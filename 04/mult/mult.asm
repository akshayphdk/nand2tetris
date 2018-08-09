// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// assign contents of RAM[0] to variable var1
@R0
D=M
@var1
M=D

// assign contents of RAM[1] to variable var2
@R1
D=M
@var2
M=D

// initialize contents of RAM[2] with 0
@R2
M=0

(REPEAT)

// check if value of var2 is 0, in which case end the loop
@var2
D=M
@END
D;JEQ

// decrement the value of var2 by 1
@var2
M=M-1

// add the value of var1 to RAM[2]
@var1
D=M
@R2
M=D+M

// jump back to start of loop where the condition will be evaluated
@REPEAT
0;JMP

(END)
@END
0;JMP
