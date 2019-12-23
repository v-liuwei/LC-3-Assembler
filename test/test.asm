.ORIG -32768
;hello
AND r1,r2,-16
LDR R1,r7,31
ddd brnp label
LD r1,label
.BLKW 6
.FILL -32768
TRAp x21
.BLKW 0
.STRINGZ "\0\a\b\f\n\r\t\v\\\'\"\?\x01\023\a\a\x23"
GETC
OUT
PUTS
IN
label PUTSP
.BLKW x8
HALT
.END