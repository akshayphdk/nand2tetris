// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Check the contents of the Keyboard 
(START)
@KBD
D=M

// Skip to clearing the screen if Keyboard contents are 0
@SKIP
D;JEQ

// Paint all pixels black if Keyboard contents are non-zero
@SCREEN
D=A
@8192
D=D+A
(LOOP_BLACK)
AD=D-1
M=-1
@LOOP_BLACK
D;JGT

// Go to the end of infinite loop
@END
0;JMP

// Paint all pixels white if Keyboard contents are 0
(SKIP)
@SCREEN
D=A
@8192
D=D+A
(LOOP_WHITE)
AD=D-1
M=0
@LOOP_WHITE
D;JGT

// Unconditional jump to start, creating an infinite loop
(END)
@START
0;JMP
