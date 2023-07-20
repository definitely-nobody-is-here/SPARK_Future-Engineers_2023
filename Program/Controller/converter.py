# from IO import io
# from Util import server
from Controller import slam
import traceback
import numpy
import cv2
import math

# converts images into data usable for SLAM and driving

# WALL HEIGHTS ARE FROM EDGES INCLUSIVEs

# colors
rm = redMin = (0, 80, 75)
rM = redMax = (55, 255, 255)
gm = greenMin = (30, 20, 30)
gM = greenMax = (110, 255, 255)

# other constants
horizontalFov = 155
verticalFov = 115
imageWidth = 544
imageHeight = 308
focalLength = ((imageWidth / 2) / math.tan(math.pi * (horizontalFov / 2) / 180))
focalLength = 91
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
halfWidth = round(imageWidth / 2)
distanceTable = [[], []]
for imgx in range(imageWidth):
    distanceTable[0].append([])
    distanceTable[1].append([])
    distanceTable[0][imgx].append((-1, -1, -1, -1))
    for height in range(1, wallEnd - wallStartLeft + 1):
        dist = wallHeight * math.sqrt((focalLength ** 2) + ((imgx - halfWidth) ** 2)) / height
        vAngle = math.atan2(remap[wallStartLeft + height - 1][imgx][0], remap[wallStartLeft + height - 1][imgx][1])
        x = -cameraOffsetX + math.cos(vAngle) * dist
        y = cameraOffsetY + math.sin(vAngle) * dist
        cDist = math.sqrt(x ** 2 + y ** 2)
        cAngle = (math.atan2(y, x) + math.pi / 2) % (math.pi * 2) - math.pi
        distanceTable[0][imgx].append((x, y, cDist, cAngle))
    distanceTable[1][imgx].append((-1, -1, -1, -1))
    for height in range(1, wallEnd - wallStartRight + 1):
        dist = wallHeight * math.sqrt((focalLength ** 2) + ((imgx - halfWidth) ** 2)) / height
        vAngle = math.atan2(remap[wallStartRight + height - 1][imgx][0], remap[wallStartRight + height - 1][imgx][1])
        x = cameraOffsetX + math.cos(vAngle) * dist
        y = cameraOffsetY + math.sin(vAngle) * dist
        cDist = math.sqrt(x ** 2 + y ** 2)
        cAngle = (math.atan2(y, x) + math.pi / 2) % (math.pi * 2) - math.pi
        distanceTable[1][imgx].append((x, y, cDist, cAngle))
def getRawHeights(leftEdgesIn: numpy.ndarray, rightEdgesIn: numpy.ndarray):
    global wallHeight, wallStartLeft, wallStartRight, wallEnd
    
    # crop and then flip
    croppedLeft = numpy.flip(numpy.swapaxes(leftEdgesIn[wallStartLeft:wallEnd], 0, 1), axis=1)
    croppedRight = numpy.flip(numpy.swapaxes(rightEdgesIn[wallStartRight:wallEnd], 0, 1), axis=1)

    # find the bottom edge of the wall
    rawHeightsLeft = wallEnd - wallStartLeft - numpy.array(numpy.argmax(croppedLeft, axis=1), dtype="float")
    rawHeightsRight = wallEnd - wallStartRight - numpy.array(numpy.argmax(croppedRight, axis=1), dtype="float")

    # TODO: OPTImIZE @SAMPLEPROVIDER(SPSPSPSPSPPSPSPSPPSPSS)
    for i in range(imageWidth):
        rawHeightsLeft[i] = remap[round(imageHeight - rawHeightsLeft[i] - 1)][i][1] - wallStartLeft
        rawHeightsRight[i] = remap[round(imageHeight - rawHeightsRight[i] - 1)][i][1] - wallStartRight

    return [rawHeightsLeft, rawHeightsRight]
def getHeights(leftEdgesIn: numpy.ndarray, rightEdgesIn: numpy.ndarray):
    rawHeightsLeft, rawHeightsRight = getRawHeights(, leftEdgesIn, rightEdgesIn)

    # TODO: OPTImIZE @SAMPLEPROVIDER(SPSPSPSPSPPSPSPSPPSPSS)
    # for i in range(imageWidth):
    #     rawHeightsLeft[i] = remap[round(wallEnd - rawHeightsLeft[i] - 1)][i][1] - wallStartLeft
    #     rawHeightsRight[i] = remap[round(wallEnd - rawHeightsRight[i] - 1)][i][1] - wallStartRight

    return [rawHeightsLeft, rawHeightsRight]
def getDistances(leftEdgesIn: numpy.ndarray, rightEdgesIn: numpy.ndarray):
    global distanceTable
    
    # crop and then flip
    croppedLeft = numpy.flip(numpy.swapaxes(leftEdgesIn[wallStartLeft:wallEnd], 0, 1), axis=1)
    croppedRight = numpy.flip(numpy.swapaxes(rightEdgesIn[wallStartRight:wallEnd], 0, 1), axis=1)

    # find the bottom edge of the wall
    rawHeightsLeft = wallEnd - wallStartLeft - numpy.array(numpy.argmax(croppedLeft, axis=1), dtype="float")
    rawHeightsRight = wallEnd - wallStartRight - numpy.array(numpy.argmax(croppedRight, axis=1), dtype="float")

    # convert heights to coordinates
    leftCoordinates = numpy.apply_along_axis(lambda a: distanceTable[0][int(a[1])][int(a[0])], 1, numpy.stack((rawHeightsLeft, range(imageWidth)), 1))
    rightCoordinates = numpy.apply_along_axis(lambda a: distanceTable[1][int(a[1])][int(a[0])], 1, numpy.stack((rawHeightsRight, range(imageWidth)), 1))
    coordinates = numpy.concatenate((leftCoordinates, rightCoordinates))

    # sort coordinates by angle
    dtype = [('x', coordinates.dtype), ('y', coordinates.dtype), ('dist', coordinates.dtype), ('theta', coordinates.dtype)]
    ref = coordinates.ravel().view(dtype)
    ref.sort(order=['theta', 'dist', 'x', 'y'])

    return coordinates
def getDistance(imgx: int, height: int, dir: int):
    global distanceTable
    return distanceTable[max(dir, 0)][imgx][int(height)]

def getWallLandmarks(heights: numpy.ndarray, rBlobs: list, gBlobs: list):
    # for blob in rBlobs:
    #     for i in range(blob[0] - blob[1], blob[0] + blob[1] + 1):
    #         if i >= 0 and i < imageWidth:
    #             heights[i] = -1
    # for blob in gBlobs:
    #     for i in range(blob[0] - blob[1], blob[0] + blob[1] + 1):
    #         if i >= 0 and i < imageWidth:
    #             heights[i] = -1

    heights = numpy.array(heights, dtype="float")

    sampleSize = 30
    
    slopeChanges = numpy.full(imageWidth - sampleSize, 0)

    for i in range(imageWidth - sampleSize * 2):
        leftSlope = (heights[i + sampleSize - 1] - heights[i]) / sampleSize
        rightSlope = (heights[i + sampleSize * 2 - 1] - heights[i + sampleSize]) / sampleSize
        leftDifference = 0
        rightDifference = 0
        invalid = False
        for j in range(i, i + sampleSize):
            if heights[j] == -1:
                invalid = True
                break
            error = (heights[j] - (heights[i] + leftSlope * (j - i)))

            leftDifference += error ** 2
            # leftDifference += (error * 3) ** 3 / 3
        if invalid:
            continue
        for j in range(i + sampleSize, i + sampleSize * 2):
            if heights[j] == -1:
                invalid = True
                break
            error = (heights[j] - (heights[i + sampleSize] + rightSlope * (j - i - sampleSize)))

            rightDifference += error ** 2
            # rightDifference += (error * 3) ** 3 / 3
        if invalid:
            continue
        angle = math.atan(leftSlope) - math.atan(rightSlope)
        # if i == 286 - sampleSize:
        #     print(leftSlope, rightSlope, leftDifference, rightDifference)
        #     print(angle)
        #     print(abs(leftSlope - rightSlope) > 0.1, leftDifference < sampleSize * 2, rightDifference < sampleSize * 2)
        if abs(leftSlope - rightSlope) > 0.075 and leftDifference < sampleSize * 2 and rightDifference < sampleSize * 2:
            slopeChanges[i] = 1
            if i != 0:
                slopeChanges[i - 1] = 1
            if i != imageWidth - 1:
                slopeChanges[i + 1] = 1
            print(i, leftSlope, rightSlope, leftDifference, rightDifference)
        # if abs(angle) > math.pi / 12 * leftDifference / sampleSize * rightDifference / sampleSize:

        # if abs(leftDifference) < sampleSize / 2 
        # if abs(difference) > sampleSize:
        #     slopeChanges[i] = difference

    slopeChanging = 0
    landmarks = []
    for i in range(imageWidth - sampleSize):
        # # if slopeChanges[i] == 0 and slopeChanging >= sampleSize / 4:
        if slopeChanges[i] == 0 or slopeChanging >= sampleSize:
            landmarks.append([i - round(slopeChanging / 2) + sampleSize, slopeChanges[i - round(slopeChanging / 2) + sampleSize]])
            # landmarks.append([i - 1, slopeChanges[i - 1]])
            slopeChanging = 0
        # if slopeChanges[i] != 0 or slopeChanging > 0:
        #     landmarks.append([i, slopeChanges[i]])
        if slopeChanges[i] == 0:
            slopeChanging = 0
        else:
            slopeChanging += 1
    
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

def processBlobs(leftBlobs: list, rightBlobs: list):
    newBlobs = []
    # for blob in blobs:
    #     newBlobs.append([math.floor(blob.pt[0]), math.ceil(blob.size * blobSizeConstant)])
    
    return newBlobs

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