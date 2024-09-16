# Silence

## Challenge
Vous êtes Bob. Une vieille amie vous avait envoyé un flag pour un FCSC futur, il y a quelques années, avant que vous ne perdiez contact. Elle se rappelle à vous en indiquant qu'elle fait maintenant partie de l'organisation du FCSC. Elle a pu mettre en place ce flag et vous propose de le jouer.

Problème, le flag est resté dans une sauvegarde de SMS de votre application SMS de l'époque, Silence. Vous avez complètement oublié le code que vous utilisiez, vous savez seulement qu'il s'agissait d'un code à 5 chiffres décimaux.

Saurez-vous retrouver ce flag et montrer à Alice que vous ne l'aviez pas oubliée ?

Toute ressemblance avec des faits et des personnages existants ou ayant existé serait purement fortuite et ne pourrait être que le fruit d’une pure coïncidence.

Aucune IA n'a été maltraitée durant la réalisation de ce challenge.

## Inputs
- Zip archive of the SMS application: [SilenceExport.zip](./SilenceExport.zip)

## Zip archive contents
Here the contents of this archive:

```console
$ tree SilenceExport
SilenceExport
├── cache
├── code_cache
├── databases
│   ├── canonical_address.db
│   ├── canonical_address.db-journal
│   ├── _jobqueue-SilenceJobs
│   ├── _jobqueue-SilenceJobs-journal
│   ├── messages.db
│   └── messages.db-journal
├── files
│   └── sessions-v2
│       └── 3
└── shared_prefs
    ├── org.smssecure.smssecure_preferences.xml
    ├── SecureSMS-Preferences.xml
    └── SecureSMS.xml

6 directories, 10 files
```

The `messages.db` sticks out. Let's look at it first.

## Dump messages database: messages.db
This is a `SQLite` database:

```console
$ file databases/messages.db
databases/messages.db: SQLite 3.x database, user version 30, last written using SQLite version 3037002, file counter 1, database pages 38, cookie 0x1b, schema 4, UTF-8, version-valid-for 1
```

We can dump it using `sqlite3`, list its `tables`, focus on the one called `sms` and dump its `schema` to get the `column names`:

```console
$ sqlite3 databases/messages.db
sqlite> .tables
android_metadata       mms                    recipient_preferences
drafts                 mms_addresses          sms
identities             part                   thread
sqlite> .schema sms
CREATE TABLE sms (_id integer PRIMARY KEY, thread_id INTEGER, address TEXT, address_device_id INTEGER DEFAULT 1, person INTEGER, date INTEGER, date_sent INTEGER, protocol INTEGER, read INTEGER DEFAULT 0, status INTEGER DEFAULT -1,type INTEGER, reply_path_present INTEGER, date_delivery_received INTEGER DEFAULT 0,subject TEXT, body TEXT, mismatched_identities TEXT DEFAULT NULL, service_center TEXT, subscription_id INTEGER DEFAULT -1, notified DEFAULT 0);
CREATE INDEX sms_thread_id_index ON sms (thread_id);
CREATE INDEX sms_read_index ON sms (read);
CREATE INDEX sms_read_and_notified_and_thread_id_index ON sms(read,notified,thread_id);
CREATE INDEX sms_type_index ON sms (type);
CREATE INDEX sms_date_sent_index ON sms (date_sent);
CREATE INDEX sms_thread_date_index ON sms (thread_id, date);
```

Now we know what each column mean and we can dump the fields. And indeed we get many messages with the caller number, some epoch timestamps, but of course the content of the messages are encrypted:

```console
sqlite> select * from sms;
1|1|+33742241337|1||1567604544675|1567604545000|0|1|-1|-2147442668|0|0||YkrskuTJIo9/s7VARk9qbWGe9EkUTr3tEIL3tzJyNobzTCuoyfB5qrmDIcVsR5m/WUXwk4bJp+f6iBq5rvKBUhaRB8RJuHJN5tSoNXOS0OejWnXlDnRYALvrjCpXygoemzcGXlGl+axIwJ2vVzVk0MdcStFEXHkiLtVQgbbJyRabImR7ssxm2CqYHld0Mr01HElwv1cY8RR7Qsynhgugvioqh4LD0MIG+StS8Ru6Ckos9UFHIAtzpH5zfcqaxQpNJnUfNUCK3NccRv+YOq1EedRpdvmwWNsE4u4XRugI3Z5ftQoS3P0dItLJzge9eM65sxBsNz4IMwmGR6o8p7kS/Ssbt6dYUAys0JYpuiikkzu6aHVm|||1|0
2|1|+33742241337|1||1567604568231|1567604568231||1|-1|-2147450793||0||LMA3qQb63vS96YZBJ0fMr1MM8rjKwSrianfR6sI7t3ygQYMHzKQ82vpdJ3afxW2Z3sesnsvsHjIL6OUZ2fe1I5FqysyHI79zRi/yHe7FLkjtEjuZF/Eut89YK4HAFgjk3/CkdHtcuYYhCUUHJgNP8qqhJCFfVEKs/o9S8v6Uk0zzjrP+4UYLtDLSnxz+a/EHrl0Gm8E5ZRlD3JwwXt+/IQHsWFiQH++KUhQ0rerlAaNF8XSHl20KMKs6b+KUICI8hsO4NBpFIHvmoOhTAzMnYK64eqePxnO63d+nHZzCW17CFFSZfQNaVT6VgmLEvuyQ2irsdU4lwXpPuJeN3JQqBMTcyYicNAG9kKzWguyhtkzJL8q0|||-1|0
3|1|+33742241337|1||1567604572231|1567604571047||1|-1|-2139095020||0||lxaeejRGQzoFYJVIcUb7utDNC2JFChynet82vbTH4FcZPhRnejoa3LAHYOHLvEPma+Y88w==|||1|0
4|1|+33742241337|1||1567604577918|1567604577918|0|1|-1|-2139094953|0|0||+l1D5vJTfyGJ+Q4X0XxlbIRd1l1VG6vP9jWqGWthXIQSzns73npNYEo+PRdEboDZBcs0Ng==|||-1|0
5|1|+33742241337|1||1568032464724|1568032463648||1|-1|-2139095020||0||sJrd34xJDbLQ0wC+8k6ZxAUjWY8RndFwuSUtQF6Gbg7uoBlr5y6lz3S7RzzX+k5ssHCAqF/3xDSCE4KdG6Rlu679WgU=|||1|0
6|1|+33742241337|1||1568035092367|1568035092367|0|1|-1|-2139094953|0|0||s1ob2pIV6eaCvGgfsE9eix7LAt8Jkr34/LfHoUDFFBdZzz7EvtUqVzjd+l5uR1hFovr570p9GOc2scrSqOlRDwni2wFm+8b11lw1XuF1Zcrnncr4|||-1|0
7|1|+33742241337|1||1568036125335|1568036125205||1|-1|-2139095020||0||v2VmmLg10lFnNFrmr1S4DZVFGp/tOaCSFynB5LtmF9WtMKJrUlR7r5pPqXIfO8qiIPBVer3jsUOPtT6uUlj09UpQ/idpCTJkHhKRbNn9qVdkB/Zq|||1|0
8|1|+33742241337|1||1568036706675|1568036706675|0|1|-1|-2139094953|0|0||u4zRR96wt9G3i1U/al3iFHBhup/2lvXSdyw2tZD4ZP5qrl/HDOOUxgZGSIxstCwTsa1KMF69GbsHOBd/nR7TI85bHF9sDUrQUD7/r/BMfwyBg63JFszt4AmSvwiBBnqCIO5q3A==|||-1|0
9|1|+33742241337|1||1568038095599|1568038095353||1|-1|-2139095020||0||dt2TO55tEJWD3PoS7aj7iu616DsUc1RPWSKL1svEtTY49FcLIENY35yJGoqgVzsocg2d4YtuFIxI6lIAVWRqMMqRzVA5O2rpS1iV+shfjSNgRU27lRj4EhvQSikCiTXYClDm461z1s3WeSucG4dZR5cIpl4=|||1|0
10|1|+33742241337|1||1568039899827|1568039899827|0|1|-1|-2139094953|0|0||aAW16N1XHWx2Gfo5s5E4an3s8EW1R9Rk5JrwshzTP9b1ugOZZ9l0NrekeowXA4s/j4YaFWUgC3NYmFKDOqyZR10zewY=|||-1|0
11|1|+33742241337|1||1568039928661|1568039928046||1|-1|-2139095020||0||IXEnbDbt6AJfWGZBVfF08dSnAWqe2zQGvQj8R04cG0ALc+sVDONzEVKYm6XdMNXmKE8UvNsVSrgSifT8Zl2laRzTfizlGB+6wMAXhpD4kxIVVmViyVORNBfwbS4WsRcmWyHhaQ==|||1|0
12|1|+33742241337|1||1568040352468|1568040352468|0|1|-1|-2139094953|0|0||cpjAbO/yKMs43qBj11YQWnyCJt7HGa5filQ33cS86i3m/5RYooXvX88FW6Qy1oE9RvtxLCQffywyHAKHX1eKaI52J6F7H7tT2blmM4sJavj1J1lb6hLFW+KAcdGlLKaycf8pPQ==|||-1|0
13|1|+33742241337|1||1568040622978|1568040622823||1|-1|-2139095020||0||kIMXgMuYiqtVoXLOv/+wkAAuttbkiu5DN/ZbGUQk8dOPH7HymctW7UH6WGETOrlm9X7L3SKxSeZgpzWS/Aicvld9/bw=|||1|0
14|1|+33742241337|1||1568876487384|1568876487384|0|1|-1|-2139094953|0|0||c/YrMmTs+h+Xx4QrOcY9WmUc323f/o69jkQ5b3wql7ZOPYFOipTT2hx8r4gRHA2ycdKLOQeEikiVn5Cvrbj63kBMk8m/eEHGPRXjJqsEvYT4ob5f|||-1|0
15|1|+33742241337|1||1568876979062|1568876979025||1|-1|-2139095020||0||z2xbauY32w4png2BgHoSTgXHEFFtET2EiRtiGRphGm6YcEsPaI51KqHPA8ALvlxqbRmUuCI/oFyDYJdm4oKoM53uA+k=|||1|0
16|1|+33742241337|1||1568877488657|1568877488657|0|1|-1|-2139094953|0|0||QTkiNewHp6JpzWOxl5HvaDXc+Z29+vVTNz7NPe/AJ+6r5nLecvujdKvWlqpCywEFQeHP6tDqvGk3c0R4wVDhzhqXPK3q2P4kx8Rq22OvZu7Knu9/|||-1|0
17|1|+33742241337|1||1568877994921|1568877994082||1|-1|-2139095020||0||JA/upunPe5P5CPU9994S8eu039OC/32NotNClTtZEdBOoCts+t6MxGcr0tdzEaJyEuax3r13t2FBo6OSH47wwwWujJ4p3iWHdvsNFDCPbqHdGWKknVL5pN10hGw1O4FESRMfTg==|||1|0
18|1|+33742241337|1||1568878876106|1568878876106|0|1|-1|-2139094953|0|0||vgLQOZZuh6ZRKI6Y7zxFMZMSdQyZ2xxE5j+e9EKGz9pVvmrG7ZBmLh10qFbjyOs9TPL6oSPVfIKMVIZpoyKwBToAnRDd5Ryo7Qc/B0FY70gnyN8QD0TKuN+vSszEHmZj8fXO3O2ZAVeDnjtwrmvNm9ZtO3+2uZkqX7c9Tq9vdUqoY3uR|||-1|0
19|1|+33742241337|1||1568879433580|1568879433300||1|-1|-2139095020||0||xfkj1x6VDR/glsyWwMalYY3rnSVOHxaeu7YbnrcjBuHQJfB7ABxz9Qc/pvtnQanoK0xgr4TQAiZYzcbr2MyZH83TDrM=|||1|0
20|1|+33742241337|1||1571301916554|1571301916448||1|-1|-2139095020||0||/BteKBnQJFzjRP7tV+aZqp7Y4+QFzWeQfrCchBL10zX6Sm7I4o0uwdXwxPH3B5ZWMNJ9/zcUR2KD5K+GSigz1rgShInoLitGd1jf6WRhPz5iJVv9MLQqRbR1NX4pGozU+lP7Eg==|||1|0
21|1|+33742241337|1||1571302603369|1571302603369|0|1|-1|-2139094953|0|0||NQwcTJx0NDhKgbJOre6fn8VCTsLplEwvEAZlYjeaw6aK3JL/zaRetMnuSqJ50cWsa6ZCRv9vNQv2upbW2fXdir/ycKLf8yZZmVYgKo+kv56ddGi5|||-1|0
22|1|+33742241337|1||1571304333059|1571304332634||1|-1|-2139095020||0||8IIIxO7ZYsMw43aTFnqObcWNQBuSa83K4vRsG2R8a8ox8+aYn7W5KiIN3wMS3OOXX+EAy9VFEEt3NqOmyWDUGT2PwEdJ73+qbPqGuCCV3It1dCuvvI85bVAn7JcYUBBPT+PrDI2/BMa9b4rMf+eebeo/gdtDP0yglyTKX02lQcc6SrdK31RV365/fwp+aehHeWrDNqyCKgfLADUovEfRo6zjTG4mlNEQvYQN6Tsqx4D1la3r|||1|0
23|1|+33742241337|1||1571305047261|1571305047261|0|1|-1|-2139094953|0|0||y/79J/6iU2aozgJSo1LyTlsMzYeq0r3kk1THlaw7aFgI0xZDKLFTaTD8eAasZmkaSFopdF/jtSoLYs5K3i+SNGSl4mBQyv5Sk2d2qIjD3ztpXc7CWhRdvfrIM2D3e3W30AReKA==|||-1|0
24|1|+33742241337|1||1571305186060|1571305185410||1|-1|-2139095020||0||8S7RmXNyCDNKGED0BcmMJILI4TQ7EjMHkNyfiwO5tLhZkn/you4x0e8bmphHh/G5prKIlyok6LDrFYLdcZh5UrBa7nGetxY2TjjCYojaciEZDcLy1CEE4IpAdzmeSVMGxwDjng==|||1|0
25|1|+33742241337|1||1571305684769|1571305684769|0|1|-1|-2139094953|0|0||M9FlZF75whdeRZ+sr/MjZpUOCWtfpcxYrVrpa9L6NU7te748Mz5ghgKGJXgx2VriAZSac/dbmqR12SzgZkI7ggXQoyg=|||-1|0
26|1|+33742241337|1||1572539943471|1572539943019||1|-1|-2139095020||0||9f2gKyItaIp91ave2n9pTmaMKxfLlPEg1teNDP9JUckJhBJjdqyOCwwogz1eGpmXRB4aIPYzlI/iRFCPd2HD+Qi+8Pc=|||1|0
27|1|+33742241337|1||1572541399167|1572541399167|0|1|-1|-2139094953|0|0||ftR5f3fsVUUa915TC9wTM9pw/sRTlC83qZHV8rv4KsIPxggV1iQkKBcrY9mSeNwmF/oXjizUBQ2e+0Hi5jS77ebtjOYjnDFEhstWc8iNd/LbXsud|||-1|0
28|1|+33742241337|1||1572543377540|1572543377227||1|-1|-2139095020||0||ADqvC5mHzzoNIydw2u1t/HhMo45h+VvKk3Su0F69wWEhLjJXke40GTZvf02KWEOpYGbKBqGxMLPEG5MWA3PP8LrgkL61CzGbq3N3FaX20+RLdoBs|||1|0
29|1|+33742241337|1||1572544419803|1572544419803|0|1|-1|-2139094953|0|0||lr+VEvKJ4vPDYm6zk+G3zM88yDs5iCvqaLyFVtA7hArt1BxwcX2Tm5ewNbHJI1ZKsqP8d1fHWtoe6OzGP3Zy8xDGGd24RBB57KLDdnlp/yFipcpis234gifKqGByV4LzMBCo0Q==|||-1|0
30|1|+33742241337|1||1572546103659|1572546102730||1|-1|-2139095020||0||V/eGMrpIcqcAqSNLBdEG8w/cn1biq39Z1vF9CHUL2TYUnxRffBiMNtKriXK+OWhWf6UtlttTCn4ZeyDxEmogXS4PZW1v2xtR4XtTJ+M3WHDrgZuYRZeKH5Pmigx1DtpQFof9BA==|||1|0
31|1|+33742241337|1||1572547077259|1572547077259|0|1|-1|-2139094953|0|0||k1fhOtq2DyIx6K6amSq5iJs4Y2fU+yxK7F8FoXWv0TLaef/bWOHQFNuddWquy57qWZQXtBf9/1S5vBJl6Hai0N3hXqWI+BU8A1T5Pw5NQYiH1ZQriWZrwwdsfPYbts8ow8sDi70j9UxqN1gxc3wBXBb/bBk=|||-1|0
32|1|+33742241337|1||1572547102350|1572547101701||1|-1|-2139095020||0||ybpwU7RrHyvlAerUUPKaFD1z7CL70pYxgxAzq4zEcSDfExhitJBMo8G3xIrPu0bZ0IDdwUuKtYnCdALCERT+tLLI7x3OoRJmjyTSOuKtqTnGebFN|||1|0
33|1|+33742241337|1||1572547288747|1572547288747|0|1|-1|-2139094953|0|0||s9kaDYnJjaMKl3SfVzW3cfvUX9ZPL2+4uYUFz3LFaaybpEBGJneE6/Gr1OjUHHCTnMj4ZSohanKWn0kkZQl7JsdATYWH1i90YCvfGalMCUWrwHX5YEr6EQp5oKGAZz1/ZzRmW+J2hbT3o+cnjhV3p5tgcP0c5LVrHh3AiROgoqTIKKSndqyzukMD5x6Q1AcRSm2B7g==|||-1|0
34|1|+33742241337|1||1572547537971|1572547537729||1|-1|-2139095020||0||TaT3kGNwCw14LqoF+ppp/W52UtnKVaxYb7ZT+Uw5JGKQk9eVoAX4v7IMDPJa1iPNoeQnqfmebVfkvKl8qoDAPUgDCcIC/K4h2RkETD5NHZc8f8Fbm/3Occj2GhXZV7n8xjoJCw==|||1|0
35|1|+33742241337|1||1572547978638|1572547978638|0|1|-1|-2139094953|0|0||6pYIPmiSWYCwYXOOkGPu6ciXaSxY2f6Z1FC9aes+D/WWGvl0dPpxAvm1DpWswhiaG5L9YEd12Hw8gNX6SH7cas+XH6029pmahAU/lXEBcwH6zs1V|||-1|0
36|1|+33742241337|1||1572548006067|1572548005848||1|-1|-2139095020||0||J79sfU9OflLSf3mVYZyPAJNkWVKP52LASCYMedkxuUZH/CTp2O2gZpkhT8RDHbMYw9KrWqmtheP5/nqO5t0OPhePD68=|||1|0
37|1|+33742241337|1||1572548221350|1572548221350|0|1|-1|-2139094953|0|0||WXOFlEjroyQ/oGX6HykQ9MSumP+/Pan3AW2qcclnQ2KMFvWftBhFlFNl2DeDr6vuiznBzGpmieUtRLqCpnYsVVh/Y/A=|||-1|0
38|1|+33742241337|1||1572861115173|1572861114817||1|-1|-2139095020||0||qKfGiVrKj/kTQgQvK3xiSbAB6oxbWyPR+0qDcq2fDJQ7SwxEFkvUjStE6nnnhKyZue42BGdffNZHDac4Drc6JL0c00WRDpjcq/qrq3ZHiw/QT4Exh8zGICNhmnkxWcBggJojnSbnGOISO/Q5aZvUSyJCvKk=|||1|0
39|1|+33742241337|1||1572862600307|1572862600307|0|1|-1|-2139094953|0|0||wVPQnQW0X8lZumfZCLv190QEp2CPiGguUMV6mU3d0JnoQ0WjIBjkm8LzLUP6QvMt3d6kI879x77Qjm7ZuXhXccB6x4fvbCKByagCXa9bWex6xOyubGOUP+ZmqSqpsESqTo5ufg==|||-1|0
40|1|+33742241337|1||1572864223653|1572864223091||1|-1|-2139095020||0||53MzQGK49/6huu4TcQZ/xfZ9/HVJuQz4AvAabKSCralZuAdczz7e7moGo5L/HHX4RjNcKT/wnaXpPhrGisk3cT+tiK1zDv/jCoCmxQiZulaph6HnZ5HD5abeU2JQN42dxmqIERHqoykQ3s4LFPnmRejm+XgpAHxkf1t7TEu843Z1q8Gd|||1|0
41|1|+33742241337|1||1572864968615|1572864968615|0|1|-1|-2139094953|0|0||wBih3WhJ0yiPHsQnPkRAeeOmkKunnwFraur+N9dMyEjKBBCtICYhJtl0bdtzxWQHQmLRLChGBhioSr/HgZjqcR8PUGd8Wvmg2iMThYCK4biYGQcbLZJFyqkvXbq7WpFmYP3uYw==|||-1|0
42|1|+33742241337|1||1572866442378|1572866441344||1|-1|-2139095020||0||iosktxPznT9Ec7BSB0TQ6vrck0w/4boAsskRAESWT6t/kveYpMEeA1u2rNULo0Yc5b1gXUQclxKEmQhheQ1roaXGqZHLZY/zoRtu5Nc4lIkaXBSLzEjJYARePeK1nL6djRAsXlY2htZbBsPGhnjzDLY5Jtc=|||1|0
43|1|+33742241337|1||1572866547283|1572866547283|0|1|-1|-2139094953|0|0||Hzo+KD5gY1/hl4jn7HLpTLj5/BxpB3SuAusOPGeTTYRC3ftOlObgXapwAF6/F8Bk+EDbAYHj5F8AeXud1jo10jI1r3Q=|||-1|0
44|1|+33742241337|1||1573736498532|1573736498025||1|-1|-2139095020||0||ArdRDTiR/YyAWkZT9/oBunXGQAezGV1Wqv2Vu8/43hsIw4c3N0QqFwY7zbTuggNn+zSmpoxSCW4I7BQt5PW4AgxdAdlU14UlfpIbAV2TtP1DS+5r/zGxX3B+IX8PGyQREGehFA==|||1|0
45|1|+33742241337|1||1573739356079|1573739356079|0|1|-1|-2139094953|0|0||fBrnB8FKasyg2y+QzbDhOi+6TMDxjHqeODr6Kcd9you/PS2janBzf+WC7OiZcHnEy8UZ+xpmIYrBG0G3/kv+hElc69IXN3fyPmjZFY7JyVQEY/6B|||-1|0
46|1|+33742241337|1||1573740459559|1573740458551||1|-1|-2139095020||0||djxhg0YL+P8FN7ih8B9GmhT2kfJEDgn6YMSm1/1pFeu3JxMBUvNjLpO9Pmx1HLqgv4dx6PHlO3G0nlhTAEFSP+QzFDGLLz/NgBi0w4wiaz2gioPyOeFlMoyOKzcbV5DvV5upMA==|||1|0
47|1|+33742241337|1||1573742415122|1573742415122|0|1|-1|-2139094953|0|0||9WZ8HBflW+DvxABWwNiXFnXdwR/MERnJ/jD8ZpTvpva8vIiJf5vqoHh0mRDKMUQvPUZx49uvfzDBFAy3fuWLQWgbY+IlgSMBob/ucIGZSoE9q5iQtAiB1c6hdobCigjtiJi5canjmjM7V4SrbZS28SyUKTz1/2FiUElCrcGHVb6BYlDP|||-1|0
48|1|+33742241337|1||1573743536237|1573743535817||1|-1|-2139095020||0||VfU5+4ycHcNwrnGz4KYs4uM+4wq/I5MaIxbqwpFYIrQ5JaPqUpM0H48N8HaL93ekZU8q9A==|||1|0
49|1|+33742241337|1||1573744538482|1573744538482|0|1|-1|-2139094953|0|0||/e+emUH9btbW5/xkrc5ZPJz1/cxDRaupqrjwhJyN/GxJcxq2drJbmAsqjlY/zNpoE8hHiam1kCSsw3kHmUc+hqQB8IvEkbv/O72Qa102937EMIYfSTWLUi12M6xV4biWBiTvNihlyhZXF7fMO1u6h9ys0aw=|||-1|0
50|1|+33742241337|1||1573745410697|1573745410482||1|-1|-2139095020||0||AAs5roei2QVFVS0d0+RQtL5l/5DQrwJyxukORXBG+nMP8WXI7bUjxFCXeEV3DD3Q00GOpRYv51e7hCrjuDytDX+y5pY=|||1|0
51|1|+33742241337|1||1573746290833|1573746290833|0|1|-1|-2139094953|0|0||6ZyLkiOB0ctp4LGgZkaiyEgYX5z8/5R4Yk/kAQ/701teC08S8oyTtnnm2kunwnRyffKn/8M2RNXcfoVhkgHAkqwXj+qKmKcXsRVdoAqRx+mjEVxMN1kVhLVd2yrS/nfbRTpf25wj2WyNk+5Z1kjvAWMSl/w=|||-1|0
52|1|+33742241337|1||1573746492624|1573746492078||1|-1|-2139095020||0||0a2LV1iSQ4we9DJBwhLeBxuFP+NqAkuaQChru0STOV4OwODOLaBVlaCb+6WwH0b34CuqbhocOZOD9Z60kh2C9Puhr7xX0wMfqabCyBygjyD9Lfcd|||1|0
53|1|+33742241337|1||1573746587504|1573746587504|0|1|-1|-2139094953|0|0||AAu548/CtmgwPLre8swMuUbnpvCuPeBi2/flnnSgDt977BrXPMf5HK8U7ixtjEMtlrylnkyao+bZUw5UkMUv6OAX1BZo4QxLVGVxpNIOZWJKQCCpTE9ruNcJ//x6mZ/YwIq8+Kp3sTJOIRdW5JL2qyyd928=|||-1|0
54|1|+33742241337|1||1573746902281|1573746901318||1|-1|-2139095020||0||RJ4ft6b0rQIyzwOT8ZfAnZ2CVr0RGX85K2HEGNmTgohZO/zRXtUiZ79kZxrlN3+hhMY6l43vhxuIg/wzTa3T4m0CiO8=|||1|0
55|1|+33742241337|1||1573747010243|1573747010243|0|1|-1|-2139094953|0|0||FwG1VYXDjGcq/w1EBaAwmP9GMUh06FSawdWNNfk1J8IxSNyw7X1RxiE1FSbc8atnfpfMYskDYeooQ2twBaGDdlBFYCU=|||-1|0
56|1|+33742241337|1||1573747184152|1573747183614||1|-1|-2139095020||0||vtEYDNRMQQv7TX1YB5mqP2H5U9rPywEBjU/kiTet6sjhJb2Y0d11RvfxQmihQ5OvDvQqKbDC4CGSy7YjW/tVxFeYCcp2oFrtP8I+yYczevoBskcD|||1|0
57|1|+33742241337|1||1573747272106|1573747272106|0|1|-1|-2139094953|0|0||Rn9fuo9jlEy8RRZ4NkzRxhNPuiZCxTBi49kS+QEjzbOzAQRmEICKi6LlNnGoeF7CveO1ZPD+Qc3pDWKa5u063ikuQ/w6EdM+AHuO8Y4HMufL2oZQ|||-1|0
58|1|+33742241337|1||1573747360125|1573747359866||1|-1|-2139095020||0||Mj3L5ySyXLUaqofVIj/fU3OAICgfUTb/lyFLAIp0Xyg8zhJUqK+BG1DhixQBnS9GYFW6lVzVdu1C8zoVYAxIdiWuXotczhC0O1zHRZRbiX0RU4bB|||1|0
59|1|+33742241337|1||1573747417795|1573747417795|0|1|-1|-2139094953|0|0||MBJguQ01+DU/b2VgCFckdcVP7eMum58LWQ4YBa09t+x+ORU5v1OJy7T60BqH8PAR/Mtc1IL40HILvkt8FeaN0CLBBkZK9epfxu3/juU2WsRJyTzZwY7TNCNlPWu0JYMMbeea6nzA/g6ILJMmBXhQMAPSdok=|||-1|0
60|1|+33742241337|1||1573747437529|1573747436973||1|-1|-2139095020||0||8VaXqzJtXYCZPck3YFrhjf/xadSLdmPeowyOlg/3ST8QtfIgCTmPO7udUUe3slWQX5nsrRY0qS8CAwhSc34OXcyJahpOuypbywYIuNsFkB/sLWjORry9wBPoSNNvy7tSIonzAw==|||1|0
61|1|+33742241337|1||1573747464270|1573747464270|0|1|-1|-2139094953|0|0||SfcCs/WDFKYGgJKnL4rLKe7l2yA2raUbz2LbjHPoyhXawX9vySH0bVgu3J9EbIr1Qi3ULhWa95nKebI2POhyBSV3KVI=|||-1|0
62|1|+33742241337|1||1573747477605|1573747476681||1|-1|-2139095020||0||1RnWX9MAbiVhYPpgjum8tBttjs/Ci0lOje2EXoPXJnRAnB/Opa4m6tWWZYBRsjTvuwzOfybZvpQ9pqC3lP7lN/lYdxU=|||1|0
63|1|+33742241337|1||1573747485593|1573747485593|0|1|-1|-2139094953|0|0||VWS4AJ5HuUcQwd5LjNJy7+Snjgsn5FmZI10Gq/xEbHebV3K8MH70ma1knv09chCiftQKRhxVx+Jd+ITiNp82AvTlxcw=|||-1|0
64|1|+33742241337|1||1573747534084|1573747533651||1|-1|-2139095020||0||01TeblY2bjzp3/IX6M70SnzylQTj41fo61Mwh1v2AAQzGUSYGLvdlYQ8Sf8MxJgwvV2mG8HoxPpobrKrMIdDDfqGTp8rPrxmA+iS+IdkWVmaXFX4Yr6QwP4u0T37kdseaFx6Pw==|||1|0
65|1|+33742241337|1||1573747535738|1573747535738|0|1|-1|-2139094953|0|0||1cfURE4xvG3bbuM2nfXCJyhbQMZKU41ukpgDWKMQl8rqfGkfvPUFch6M6cU8gLRvow7t1qKiDloxxj7Kq8eHb3iIrXQuGg5iPTZhInWmrHytmgg0|||-1|0
66|1|+33742241337|1||1573747549389|1573747548962||1|-1|-2139095020||0||zPTMFV7sMlXpgA4RQf/tI3hHLzC7tijtHhDRqDH+TU5eKKlUBEJ8TGtyPA1gmCVG1CP32w==|||1|0
67|1|+33742241337|1||1573747550502|1573747550502|0|1|-1|-2139094953|0|0||UkdBDkcPeotKhJgWzcXOE9oQsDVeuEZ9UVNPJLTJO8BrabJL0zW/lX40jetaiT7vsmwVeMv00A7pQO/DQInR47Y3GkquXP/SdNWfLJZNk0Ud6DAplmwsQmnV7TxEAGctoK1PVQ==|||-1|0
68|1|+33742241337|1||1573747552357|1573747551892||1|-1|-2139095020||0||hgZIoIti/b1FCUqX6GX0reEVRPSU9u01C/U0FS04ADaIOUMIIHIP/li4ku22XNtmIWzfAB4mEs7OdN63TIqnps66tBQ=|||1|0
69|1|+33742241337|1||1573747556090|1573747556090|0|1|-1|-2139094953|0|0||fp0IcA+b04SelPnPL2F1F6HuYlf6bFuoFfdpRtX5gGnyPDVyku3jCwF7JEHMORp0T6L0Z4UKG59hIj+aTysSNWzKeyRMHKbGMX1VXJaBaCYh6h6t|||-1|0
70|1|+33742241337|1||1573747557228|1573747557144||1|-1|-2139095020||0||FHyXJzMKaXl+bO39xisB7UBb2sibl0KbCmHcjNJXWvprtIwzVazJDV+MNaeYXUedhhxWqdVj3MZ6VKJjoTYPZ9C1oWQ=|||1|0
71|1|+33742241337|1||1576081180421|1576081180126||1|-1|-2139095020||0||4VeyMNKiYjMPNERQCp/JGZVfScdQzxaF0LNnrKYNJc27b+OFFL2fv36GPd5rNgAdnWxNoQ18wtCRBjEwyJdIoaSa2L1h/Vku6LkRFswAXEc62UlD2/J5Myygc8LeZDVor2RsFy/I/UfoZkQ9fH4XDo8b2jc=|||1|0
72|1|+33742241337|1||1576081778276|1576081778276|0|1|-1|-2139094953|0|0||sYKHp16miSHctgeoHtGz9jdAsrDCnwGA/Uc59GKVAb3sbASjiL44Yn7cx3i6Tz96XWmmji9mVUwjyWn04jtYu9KedIr23jEONAaTnWvMejwYfXli8Baa6iQzR0yXdz2eHdQWY5quenEKuzljev7pxQw+r/s=|||-1|0
73|1|+33742241337|1||1576083328011|1576083327900||1|-1|-2139095020||0||aKyXAPnq9FpQ5JVTrN4xcKLL0kAqCHzy1sgfNzjI7JCjfojl5MaZDuG7adxbPGm+i59kB2lb+lnbbycG7e9yKdJkhJ+UrFBy+OpwZQlWzQ60kZ07R4pD7TK3FZplV54T2sdGuA==|||1|0
74|1|+33742241337|1||1576083811575|1576083811575|0|1|-1|-2139094953|0|0||ZuBgSYEO94sAXGJdV4fu6sCNGe75z3jPkJciqPpTJHCAGcE4pXNYPml1Eu1qOObQXShoIRvdO9GqTilcVng+Xk3EwUaVkwcad/RE5uzTKjFMFtcjM95N33MfWddrfgf3hGNHcA==|||-1|0
75|1|+33742241337|1||1576083917581|1576083917328||1|-1|-2139095020||0||PWEkjVlMPxv7dj3qMG29DMDLM+onM5Uxu5v3vh5CAtbUyAQam67tUU29xKPZHd9hSuSRIIQdW6e67HPfUqtmmZ/dyL+bYTYEDBfsoDHBXCKNLXyW7bdfl2XR+KT/tvGwfFW0aA==|||1|0
76|1|+33742241337|1||1576084287613|1576084287613|0|1|-1|-2139094953|0|0||oywmymMX/AAubKrER2vqXJoYQMmGOsLIV5sg7tD+h1NWOibQ2jQF1mR8D42RnPs2X5d+q6LJGbHsrvKC4IMoUGqxeohH40kI1YgDXdCcODrq9tLYspYXClMr/zb9BhuJCxaBknGoXJ1cUJ/JH9v/qsK5yZQ=|||-1|0
77|1|+33742241337|1||1576084868170|1576084868004||1|-1|-2139095020||0||wUL3jn1P3OojPq+KCuSNdhoGNnIXSTGYXMdr09UVf0FOTGmcKFW4AI1/dl4bbwc0aQL52APybs/gezeu3FWsZLNbCYtfTndhx5dd3VSjpZ4uyvASH97wvietBnpeHS25YqzPtMvufwUMFbHWjLPOOw5yz93WHMn57wR38pPN9wCfdrceqaEwlF0t1+TXy0HsLr/6WA==|||1|0
78|1|+33742241337|1||1576085386871|1576085386871|0|1|-1|-2139094953|0|0||SSrdt8ICPN4aS58tAf5orLY1sTcaoM6EatJmNJBV2ZobjwPfpdZ7mnOyPEcl1CQVrEdvfwVfReEZMUJV9J4OzAJSp9l2Jm5UEif5okWmRiVD8xY7/IitT6JIrkYP+PfCd739pg==|||-1|0
79|1|+33742241337|1||1576085538213|1576085537531||1|-1|-2139095020||0||DImlqV0UDSMDbfelO30FSdrcLOM1IXDE4G/UbJEc+Lou9MLXtQGDmqfy1/qWT/TxzVo0zipfIp9euV6o3rDzggZG80uo1R0o7w9IL9Zy+dp8zBqIShaKGujE9tv/wOnHLJxFKw==|||1|0
80|1|+33742241337|1||1576085768163|1576085768163|0|1|-1|-2139094953|0|0||F3mYEv6pY6x8X61YS2ljLHxZwkTKtmaaqHV0Mh0JSXk/3AD6w3R5pl48Nm7hdwsIXTsP1I+cG6w+VeLo0TUQr/ORSMl8NXC3h3GDgQ43B9YSDjE9|||-1|0
81|1|+33742241337|1||1576086199742|1576086198719||1|-1|-2139095020||0||ZEwHcIKnMwtevLnHbpwZkuinS/ER5dH7KtpuESKjatGC1HnsDn71yITr2NwHXGQk+z35lqFkIWkzXeqPfqJpTul79q8=|||1|0
82|1|+33742241337|1||1576086453584|1576086453584|0|1|-1|-2139094953|0|0||Ys3CK43pgCxvELE65Gq066U3/MSpvDeRw07Mmzsq5sGyX6p+XwZRfqbUPgPEWE8V+OqTxzhjWYeSjCn4np2f2wjtP2ShRyuF1fVv9nc8KZ8Y9kjw|||-1|0
83|1|+33742241337|1||1576086631283|1576086630781||1|-1|-2139095020||0||B52Vk5bgAou4ZXllA9boJBsw/xQz3UxS6VzQTNlXnigy1b+A6oJVMG5ElZm+BykrVj8VJyVVLdeBrxPrEz51bcXEk9fPvrS4ifigJrdFVlQHa9wy|||1|0
84|1|+33742241337|1||1576086752257|1576086752257|0|1|-1|-2139094953|0|0||J3shhIQ8+JKr5FEcXaSwwBt8oE3XTWzDPPFHl87aQbn2NC9AeAbHYizhAlVL4vA5sUc9BeEhL98bdmW4cSpmqOAaIPnwa+dd9u2tZvsEZMrY/lhW|||-1|0
85|1|+33742241337|1||1576086777249|1576086776564||1|-1|-2139095020||0||OjYmhExA3EbTFoIQMchebF8XWok6MIVquW3EhsVXk48XIgNfU1tEnAfRbMx83k3CKxy4KQ==|||1|0
86|1|+33742241337|1||1579255910384|1579255910384|0|1|-1|-2139094953|0|0||hARVV+7BwMlLywNdSHq913FjlZ+J9vAR7cOKQbEuNl5WZeaEH7newBsl6prig+6L4Cx4hvXKJ2IhEobDZCY4EQYJAtM=|||-1|0
87|1|+33742241337|1||1579256620707|1579256620513||1|-1|-2139095020||0||K2RBlqgyNjNaVlb3vZoU1QWcWafu05N7E7b/n3zMUmAoNt2aChTjE8bO/VumQWvKEeKvD5pOgdCaEVbpDOFJoZs3xno=|||1|0
88|1|+33742241337|1||1579261688344|1579261688344|0|1|-1|-2139094953|0|0||vH5ET5J+y3Gi7jnfaH1RDhWEBwO+cCzy6pY4+hh1Uxp3BpmuBdqQd8IVUocY7hfSx4FFc7V/GW6c4g7i0wsitk8H/ALaljcsw93yZjinGVED3YQ5ltxEoZmDUZOKeE11om9ngw==|||-1|0
89|1|+33742241337|1||1579263185672|1579263185030||1|-1|-2139095020||0||EkcLjbn1A6m1JZx5iJIxdI8Db4nmqyOybt6Nzd22bh3/YSYIp+Zh3MIuRmdVMebD71H5EsfRSinHi0R3jVfsE/Mwz7U=|||1|0
90|1|+33742241337|1||1579263300864|1579263300864|0|1|-1|-2139094953|0|0||70krXTrL8SFhK1M8sfPjhCmVEphIo9kM6s2fLK6pYPYpd/uciYtMH6RridOweD2jE60PjbyD0ZTuWHUpektCusZusq4H4FxLXB6p9t2e9wZ3DUH/PxJNuUHgcvu7b8TiAG3EhLJ1cH/tbxNdkLx2vPsIxsgQHehkUVwZLE/dqsUHnquT|||-1|0
91|1|+33742241337|1||1579263472603|1579263472039||1|-1|-2139095020||0||QEGz691TK7PjHBZXk9fm1w9Z9b9z0R1D/UshusJe5dVSCT9yzI4jribmcElZEtZ4Xx928eFXkcSfs7qsmeuC+LqATDBO5u1d8PfUnyD3rJrswRMPYu8uIOMd7Y9bADhvlX1rEtMpZIzCtvRzSRvx+hl7Yl+677NkUQ+tJulmGHLYwb/5|||1|0
92|1|+33742241337|1||1579264103985|1579264103985|0|1|-1|-2139094953|0|0||CBIdFQPKeSGA8lMTm0e8QAieLcrT0F1e+sFvczbrXKudFWhJ1ARsjch4E1aX4aq71R0zVA4Q/YxSjF+EfQoIx/Fk4NR+HE96V6MHKVFrRd5mctC1|||-1|0
93|1|+33742241337|1||1579264725655|1579264725487||1|-1|-2139095020||0||uzOSvuoTuPkEqvuBxNOFfKbXZlIQIkMXjuOFZY+aKJvVezifWBHgCujn0m8UIz0Sngd7fMaOw6HBIESw2v/e1ZS23W4=|||1|0
94|1|+33742241337|1||1580229747252|1580229746512||1|-1|-2139095020||0||8mIPtc6vPmBGrwQnrWLaZX+v8eudThWFfJgDpqTNW0BMrXWxuac9Ssql6O9R8aexdQwM/ckUvVcaTQ1OhF2069/qxh7VJkeLIkuLYP1WoByjg5Me|||1|0
95|1|+33742241337|1||1580230422973|1580230422973|0|1|-1|-2139094953|0|0||Xhwp2paU5GeZ4M1364MBQjYueBH4JJzJvtM5NUoIIp0+Wx6FoxUPDYUV7LzowYf4llxQnA==|||-1|0
96|1|+33742241337|1||1580230530174|1580230530061||1|-1|-2139095020||0||RM7a4q7rwaqX6xcR7Mpjy2Dw8O1WCBdS1eJ4320MezGHz62+gAKBzWUDTnXrKYaeXn2onGR2i9lqfOSUP5GvZBOtNWSz9IRYHq9iYLsNvVCIahmGXCkJB++ujwf2//Uz25X+B8SzSgkuIy4F/Jkv4Us0qmulpU7TcthgTlzpEP1Cmgl0x2h6sbkMOKrsmbja+EuklQ==|||1|0
97|1|+33742241337|1||1580232569940|1580232569940|0|1|-1|-2139094953|0|0||XQoMQMdTg8BEXXBV92ijkTvCPaNb7Xz+D3O65sqHY4R5f0Wf7OdI5KeiVWHaWTAkEDHReO7Hnotx4gUNX2idfpEPQqarSLxDmonUbjD19N4ede4R|||-1|0
98|1|+33742241337|1||1580232984257|1580232984193||1|-1|-2139095020||0||S6yNELwPHqu9GvBqd63rnsz39bBN3d9YJAC54kyehfqjcvZ0gII5BDwJAS8KI/LmnHgXhU/iOP2cXNkRnSj6c3amKzRyJR60zzft1bR0Tvz+7gGAgtEdgCCjSoVwx3H77ocQxCfqnWDlmpzfDDyM7iMngei8S/0/R2j6iiHAcrwhFa/wNAB46lgHrZpDDlt5ssIm8SDD/tKQDP/8wai8pQfZOEU=|||1|0
99|1|+33742241337|1||1580233458904|1580233458904|0|1|-1|-2139094953|0|0||G5hcXQXeQ24gnOATl4eVvA445iQ/PQqt3lMvdlBdo2I8/k6hNekQ1ZMOOIa7FkkU9efcSQX1bI+PEE6YW/Azj7S2MDiXm/BdhS8ZdDyv311VdWzm7SoUpc27DwM7ZFPMdY6Bdw==|||-1|0
100|1|+33742241337|1||1580233679661|1580233679570||1|-1|-2139095020||0||wpphxecqi1g9zyiXdhUTubIBTes1Xsjddr9zJxLTKEV9ZaSP53x2TMjhMLjSv09GZX8VpiXcMj4zxQ/jnf3D50DW2QO6EltD/iVNHsNXZmXPOsjpkAmGKTX1mhEe+U2AJjsQyQ==|||1|0
101|1|+33742241337|1||1580233879698|1580233879698|0|1|-1|-2139094953|0|0||z19jQtTCXLbyoN34sqZmjOhLl0cZ42KccYDV+s83dH+Tc4xMJcb51QYxtrADm1d/dz1TOXsEAD+4OTtOnaRsAk42Xes=|||-1|0
102|1|+33742241337|1||1580234263506|1580234263365||1|-1|-2139095020||0||L+ZQr389e32uMZjWbsb1pOy1Vf6VdbTObcLzvlwSTRMfs8JCq0Lg+vIdAahP+DHyN5Q7DhVcSdbApJxOs2b1wlnhL25Jd0wmia0emjFmgfH+NJ9BQLKGnNGd72u6J0DHYIxwg0IQys83MMKyetL8K7wfuE/ynBiCVVvmH7DZ+DiKnjkznaRE/sC3coqTgQeTEGo1Ww==|||1|0
103|1|+33742241337|1||1580234468660|1580234468660|0|1|-1|-2139094953|0|0||qk7rA9kwaPMu1ww1IJ0mcqOiffidxtBJHtugr92jZsCE5uEr7BrDIpQzI011RFS/1LcDnL0XgoCOtZ7GHq0sstCRK4XXTEKxUXiW3dE33vmxHvLVsSH5NhATxbNSUUe5l+MnDz/dbIUPkk7DLmZZsOF7Npg=|||-1|0
104|1|+33742241337|1||1580234555661|1580234555399||1|-1|-2139095020||0||gbv5kpftfkXBmVieaFjz0rE+eDTD6gH66qBw9JVjIaoeaSzmToUA4Mw8wJZIlETPiOkdGuFuKW7P6FisucDZSj6H5Cxe300KveZBy5EbYvZAbgClJE4FPLWGad/gkwf1bev4Q3Yrbgebgrzhj0/P3j1N098=|||1|0
105|1|+33742241337|1||1580234635857|1580234635857|0|1|-1|-2139094953|0|0||cmzRDxz1TuTvc7JSBIuqfSy+idLQetc301mOtAc0mmSXyfwpwk1bf/NWvvcA4joFkPCg5hLrEvZOCtjV35zufGvcTkpJG4tjLyy1egZ30iHLLqBp/eU2kU28Ea0rkY4tLQi7Mw==|||-1|0
106|1|+33742241337|1||1580234658356|1580234657925||1|-1|-2139095020||0||G+dOf1rwVs0bVMZZk4kxReVUBXLBX4++FVpotoqemM93nPaLYoXCccW0WhfIMNAvk1icyNiXBX87VUFTJkdJ8ELEAE4U3KTg1zgi6TksvibHMSGqsF55FgCtKeyNRbtsn+gJ0ThHdymNR9h6rhZzQjJSlyTdsTHqOxV3+p5EDUoq4yzO|||1|0
107|1|+33742241337|1||1580234730410|1580234730410|0|1|-1|-2139094953|0|0||LrTBBN96FLxnBTyx5LZgCFsVQWdehazDgoOt513ko/FlH3iNe0vw6ktIlSvzm9VQfntM7tVKQhWRjz7i4HV88bSoiY8AYjEtGR/ZvKDCam0uxmvXYccjGlJGEE0f4bzISFjq/Q==|||-1|0
108|1|+33742241337|1||1580234767134|1580234766366||1|-1|-2139095020||0||1T8IDWKnJ0G6UVLVP0ZvFb0FwDqlnhDpPC8yKcahQfjZakbvQE8UWU2PAvvDwfzOeomz2c0ZVj1uFNjc8Z3KWJLDPnBWyeVgZWQHDU9Bbwt3OPkRd3Zkx4lE4qgZMugFCkAhRY9WW5URS/vhPxuyxAmnmo8O19/wldF2T+73udRok4zNploA7SRruoS19VtujJLfQujqTxuNUVJnNlGcwW1YKlE=|||1|0
109|1|+33742241337|1||1580234796528|1580234796528|0|1|-1|-2139094953|0|0||zNSZqyjZQXCcuUigmPmFuylg/caYkwoSgbtzvMfi//Mny1BaA3FCeACuj+PS5QXBonFQZrS7XCJaHTfr9d4SFvWtjngzW8JVW92xl9Ki9NLzlixKUybTQoeSb2kgtwKlyJbsXg==|||-1|0
110|1|+33742241337|1||1580234836626|1580234836070||1|-1|-2139095020||0||1JheqRZKbqsardxSGeFdFrl5+r8XBaPg1WXEtQVTMWml/Ma+PkuiFZXD5C6xx+uLDxn4lYQJvWOvZAw2yV5dLEhruWkD8ooLFZUqXD83CfHeC9ZxC4jYPZJs2Bxp5uDCbpcoA0q937C8O76vUP+4ugignZrephE+CqARJN7pUnNwe+ZX|||1|0
111|1|+33742241337|1||1580234886849|1580234886849|0|1|-1|-2139094953|0|0||KkrkA9UtvpRoYJKYKwhPyUz9RNtoCy3FIZQ5oxxWGLgItgSJ4fw1PaF1usUWUlDY4jnEmMk3oDlllPdn97rLdQuE7J2sPIilvi45bYXqgnHF4dVBh1SuHNRGBEbJuts+eywAJ0r5s7k3W5pd+OGKJn2veIo=|||-1|0
112|1|+33742241337|1||1580234889637|1580234888947||1|-1|-2139095020||0||j4ScQTM1dQHeSWNSqpUVnk/3Qv4CkjVeanAlEzwE0goTp7uEO4KFR9HSR3E1EoWhfTBe0CBu95o1/2FaoxeLjjY40phexiePqnzaCpm+lApTX947SBBz8AY0zaeZp9ZRhaw2DYX75eGaKR8+r/zPiGUJ67k=|||1|0
113|1|+33742241337|1||1580234900822|1580234900822|0|1|-1|-2139094953|0|0||SaN4TJ1ZkBn/+B477WorREwfvN+c0m963THcRUrD6defaYBzXc5IhEHBOylUkIx+X2qSZ74tG0JTLFOvsorr35WK7Rg=|||-1|0
114|1|+33742241337|1||1580234901636|1580234901542||1|-1|-2139095020||0||+JIHX/5asdvF2nhKhwtORrG5OvlNvDKP5rZV6vo+lcyoVZbHkIBiACVLlQbv72Wb31Pwvc4vZZAMUIq6VvyYyFr9d8U=|||1|0
sqlite> select * from thread;
1|1580234901542|114|3|+JIHX/5asdvF2nhKhwtORrG5OvlNvDKP5rZV6vo+lcyoVZbHkIBiACVLlQbv72Wb31Pwvc4vZZAMUIq6VvyYyFr9d8U=|0|1|0|0|-2139095020||0|-1|1580234905438
```

We can also quickly check the other tables, but the `sms` one is of course what we should focus on:
```console
sqlite> select * from mms;
sqlite> select * from drafts;
sqlite> select * from identities;
4|3|BbP2zGmVR1d9cvCgHo/WlNoBryuUx6Za/VsUwKEvWEVU|RogpmPwdkQoRjADwBMdyGUT1fxM=
```

##  Application preferences (SMSSecure)
They are stored in file `SilenceExport/shared_prefs/SecureSMS-Preferences.xml`, which tells us that this is the `SecureSMS` application, by the way. Here we find cryptographic keys:

```xml
<?xml version='1.0' encoding='utf-8' standalone='yes' ?>
<map>
    <int name="passphrase_iterations" value="18743" />
    <boolean name="passphrase_initialized" value="true" />
    <string name="master_secret">/HKfpIBcOS94xxk3V+KuwGG8w6JMG67JK30vU9BB+k2LvU7Jk3sGd4j477m6EMi+Xx7LBS7iMUS11xuvx+zDPv8e16k=</string>
    <string name="asymmetric_master_secret_curve25519_private">S50Z7P9sdnhQdr+IVQ9U6ew+iUdTSFx4z+uO+8/F8LB1xytfDqhlz7ISAy3DQUzmVVGOIbI6KzzqTFYm2HtlNBUp3dtE3ujIi2HEQjxZBpwq2a5o</string>
    <string name="encryption_salt">9Be77hAJpDuviHX1s3iL6Q==</string>
    <string name="pref_identity_private_curve25519">I608P8gIzbHkh1A4ulinQhBo0h+mFU8hIjpV5YoRpZWy7IqvdoGlvbwVrUEcGgr0N9lPneHrigLsQv7oE+FQFVCnkv4ij2JBa3WyY1fekpVejN5/</string>
    <string name="mac_salt">QdB3nWZZ1Y7s5JrWq/dzww==</string>
    <string name="asymmetric_master_secret_curve25519_public">BSVqnzyu4pBX7+fWs9oTToNFlMGlZ0e6F7puN7hmjOFG</string>
    <string name="pref_identity_public_curve25519">BUM/3NOyDAI/O1Q7TjHoY2ZrsmPX+vo1DJdxqJnkkhlv</string>
</map>
```

## Decrypt the messages: breakthesilence
Googling around, I stumbled upon a tool that exactly does that: https://gitlab.com/hydrargyrum/breakthesilence.git

The main code is written in `Java`, plus some `shell` & `python` scripting around:
```console
$ tree breakthesilence/
breakthesilence/
├── breakthesilence_to_json.py
├── build-jar.sh
├── LICENSE
├── README.md
├── requirements.txt
├── run-all.sh
├── run-jar.sh
└── src
    └── re
        └── indigo
            └── breakthesilence
                └── MasterSecretUtil.java

4 directories, 8 files
```

Essentially, what it does is to ask for the `decryption password` as input (variable `$1` below), then try to recover the `encryption key` from the `SecureSMS-Preferences.xml` file:

```console
$ cat run-jar.sh
(...)
echo "$passwd" | java -cp "$BCPROV_JAR:build/breakthesilence.jar" re.indigo.breakthesilence.MasterSecretUtil "$1/shared_prefs/SecureSMS-Preferences.xml"
```

If that step is successful, the recovered keys are stored in a file (variable `$props` below) and the `Python` script is called to decrypt the messages in `messages.db`:

```console
$ cat run-all.sh
(...)
./breakthesilence_to_json.py "$1" "$2" < "$props"
```

Exactly what we need. Let's tweak it to `bruteforce the password`.

## Bruteforce the password
Here's the `Java` code from `breakthesilence`, modified to bruteforce the password:

```diff
diff --git a/src/re/indigo/breakthesilence/MasterSecretUtil.java b/src/re/indigo/breakthesilence/MasterSecretUtil.java
index c5bf347..3fa6e7e 100644
--- a/src/re/indigo/breakthesilence/MasterSecretUtil.java
+++ b/src/re/indigo/breakthesilence/MasterSecretUtil.java
@@ -274,40 +274,27 @@ public class MasterSecretUtil {
     }

     String userPassphrase;
-
-    if (System.console() != null) {
-      userPassphrase = new String(System.console().readPassword("Password (leave empty if empty): "));
-    } else {
-      System.err.println("No console, reading password from stdin.");
-      BufferedReader buffer = new BufferedReader(new InputStreamReader(System.in));
-      try {
-        userPassphrase = buffer.readLine();
-      } catch (IOException exc) {
-        System.err.println("Can't read stdin");
-        exc.printStackTrace(System.err);
-        System.exit(74);
-        return;
-      }
-    }
-
-    if (userPassphrase.isEmpty()) {
-      userPassphrase = UNENCRYPTED_PASSPHRASE;
-    }
-
     InputData silProps = new InputData();
     silProps.passphrase_iterations = Integer.parseInt(props.getProperty("passphrase_iterations"));
     silProps.master_secret = Base64.getDecoder().decode(props.getProperty("master_secret"));
     silProps.mac_salt = Base64.getDecoder().decode(props.getProperty("mac_salt"));
     silProps.encryption_salt = Base64.getDecoder().decode(props.getProperty("encryption_salt"));
+
+    for (int i = 10000; i <= 99999; i = i + 1) {
+
+    userPassphrase = Integer.toString(i);
     silProps.user_passphrase = userPassphrase;

     MasterSecret sec;
     try {
        sec = getMasterSecret(silProps, silProps.user_passphrase);
+       System.err.println("Code " + userPassphrase);
+       System.out.println("encryption_key = " + Base64.getEncoder().encodeToString(sec.encryptionKey));
+       System.out.println("mac_key = " + Base64.getEncoder().encodeToString(sec.macKey));
+       System.exit(0);
+       return;
     } catch (InvalidPassphraseException exc) {
-      System.err.println("Invalid passphrase!");
-      System.exit(65);
-      return;
+      System.err.println("Invalid passphrase " + userPassphrase);
     } catch (GeneralSecurityException exc) {
       exc.printStackTrace(System.err);
       System.exit(1);
@@ -317,8 +304,6 @@ public class MasterSecretUtil {
       System.exit(74);
       return;
     }
-
-    System.out.println("encryption_key = " + Base64.getEncoder().encodeToString(sec.encryptionKey));
-    System.out.println("mac_key = " + Base64.getEncoder().encodeToString(sec.macKey));
+    }
   }
 }
```

We rebuild the `JAR` file, then run it against the `SecureSMS-Preferences.xml` file we have:

```console
$ ./build-jar.sh
(...)
Successful build in build/breakthesilence.jar

$ java -cp 'bcprov-jdk15on-165.jar:build/breakthesilence.jar' re.indigo.breakthesilence.MasterSecretUtil '../../SilenceExport/shared_prefs/SecureSMS-Preferences.xml'
(...)
Invalid passphrase 56846
Invalid passphrase 56847
Invalid passphrase 56848
Code 56849
encryption_key = fYnrqMm95DkntXQHuEyxRg==
mac_key = M6c/T2mk87lbBQ43GPf/+icPryU=
```

Here we go ! We successfully recovered the `encryption keys` with `password = 56849`! Let's store them in a file, launch the `Python script` to decrypt the messages and collect the results in `messages.json`:

```console
$ cat keys.txt
encryption_key = fYnrqMm95DkntXQHuEyxRg==
mac_key = M6c/T2mk87lbBQ43GPf/+icPryU=

$ ./breakthesilence_to_json.py ../SilenceExport messages.json < keys.txt
Enter output of run-jar.sh:
OK, successfully read properties.
Proceeding to conversion, this may take a while, please wait!
Done!
```

We successfully decrypted the messages, especially the one containing the flag!

```console
$ cat messages.json | jq . | grep FCSC
        "body": "Le code est FCSC{07d6313bfb88a72ca39e223a78477c45}. Ne l'oublie pas, il ne marchera peut-être pas tout de suite.",
```

## Flag
> FCSC{07d6313bfb88a72ca39e223a78477c45}
