# from IO import io
# from Util import server
import traceback
import numpy
import cv2
import math

# converts images into data usable for SLAM and driving

# WALL HEIGHTS ARE FROM EDGES INCLUSIVEs

# constants
X = 0
Y = 1
DISTANCE = 2
ANGLE = 3

# colors
rm = redMin = (0, 80, 75)
rM = redMax = (55, 255, 255)
gm = greenMin = (30, 20, 30)
gM = greenMax = (110, 255, 255)

# other constants
imageWidth = 544
imageHeight = 308
focalLength = 105
wallHeight = 10
cameraOffsetX = 3
cameraOffsetY = 10

# create blob detectors
__params = cv2.SimpleBlobDetector_Params()
__params.filterByArea = True
__params.minArea = 65
__params.maxArea = 128941274721
__params.filterByCircularity = True
__params.minCircularity = 0.3
__params.filterByConvexity = True
__params.minConvexity = 0.7
# __params.filterByInertia = True
# __params.minInertiaRatio = 0
# __params.maxInertiaRatio = 1
blobDetector = cv2.SimpleBlobDetector_create(__params)
blobSizeConstant = 0.6

def filter(imgIn: numpy.ndarray):
    try:
        global redMax, redMin, greenMax, greenMin
        # convert to HSV
        hsv = cv2.cvtColor(imgIn, cv2.COLOR_BGR2HSV)
        # red filter
        # red is at 0 and also 180, accounting for HSV wraparound
        rMask1 = cv2.inRange(hsv, redMin, redMax)
        redMinList = list(redMin)
        redMinList = [180 - redMax[0], redMinList[1], redMinList[2]]
        redMin2 = tuple(redMinList)
        redMaxList = list(redMax)
        redMaxList = [180, redMaxList[1], redMaxList[2]]
        redMax2 = tuple(redMaxList)
        rMask2 = cv2.inRange(hsv, redMin2, redMax2)
        rMask = cv2.bitwise_or(rMask1, rMask2)
        # green filter
        gMask = cv2.inRange(hsv, greenMin, greenMax)
        # blur images to remove noise
        blurredR = cv2.medianBlur(rMask, 5)
        blurredG = cv2.medianBlur(gMask, 5)
        grayImage = cv2.cvtColor(imgIn, cv2.COLOR_RGB2GRAY)
        blurredImg = cv2.GaussianBlur(grayImage, (3, 3), 0)
        # edge detection
        lower = 50
        upper = 125
        edgesImg = cv2.Canny(blurredImg, lower, upper, 3)
        # combine images
        return [edgesImg, blurredG, blurredR]
    except Exception as err:
        traceback.print_exc()
        io.error()
        server.emit('programError', str(err))

# remapping for distortion correction
K=numpy.array([[181.20784053368962, 0.0, 269.26274741570063], [0.0, 180.34861809531762, 164.95661764906816], [0.0, 0.0, 1.0]])
D=numpy.array([[0.08869574884019396], [-0.06559255628891703], [0.07411420387674333], [-0.03169574352239552]])
remap, remapInterpolation = cv2.fisheye.initUndistortRectifyMap(K, D, numpy.eye(3), K, (imageWidth, imageHeight), cv2.CV_16SC2)

# distance scanner
wallStartLeft = 163
wallStartRight = 154
wallEnd = imageHeight
wallEnd = 249
wallStartBuffer = 5
halfWidth = round(imageWidth / 2)
distanceTable = [[], []]
for imgx in range(imageWidth):
    distanceTable[0].append([])
    distanceTable[1].append([])
    distanceTable[0][imgx].append((-1, -1, -1, -1))
    for height in range(1, wallEnd - wallStartLeft + 1):
        dist = wallHeight * math.sqrt((focalLength ** 2) + ((imgx - halfWidth) ** 2)) / height
        angle = math.atan2(halfWidth - remap[wallStartLeft + height - 1][imgx][0], focalLength) + math.pi * 2 / 3
        x = -cameraOffsetX + math.sin(angle) * dist
        y = cameraOffsetY + math.cos(angle) * dist
        cDist = math.sqrt(x ** 2 + y ** 2)
        cAngle = (math.atan2(y, x) + math.pi / 2) % (math.pi * 2) - math.pi
        distanceTable[0][imgx].append((x, y, cDist, cAngle))
    distanceTable[1][imgx].append((-1, -1, -1, -1))
    for height in range(1, wallEnd - wallStartRight + 1):
        dist = wallHeight * math.sqrt((focalLength ** 2) + ((imgx - halfWidth) ** 2)) / height
        angle = math.atan2(halfWidth - remap[wallStartRight + height - 1][imgx][0], focalLength) + math.pi / 3
        x = cameraOffsetX + math.sin(angle) * dist
        y = cameraOffsetY + math.cos(angle) * dist
        cDist = math.sqrt(x ** 2 + y ** 2)
        cAngle = (math.atan2(y, x) + math.pi / 2) % (math.pi * 2) - math.pi
        distanceTable[1][imgx].append((x, y, cDist, cAngle))
def getRawHeights(leftEdgesIn: numpy.ndarray, rightEdgesIn: numpy.ndarray):
    global wallHeight, wallStartLeft, wallStartRight, wallEnd
    
    # crop and then flip
    croppedLeft = numpy.swapaxes(leftEdgesIn[wallStartLeft + wallStartBuffer:wallEnd], 0, 1)
    croppedRight = numpy.swapaxes(rightEdgesIn[wallStartRight + wallStartBuffer:wallEnd], 0, 1)

    # find the bottom edge of the wall
    rawHeightsLeft = numpy.array(numpy.argmax(croppedLeft, axis=1), dtype="float") + wallStartBuffer + 2
    rawHeightsRight = numpy.array(numpy.argmax(croppedRight, axis=1), dtype="float") + wallStartBuffer + 2

    return [rawHeightsLeft, rawHeightsRight]
def mergeHeights(rawHeightsLeft: numpy.ndarray, rawHeightsRight: numpy.ndarray):
    return 'oof'
def getDistances(leftEdgesIn: numpy.ndarray, rightEdgesIn: numpy.ndarray):
    global distanceTable
    
    # crop and then flip
    croppedLeft = numpy.swapaxes(leftEdgesIn[wallStartLeft + wallStartBuffer:wallEnd], 0, 1)
    croppedRight = numpy.swapaxes(rightEdgesIn[wallStartRight + wallStartBuffer:wallEnd], 0, 1)

    # find the bottom edge of the wall
    rawHeightsLeft = numpy.array(numpy.argmax(croppedLeft, axis=1), dtype="float") + wallStartBuffer + 2
    rawHeightsRight = numpy.array(numpy.argmax(croppedRight, axis=1), dtype="float") + wallStartBuffer + 2

    # convert heights to coordinates
    leftCoordinates = numpy.apply_along_axis(lambda a: distanceTable[0][int(a[1])][int(a[0])], 1, numpy.stack((rawHeightsLeft, range(imageWidth)), 1))
    rightCoordinates = numpy.apply_along_axis(lambda a: distanceTable[1][int(a[1])][int(a[0])], 1, numpy.stack((rawHeightsRight, range(imageWidth)), 1))

    return [leftCoordinates, rightCoordinates]
def mergeDistances(leftCoordinates: numpy.ndarray, rightCoordinates: numpy.ndarray):
    # merge
    coordinates = numpy.concatenate((leftCoordinates, rightCoordinates))

    # sort coordinates by angle
    dtype = [('x', coordinates.dtype), ('y', coordinates.dtype), ('dist', coordinates.dtype), ('theta', coordinates.dtype)]
    ref = coordinates.ravel().view(dtype)
    ref.sort(order=['theta', 'dist', 'x', 'y'])

    return coordinates
def getDistance(imgx: int, height: int, dir: int):
    global distanceTable
    return distanceTable[max(dir, 0)][imgx][int(height)]

def getWallLandmarks(distances: numpy.ndarray, rBlobs: list, gBlobs: list):
    for blob in rBlobs:
        for i in range(blob[0] - blob[1], blob[0] + blob[1] + 1):
            if i >= 0 and i < imageWidth:
                distances[i][2] = -1
    for blob in gBlobs:
        for i in range(blob[0] - blob[1], blob[0] + blob[1] + 1):
            if i >= 0 and i < imageWidth:
                distances[i][2] = -1

    sampleSize = 30
    
    slopeChanges = numpy.full(imageWidth - sampleSize, 0)

    for i in range(imageWidth - sampleSize * 2):
        leftSlope = (distances[i + sampleSize - 1][Y] - distances[i][Y]) / (distances[i + sampleSize - 1][X] - distances[i][X])
        rightSlope = (distances[i + sampleSize * 2 - 1][Y] - distances[i + sampleSize][Y]) / (distances[i + sampleSize * 2 - 1][X] - distances[i + sampleSize][X])
        invalid = False
        for j in range(i, i + sampleSize * 2):
            if distances[j][2] == -1:
                invalid = True
                break
        if invalid:
            continue
        leftAngle = math.atan2(leftSlope, 1)
        rightAngle = math.atan2(rightSlope, 1)
        if abs(leftAngle - rightAngle) > math.pi / 4:
            slopeChanges[i] = 1
            if i != 0:
                slopeChanges[i - 1] = 1
            if i != imageWidth - 1:
                slopeChanges[i + 1] = 1

    slopeChanging = 0
    landmarks = []
    for i in range(imageWidth - sampleSize):
        # # if slopeChanges[i] == 0 and slopeChanging >= sampleSize / 4:
        if (slopeChanging > 0 and slopeChanges[i] == 0) or slopeChanging >= sampleSize * 2 + 2:
            landmarks.append([i - math.ceil(slopeChanging / 2) + sampleSize, slopeChanges[i - math.ceil(slopeChanging / 2) + sampleSize]])
            # landmarks.append([i - 1, slopeChanges[i - 1]])
            slopeChanging = 0
        # if slopeChanges[i] != 0 or slopeChanging > 0:
        #     landmarks.append([i, slopeChanges[i]])
        if slopeChanges[i] == 0:
            slopeChanging = 0
        else:
            slopeChanging += 1
    
    if slopeChanging > 0:
        landmarks.append([imageWidth - math.ceil(slopeChanging / 2), slopeChanges[imageWidth - math.ceil(slopeChanging / 2)]])
    return landmarks

def getBlobs(rLeftIn: numpy.ndarray, gLeftIn: numpy.ndarray, rRightIn: numpy.ndarray, gRightIn: numpy.ndarray):
    global wallStartLeft, wallStartRight, wallEnd
    try:
        # add borders to fix blob detection
        # blobStart = 79
        # blobEnd = 100 # fix???
        rLeft = cv2.copyMakeBorder(rLeftIn[wallStartLeft:wallEnd], 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=[0,0,0])
        gLeft = cv2.copyMakeBorder(gLeftIn[wallStartLeft:wallEnd], 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=[0,0,0])
        rRight = cv2.copyMakeBorder(rRightIn[wallStartRight:wallEnd], 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=[0,0,0])
        gRight = cv2.copyMakeBorder(gRightIn[wallStartRight:wallEnd], 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=[0,0,0])

        blobDetector.empty()
        rLeftBlobs = processBlobs(blobDetector.detect(255 - rLeft))
        blobDetector.empty()
        gLeftBlobs = processBlobs(blobDetector.detect(255 - gLeft))
        blobDetector.empty()
        rRightBlobs = processBlobs(blobDetector.detect(255 - rRight))
        blobDetector.empty()
        gRightBlobs = processBlobs(blobDetector.detect(255 - gRight))

        return [rLeftBlobs, gLeftBlobs, rRightBlobs, gRightBlobs]

    except Exception as err:
        traceback.print_exc()
        io.error()
        server.emit('programError', str(err))

def processBlobs(blobs: list):
    newBlobs = []
    for blob in blobs:
        newBlobs.append([math.floor(blob.pt[0]), math.ceil(blob.size * blobSizeConstant)])
    
    return newBlobs

def mergeBlobs(leftBlobs: list, rightBlobs: list):
    # keep angle and distance instead of x and size
    return []

def setColors(data: list, sendServer: bool):
    global redMax, redMin, greenMax, greenMin
    redMax = (int(data[0]), int(data[2]), int(data[4]))
    greenMax = (int(data[1]), int(data[3]), int(data[5]))
    redMin = (int(data[6]), int(data[8]), int(data[10]))
    greenMin = (int(data[7]), int(data[9]), int(data[11]))
    print('-- New ----------')
    print(redMax, redMin)
    print(greenMax, greenMin)
    if sendServer:
        server.emit('colors', getColors())
def getColors():
    global redMax, redMin, greenMax, greenMin
    array = []
    for i in range(6):
        if i % 2 == 0:
            array.append(redMax[math.ceil(i / 3)])
        else:
            array.append(greenMax[math.ceil((i - 1) / 3)])
    for i in range(6):
        if i % 2 == 0:
            array.append(redMin[math.ceil(i / 3)])
        else:
            array.append(greenMin[math.ceil((i - 1) / 3)])
    return array
def setDefaultColors():
    global rM, rm, gM, gm
    print('-- New ----------')
    print(rM, rm)
    print(gM, gm)
    return [rM[2], gM[2], rM[1], gM[1], rM[0], gM[0], rm[2], gm[2], rm[1], gm[1], rm[0], gm[0]]