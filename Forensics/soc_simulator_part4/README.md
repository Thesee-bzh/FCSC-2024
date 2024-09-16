# SOC Simulator

## Challenge
Durant l'été 2022, un opérateur d'importance vitale (OIV) alerte l'ANSSI car il pense être victime d'une cyberattaque d'ampleur. Le security operation center (SOC) de l'OIV envoie à l'ANSSI un export de sa collecte système des derniers jours. Vous êtes chargé de comprendre les actions réalisées par l'attaquant.

Note : Les 5 parties sont numérotées dans l'ordre chronologique de l'attaque mais il n'est pas nécessaire de les résoudre dans l'ordre.

## Part4 - Lateral move
Sur une courte période de temps, l'attaquant a essayé de se connecter à de nombreuses machines, comme s'il essayait de réutiliser les secrets volés dans la partie 2. Cela lui a permis de se connecter à la machine Workstation2. Retrouver l'IP source, le compte utilisé et l'heure UTC de cette connexion.

> Format du flag (insensible à la casse) : FCSC{192.168.42.27|MYCORP\Technician|2021-11-27T17:38:54}.

## Decode evtx files to json
Convert `event files` to `json` using `evtx_dump` from https://github.com/omerbenamram/evtx.git. We use format `jsonl` so that we can parse output with `jq`:

```console
$ for file in $(ls *.evtx); do evtx_dump $file -o jsonl -f $file.json; done
```

## Check failed logons
Here's a small `bash script` to extract the `Event IDs` from the `event logs` using `jq`:

```console
$ cat get_event_ids.sh
cat $1 | jq -r '.Event.System.EventID' | sort -nr | uniq -c | sort -nr
$
$ for file in $(ls *.json); do ./get_event_ids.sh $file > $file.eventids; done
```

We see an unusual number of failed logons (`event 4625`) in those `event files`:

```console
$ grep 4625 *.eventids
(...)
20220706T153443.evtx.eventids:     21 4625
20220706T154249.evtx.eventids:      8 4625
(...)
```

## Details of login attempts around from 20220706T153443.evtx
Let's focus on that file `20220706T153443.evtx` now and look at the `login attempts` in detail:

```console
$ cat logins.sh
cat $1 | jq -r '.Event as $e | select($e.System.EventID == "4625" or $e.System.EventID == "4624") | [$e.System.TimeCreated."#attributes".SystemTime, $e.System.EventID, $e.System.Computer, $e.EventData.TargetUserName, $e.EventData.TargetDomainName, $e.EventData.IpAddress, $e.EventData.IpPort] | join("\t")'
```

Here are the `failed login attempts` in a short period of time. This is using the `Administrator` account:

```console
$ ./logins.sh 20220706T153443.evtx.json | grep 4625
2022-07-06T13:22:57.861846300Z  4625    DC01.tinfa.loc  Administrator   tinfa.loc       172.16.20.20    64745
2022-07-06T13:24:52.739018000Z  4625    DC01.tinfa.loc  Administrator   DC01    fe80::81f:b104:22cc:90f1        56659
2022-07-06T13:22:59.575596100Z  4625    exchange.tinfa.loc      Administrator   tinfa.loc       172.16.20.20    64769
2022-07-06T13:22:59.321969600Z  4625    Workstation7.tinfa.loc  Administrator   tinfa.loc       172.16.20.20    64765
2022-07-06T13:26:55.995391100Z  4625    Workstation7.tinfa.loc  Administrator   WORKSTATION7    172.16.20.20    63734
2022-07-06T13:22:57.730770300Z  4625    Workstation2.tinfa.loc  Administrator   tinfa.loc       172.16.20.20    64743
2022-07-06T13:26:56.087064200Z  4625    DC01.tinfa.loc  Administrator   DC01    172.16.20.20    63736
2022-07-06T13:22:59.186332600Z  4625    Workstation1.tinfa.loc  Administrator   tinfa.loc       172.16.20.20    64763
2022-07-06T13:26:56.174084700Z  4625    Workstation1.tinfa.loc  Administrator   WORKSTATION1    172.16.20.20    63738
2022-07-06T13:22:58.811549300Z  4625    Workstation5.tinfa.loc  Administrator   tinfa.loc       172.16.20.20    64755
2022-07-06T13:26:56.674205300Z  4625    Workstation5.tinfa.loc  Administrator   WORKSTATION5    172.16.20.20    63753
2022-07-06T13:22:59.695697700Z  4625    Workstation0.tinfa.loc  Administrator   tinfa.loc       172.16.20.20    64771
2022-07-06T13:26:56.664043000Z  4625    Workstation0.tinfa.loc  Administrator   WORKSTATION0    172.16.20.20    63747
2022-07-06T13:22:58.553102600Z  4625    Workstation8.tinfa.loc  Administrator   tinfa.loc       172.16.20.20    64751
2022-07-06T13:26:56.274502100Z  4625    Workstation8.tinfa.loc  Administrator   WORKSTATION8    172.16.20.20    63740
2022-07-06T13:22:58.097901200Z  4625    Workstation4.tinfa.loc  Administrator   tinfa.loc       172.16.20.20    64747
2022-07-06T13:26:56.807941100Z  4625    Workstation4.tinfa.loc  Administrator   WORKSTATION4    172.16.20.20    63751
2022-07-06T13:22:58.782223700Z  4625    Workstation6.tinfa.loc  Administrator   tinfa.loc       172.16.20.20    64753
2022-07-06T13:26:57.394870800Z  4625    Workstation6.tinfa.loc  Administrator   WORKSTATION6    172.16.20.20    63762
2022-07-06T13:22:59.804414400Z  4625    Workstation9.tinfa.loc  Administrator   tinfa.loc       172.16.20.20    64773
2022-07-06T13:26:56.725031600Z  4625    Workstation9.tinfa.loc  Administrator   WORKSTATION9    172.16.20.20    63749
```

## Focusing on workstation2
Now focusing on the `workstation2`:

```console
$ ./logins.sh 20220706T153443.evtx.json | grep -i workstation2
2022-07-06T13:22:23.971033300Z  4624    WEC.tinfa.loc   WORKSTATION2$   TINFA.LOC       -       -
2022-07-06T13:23:52.972888800Z  4624    WEC.tinfa.loc   WORKSTATION2$   TINFA.LOC       -       -
2022-07-06T13:24:04.039245100Z  4624    WEC.tinfa.loc   WORKSTATION2$   TINFA.LOC       -       -
2022-07-06T13:25:21.972435100Z  4624    WEC.tinfa.loc   WORKSTATION2$   TINFA.LOC       -       -
2022-07-06T13:22:57.210183900Z  4624    Workstation2.tinfa.loc  ANONYMOUS LOGON NT AUTHORITY    172.16.20.20    64719
2022-07-06T13:22:57.730770300Z  4625    Workstation2.tinfa.loc  Administrator   tinfa.loc       172.16.20.20    64743
2022-07-06T13:26:55.701792200Z  4624    Workstation2.tinfa.loc  ANONYMOUS LOGON NT AUTHORITY    172.16.20.20    63707
2022-07-06T13:26:57.153049100Z  4624    Workstation2.tinfa.loc  Administrator   WORKSTATION2    172.16.20.20    63759
2022-07-06T13:26:57.208596300Z  4624    Workstation2.tinfa.loc  Administrator   WORKSTATION2    172.16.20.20    63760
2022-07-06T13:27:38.048795400Z  4624    DC01.tinfa.loc  WORKSTATION2$   TINFA.LOC       172.16.10.202   59403
2022-07-06T13:26:50.972560800Z  4624    WEC.tinfa.loc   WORKSTATION2$   TINFA.LOC       -       -
2022-07-06T13:27:52.582618400Z  4624    WEC.tinfa.loc   WORKSTATION2$   TINFA.LOC       -       -
2022-07-06T13:28:19.974415000Z  4624    WEC.tinfa.loc   WORKSTATION2$   TINFA.LOC       -       -
2022-07-06T13:29:48.974505900Z  4624    WEC.tinfa.loc   WORKSTATION2$   TINFA.LOC       -       -
2022-07-06T13:31:17.974252100Z  4624    WEC.tinfa.loc   WORKSTATION2$   TINFA.LOC       -       -
2022-07-06T13:32:46.973930700Z  4624    WEC.tinfa.loc   WORKSTATION2$   TINFA.LOC       -       -
2022-07-06T13:34:04.040128000Z  4624    WEC.tinfa.loc   WORKSTATION2$   TINFA.LOC       -       -
2022-07-06T13:34:15.973543000Z  4624    WEC.tinfa.loc   WORKSTATION2$   TINFA.LOC       -       -
```

Indeed, we see a successfull login from `Administrator` on `workstation2` in that same timeframe, exactly at `2022-07-06T13:26:57`:

```console
$ ./logins.sh 20220706T153443.evtx.json | grep -i workstation2 | grep Administrator | grep 4624
2022-07-06T13:26:57.153049100Z  4624    Workstation2.tinfa.loc  Administrator   WORKSTATION2    172.16.20.20    63759
2022-07-06T13:26:57.208596300Z  4624    Workstation2.tinfa.loc  Administrator   WORKSTATION2    172.16.20.20    63760
```

## Flag
> FCSC{172.16.20.20|WORKSTATION2\Administrator|2022-07-06T13:26:57}
