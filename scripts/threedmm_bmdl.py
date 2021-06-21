import os
from collections import namedtuple

BmdlVertex = namedtuple('BmdlVertex', ['x', 'y', 'z', 'u', 'v'])
BmdlTriangle = namedtuple('BmdlFace', ['v1', 'v2', 'v3'])

class ThreeDMovieMakerBMDL:
    ORDER_LITTLE = 'little'
    SCALE_POSITION = 65535.0
    SCALE_TEXTURE = 65535.0

    def __init__(self, path_bmdl_file: str):

        self.vertices = []
        self.triangles = []

        with open(path_bmdl_file, 'rb') as bmdl_file:
            data = bmdl_file.read()
        
        byteCount = len(data)

        vertexCount = int.from_bytes(data[4:6], byteorder=self.ORDER_LITTLE, signed=False)
        triangleCount = int.from_bytes(data[6:8], byteorder=self.ORDER_LITTLE, signed=False)

        vertexStart = 4 + 2 + 2 + 40
        triangleStart = vertexStart + 32*vertexCount

        #print('Header stuff')

        #print(data[0:48].hex('|', -2))

        #print('Vertices')

        for i in range(vertexCount):
            curVertStart = vertexStart + 32*i

            x = int.from_bytes(data[curVertStart:curVertStart+4], byteorder=self.ORDER_LITTLE, signed=True) / self.SCALE_POSITION
            y = int.from_bytes(data[curVertStart+4:curVertStart+8], byteorder=self.ORDER_LITTLE, signed=True) / self.SCALE_POSITION
            z = int.from_bytes(data[curVertStart+8:curVertStart+12], byteorder=self.ORDER_LITTLE, signed=True) / self.SCALE_POSITION
            u = int.from_bytes(data[curVertStart+12:curVertStart+16], byteorder=self.ORDER_LITTLE, signed=True) / self.SCALE_TEXTURE
            v = int.from_bytes(data[curVertStart+16:curVertStart+20], byteorder=self.ORDER_LITTLE, signed=True) / self.SCALE_TEXTURE

            #print(data[curVertStart:curVertStart+32].hex('|', -4))

            self.vertices.append(BmdlVertex(x, y, z, u, v))

        #print('Triangles')

        for i in range(triangleCount):
            curTriStart = triangleStart + 32*i

            v1 = int.from_bytes(data[curTriStart:curTriStart+2], byteorder=self.ORDER_LITTLE, signed=False)
            v2 = int.from_bytes(data[curTriStart+2:curTriStart+4], byteorder=self.ORDER_LITTLE, signed=False)
            v3 = int.from_bytes(data[curTriStart+4:curTriStart+6], byteorder=self.ORDER_LITTLE, signed=False)

            #print(data[curTriStart:curTriStart+32].hex('|', -2))

            self.triangles.append(BmdlTriangle(v1, v2, v3))
    