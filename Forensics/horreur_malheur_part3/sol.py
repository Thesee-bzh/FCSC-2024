from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
import zlib

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
