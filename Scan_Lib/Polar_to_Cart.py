"""
Jesse Moore CPTC 20202
Module to open a file of polar coordinates, convert them to cartesian with
provided offsets and output them into a seperate file. Made to work with
a module that generates a set of LiDAR scans.

Input File Format:
    Line 1: List of angle measurements as comma seperated values
    Line 2-n: Each line represents one scan of data as a comma seperated
    list.

Output File Format:
    Line 1-n: X, Y, Z followed by newline
"""
import math

angOffset = 90
scanHeight = 377
partLen = 254
partWid = 254
yOffset = partWid / 2
medianStep = 3


def polarFileToCart(path, f, xdist, debug=False):
    filename = path + 'cart_'+f
    with open(path + f, 'r') as pf, open(filename, 'w') as cf:
        firstLine = True
        scanNumber = 0
        if debug:
            print('P2C Starting file')
        """
        cf.write('0, 0, 0' + '\n' +
                 str(partLen) + ', 0, 0' + '\n' +
                 '0, ' + str(partWid) + ', 0' + '\n' +
                 str(partLen) + ', ' + str(partWid) + ', 0' + '\n')
        """
        for line in pf:
            if firstLine:
                if debug:
                    print('P2C Read angles')
                angles = line.split()
                for i in range(0, len(angles)):
                    angles[i] = float(angles[i]) - angOffset
                firstLine = False
                if debug:
                    print('P2C Processing data')
            else:
                dist = line.split()
                for j in range(len(dist)):
                    dist[j] = float(dist[j])
                    x = scanNumber
                    if angles[j] == 0:
                        y = 0
                        z = dist[j]
                        z = scanHeight - z
                    else:
                        theta = angles[j] * math.pi / 180
                        y = dist[j] * math.sin(theta)
                        y = math.copysign(y, angles[j])
                        # y = y * -1
                        # y = y + yOffset
                        z = dist[j] * math.cos(theta)
                        z = scanHeight - z
                    cf.write(str(x) + ', ' + str(y) + ', ' + str(z) + '\n')
            scanNumber += xdist
    if debug:
        print('P2C Finished')
