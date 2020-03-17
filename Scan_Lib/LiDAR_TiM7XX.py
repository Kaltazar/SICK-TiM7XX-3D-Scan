'''
Jesse Moore CPTC 2020
Python module to work with SICK LiDAR TiM7XX scanners via Telegram protocal
This is a set of functions to work with SICK 2D LiDAR scanners over Ethernet.
This module supports multiple instances of scanners.
'''
import socket

# Telegram commands
scanOnce = "\x02sRN LMDscandata\x03".encode()
outputRange = "\x02sRN LMPoutputRange\x03".encode()


# Create scanner instences
class Lidar:
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.ip_port = 2112
        self.sock = None
        self.mesCount = 0

    # Get start and stop angles and number of points returned as list
    def getAngles(self):
        spaceCount = 0
        spaceTarget = 4
        d = []
        dt = ''
        self.sock.send(outputRange)
        while True:
            c = self.sock.recv(1).decode()
            if c == ' ' and spaceCount < spaceTarget:
                spaceCount += 1
            elif spaceCount == spaceTarget:
                if c == '\x03':
                    d.append(dt)
                    break
                elif c != ' ':
                    dt += c
                elif c == ' ':
                    d.append(dt)
                    dt = ''
        s = int(d[0], 16)/10000
        e = int(d[1], 16)/10000
        return s, e

    # Returns a list off all angles based on scans per degree, 3 for the TiM7XX
    def getAngleList(self):
        s, e = self.getAngles()
        n = 3
        angles = []
        for i in range(int(s), int(e)):
            angles.append(i)
            for j in range(1, n):
                angles.append(i + (j/n))
        angles.append(e)
        self.mesCount = len(angles)
        return angles

    # Scan once and get distances returned as list
    def singleScan(self):
        if self.mesCount == 0:
            self.getAngleList()
        self.sock.send(scanOnce)
        spaceCount = 0
        spaceTarget = 26
        d = []
        dt = ''
        count = 0
        while True:
            c = self.sock.recv(1).decode()
            if c == '\x02':
                inside = True
            if inside is True:
                if c == ' ' and spaceCount < spaceTarget:
                    spaceCount += 1
                elif count == self.mesCount:
                    if c == '\x03':
                        inside = False
                        break
                elif spaceCount == spaceTarget:
                    if c != ' ':
                        dt += c
                    elif c == ' ':
                        d.append(dt)
                        dt = ''
                        count += 1
        for i in range(0, len(d)):
            d[i] = int(d[i], 16)
        return d

    # Get a full raw packet of data as a decoded string
    def getFull(self):
        self.sock.send(scanOnce)
        data = ''
        while True:
            c = self.sock.recv(1).decode()
            if c == '\x02':
                start = True
            elif c == '\x03':
                start = False
                return data
                break
            elif start is True:
                data += c

    # Connetion functions
    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.ip_address, int(self.ip_port)))
        except OSError:
            print('Could not connect to LiDAR at IP: ' + self.ip_address +
                  'Check the IP and connections.')

    def disconnect(self):
        self.sock.close()
