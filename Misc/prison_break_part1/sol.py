import BAC0
import random
import socket

LOCAL_IP = "<local ip>" ## FIX HERE: e.g., 192.168.0.42
LOCAL_PORT = random.randint(1024, 65535)

if __name__ == "__main__":

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

    # Complete here
    bacnet.whois(target)
    for _, (address, device_id) in enumerate(bacnet.discoveredDevices):
        print(f"device {address} {device_id}")
        objlist = bacnet.read(f"{address} device {device_id} objectList")
        print(f"{objlist=}")
        token = bacnet.read(f"{address} characterstringValue 1 description")
        print(f"{token=}")
