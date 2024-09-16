from pwn import *
from Crypto.Util.number import long_to_bytes

c = remote("challenges.france-cybersecurity-challenge.fr", 2151)
c.recvuntil(b"Public key:\n")

p_ = c.recvline().decode()
p = int(p_.split()[2])

g_ = c.recvline().decode()
g = int(g_.split()[2])

y_ = c.recvline().decode()
y = int(y_.split()[2])

r = g*y % p
s = (-r) % (p-1)
m = (-r) % (p-1)

c.recvuntil(b"Input a message.\n")
c.recvuntil(b">>> ")
c.sendline(str(m))
c.recvuntil(b"Input a signature. First, input r.\n")
c.recvuntil(b">>> ")
c.sendline(str(r))
c.recvuntil(b"Now, input s.\n")
c.recvuntil(b">>> ")
c.sendline(str(s))
c.recvline()
