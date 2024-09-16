# Horreur, malheur 1/5 - Archive chiffrée

## Challenge
Introduction commune à la série Horreur, malheur

Vous venez d'être embauché en tant que Responsable de la Sécurité des Systèmes d'Information (RSSI) d'une entreprise stratégique.

En arrivant à votre bureau le premier jour, vous vous rendez compte que votre prédécesseur vous a laissé une clé USB avec une note dessus : VPN compromis (intégrité). Version 22.3R1 b1647.

Note : La première partie (Archive chiffrée) débloque les autres parties, à l'exception de la seconde partie (Accès initial) qui peut être traitée indépendamment. Nous vous recommandons de traiter les parties dans l'ordre.

Sur la clé USB, vous trouvez deux fichiers : une archive chiffrée et les journaux de l'équipement. Vous commencez par lister le contenu de l'archive, dont vous ne connaissez pas le mot de passe. Vous gardez en tête un article que vous avez lu : il paraît que les paquets installés sur l'équipement ne sont pas à jour...

> Le flag est le mot de passe de l'archive.

> Remarque : Le mot de passe est long et aléatoire, inutile de chercher à le bruteforcer.

## Inputs
- encrypted archive [archive.encrypted](./archive.encrypted)

## Encrypted archive
The archive is protected by a password, but we can list the files:
```console
$ unzip archive.encrypted
Archive:  archive.encrypted
[archive.encrypted] tmp/temp-scanner-archive-20240315-065846.tgz password:
   skipping: tmp/temp-scanner-archive-20240315-065846.tgz  incorrect password
   skipping: home/VERSION            incorrect password
   skipping: data/flag.txt           incorrect password
```

Looking at the archive in more details, we see that the `ZipCrypto` library is used:
```console
$ 7z l -slt archive.encrypted
7-Zip [64] 16.02 : Copyright (c) 1999-2016 Igor Pavlov : 2016-05-21
p7zip Version 16.02 (locale=en_US.UTF-8,Utf16=on,HugeFiles=on,64 bits,2 CPUs Intel(R) Core(TM) i5-4210M CPU @ 2.60GHz (306C3),ASM,AES-NI)

Scanning the drive for archives:
1 file, 65470 bytes (64 KiB)

Listing archive: archive.encrypted

--
Path = archive.encrypted
Type = zip
Physical Size = 65470

----------
Path = tmp/temp-scanner-archive-20240315-065846.tgz
Folder = -
Size = 64697
Packed Size = 64714
Modified = 2024-03-15 15:58:46
Created =
Accessed =
Attributes = _ -rw-r--r--
Encrypted = +
Comment =
CRC = 126407B2
Method = ZipCrypto Deflate
Host OS = Unix
Version = 20
Volume Index = 0

Path = home/VERSION
Folder = -
Size = 194
Packed Size = 120
Modified = 2022-12-05 17:06:09
Created =
Accessed =
Attributes = _ -rwxr-xr-x
Encrypted = +
Comment =
CRC = 6C3A35F8
Method = ZipCrypto Deflate
Host OS = Unix
Version = 20
Volume Index = 0

Path = data/flag.txt
Folder = -
Size = 33
Packed Size = 44
Modified = 2024-03-15 15:32:38
Created =
Accessed =
Attributes = _ -rw-r--r--
Encrypted = +
Comment =
CRC = 07FF9365
Method = ZipCrypto Deflate
Host OS = Unix
Version = 20
Volume Index = 0
```

So three files:
- tmp/temp-scanner-archive-20240315-065846.tgz: size=64697, crc=0x126407B2
- home/VERSION: size=194, crc=0x6C3A35F8
- data/flag.txt: size=33, crc=0x07FF9365

There’s a known plaintext attack against libray `ZipCrypto`, explained here: https://medium.com/@whickey000/how-i-cracked-conti-ransomware-groups-leaked-source-code-zip-file-e15d54663a8

And since the challenge mentions that some modules are not up to date, we can assume that `ZipCrypto` is not up to date and that we're on the good track.

## Version of Ivanti Connect Secure
To exploit the `ZipCrypto` libray, we need some known plaintext at the beginning of one the files in the archive. The file that sticks out is `home/VERSION`.

Googling around about the `Ivanti Connect Secure` VPN issue (see part2), we found this detailed paper from `Synacktiv`: https://www.synacktiv.com/sites/default/files/2024-01/synacktiv-pulseconnectsecure-multiple-vulnerabilities.pdf

In this paper, we found an example of that exact file `home/VERSION`, which gives us the exact format, but maybe not the exact version we want.

Talking about version, the challenge mentions a note on the `USB stick`: it refers to the compromised VPN and mentions a version number: `22.3R1 b1647`.

Finally, after Googling around a little further, I came to the exact `VERSION` file corresponding to that version here: https://www.assetnote.io/resources/research/high-signal-detection-and-exploitation-of-ivantis-pulse-connect-secure-auth-bypass-rce

So this should be the file `VERSION`:
```console
$ cat VERSION
export DSREL_MAJOR=22
export DSREL_MINOR=3
export DSREL_MAINT=1
export DSREL_DATAVER=4802
export DSREL_PRODUCT=ssl-vpn
export DSREL_DEPS=ive
export DSREL_BUILDNUM=1647
export DSREL_COMMENT="R1"

```

We can make sure it has the exact same length as the original one (length=194 in the encrypted archive):
```console
$ wc -c VERSION
194 VERSION
```

To make sure it is exactly the same file, we can check it's crc (crc=0x6C3A35F8 in the encrypted archive):
```python
$ python3
>>> import binascii
>>> with open('VERSION', 'rb') as f:
...     data = f.read()
...     print(hex(binascii.crc32(data) & 0xFFFFFFFF))
...
0x6c3a35f8
```

Everything is set: we have recovered the plaintext for file `home/VERSION` in the `encrypted archive`; We're ready to exploit the `ZipCrypto` vulnerability.

## Plaintext attack against ZipCrypto
We can follow the steps from https://medium.com/@whickey000/how-i-cracked-conti-ransomware-groups-leaked-source-code-zip-file-e15d54663a8

0xdf also explains it for the `RANSOM` box from `HackTheBox` at https://0xdf.gitlab.io/2022/03/15/htb-ransom.html

We first `zip` our file `VERSION`, which is the plaintext for file `home/VERSION` in the encrypted archive `archive.encrypted` and launch the attack:
```console
$ zip plain.zip VERSION
  adding: VERSION (deflated 44%)

$ ./bkcrack -C archive.encrypted -c home/VERSION -P plain.zip -p VERSION
bkcrack 1.6.1 - 2024-01-22
[13:42:25] Z reduction using 101 bytes of known plaintext
100.0 % (101 / 101)
[13:42:26] Attack on 83134 Z values at index 6
Keys: 6ed5a98a a1bb2e0e c9172a2f
67.6 % (56195 / 83134)
Found a solution. Stopping.
You may resume the attack with the option: --continue-attack 56195
[13:45:42] Keys
6ed5a98a a1bb2e0e c9172a2f
```

We recovered the keys that allow us to craft another `encrypted archive`, protected with the passord we want (here `pass`):
```console
$ ./bkcrack -C archive.encrypted -k 6ed5a98a a1bb2e0e c9172a2f -U archive.encrypted.pass.zip pass
bkcrack 1.6.1 - 2024-01-22
[13:48:35] Writing unlocked archive archive.encrypted.pass.zip with password "pass"
100.0 % (3 / 3)
Wrote unlocked archive.
```

Finally we can `unzip` the newly crafted `encrypted archive` with the password we just set (`pass`):
```console
$ unzip archive.encrypted.pass.zip
Archive:  archive.encrypted.pass.zip
[archive.encrypted.pass.zip] tmp/temp-scanner-archive-20240315-065846.tgz password:
  inflating: tmp/temp-scanner-archive-20240315-065846.tgz
  inflating: home/VERSION
  inflating: data/flag.txt

$ cat data/flag.txt
50c53be3eece1dd551bebffe0dd5535c
```

We've successfully unzipped the `encrypted archive` and recovered the flag!

## Flag
> FCSC{50c53be3eece1dd551bebffe0dd5535c}
