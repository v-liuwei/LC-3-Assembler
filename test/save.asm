.ORIG x-3000
;hello
AND r1,r2 -16
LDR R1,r7,31
ddd brnp label
LD r1,label
.BLKW x3
.BLKW 6
TRAp x21
.BLKW 0
.STRINGZ "hello"
GETC
OUT
PUTS
IN
label PUTSP
HALT
.END
