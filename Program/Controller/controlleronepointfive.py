from IO import io
from Util import server
from Controller import converter
from Controller import slam
import math
import cv2
import base64
import numpy
import time

X = 0
Y = 1
TYPE = 2
FOUND = 3

OUTER_WALL = 0
INNER_WALL = 1
RED_PILLAR = 2
GREEN_PILLAR = 3

NO_DIRECTION = 0
CLOCKWISE = 1
COUNTER_CLOCKWISE = -1

turnPillar = 0

useServer = True
def setMode(sendServer: bool = None):
    global useServer
    if sendServer != None: useServer = sendServer

def drive():
    global turnPillar
# def drive(img):
    totalStart = time.perf_counter()
    start = time.perf_counter()
    read = io.camera.io.camera.io.camera.io.camera.io.camera.read()
    # print("camera: ", time.perf_counter() - start)
    start = time.perf_counter()
    # read = numpy.split(numpy.array(img), 2, axis=1)
    leftEdgesImg, gLeftImg, rLeftImg = converter.filter(converter.undistort(read[0]))
    rightEdgesImg, gRightImg, rRightImg = converter.filter(converter.undistort(read[1]))
    # print("filter + undistort: ", time.perf_counter() - start)
    start = time.perf_counter()
    # leftCoordinates, rightCoordinates = converter.getDistances(leftEdgesImg, rightEdgesImg)

    leftHeights, rightHeights = converter.getRawHeights(leftEdgesImg, rightEdgesImg)
    rLeftContours = converter.getContours(rLeftImg)
    gLeftContours = converter.getContours(gLeftImg)
    rRightContours = converter.getContours(rRightImg)
    gRightContours = converter.getContours(gRightImg)

    leftWalls = converter.getWalls(leftHeights.copy(), rLeftContours, gLeftContours)
    rightWalls = converter.getWalls(rightHeights.copy(), rRightContours, gRightContours)

    rContours = converter.mergeContours(rLeftContours, rRightContours, leftHeights, rightHeights)
    gContours = converter.mergeContours(gLeftContours, gRightContours, leftHeights, rightHeights)

    corners, walls = converter.processWalls(leftWalls, rightWalls)
    # print("image processing: ", time.perf_counter() - start)
    start = time.perf_counter()

    slam.carAngle = io.imu.angle()

    if slam.carDirection == NO_DIRECTION:
        slam.findStartingPosition(leftHeights, rightHeights)
    
    processedWalls = []

    centerWalls = 0
    leftWalls = 0
    rightWalls = 0
    
    centerWallDistance = 0
    leftWallDistance = 0
    rightWallDistance = 0

    carAngle = 0

    for wall in walls:
        UNKNOWN = -1
        LEFT = 0
        CENTER = 1
        RIGHT = 2
        wallType = 0
        
        if wall[0][X] - wall[1][X] != 0 and wall[0][Y] - wall[1][Y] != 0:
            slope = (wall[0][Y] - wall[1][Y]) / (wall[0][X] - wall[1][X])
            yIntercept = -wall[0][Y] - slope * wall[0][X]
            
            distance = abs(yIntercept) / math.sqrt(slope**2 + 1)
            angle = math.atan2(-slope, 1)

            if (abs(slope) < 0.75):
                wallType = CENTER
            else:
                if wall[0][X] - wall[0][Y] / slope < 0:
                    wallType = LEFT
                else:
                    wallType = RIGHT
                # if slope > 0:
                #     wallType = LEFT
                # else:
                #     wallType = RIGHT
                # if wall[0][X] > 0 and wall[1][X] > 0:
                #     wallType = RIGHT
                # elif wall[0][X] < 0 and wall[1][X] < 0:
                #     wallType = LEFT
                # else:
                    # wallType = UNKNOWN
        elif wall[0][Y] - wall[1][Y] != 0:
            # vertical wall
            distance = abs(wall[0][X])
            if wall[0][X] > 0 and wall[1][X] > 0:
                wallType = RIGHT
                angle = math.pi / 2
            elif wall[0][X] < 0 and wall[1][X] < 0:
                wallType = LEFT
                angle = -math.pi / 2
            else:
                wallType = UNKNOWN
        else:
            #horizontal wall
            distance = abs(wall[0][Y])
            angle = 0
            wallType = CENTER
        
        if wallType == CENTER:
            centerWalls += 1
            centerWallDistance += distance
            carAngle += angle
        elif wallType == LEFT:
            leftWalls += 1
            leftWallDistance += distance
            # carAngle += angle + math.pi / 2
        elif wallType == RIGHT:
            rightWalls += 1
            rightWallDistance += distance
            # carAngle += angle - math.pi / 2
        
        processedWalls.append([wallType, distance, angle])
        
    if centerWalls != 0:
        centerWallDistance /= centerWalls
        carAngle /= centerWalls
    if leftWalls != 0:
        leftWallDistance /= leftWalls
    if rightWalls != 0:
        rightWallDistance /= rightWalls
    
    # if centerWalls + leftWalls + rightWalls != 0:
    #     carAngle /= centerWalls + leftWalls + rightWalls
    
    pillar = [None]
    for contour in rContours:
        if pillar[0] == None or contour[2] < pillar[2]:
            pillar = contour
            pillar.append(RED_PILLAR)
    for contour in gContours:
        if pillar[0] == None or contour[2] < pillar[2]:
            pillar = contour
            pillar.append(GREEN_PILLAR)
    
    steering = 0

    waypointX = 0
    waypointY = 0
    
    if centerWalls != 0 and centerWallDistance < 130:
        print("Corner SECTION")
        if turnPillar == 0:
            if pillar[0] != None:
                turnPillar = pillar[4]
        if turnPillar == 0:
            if centerWallDistance < 100:
                steering = 100
        elif turnPillar == RED_PILLAR:
            if centerWallDistance < 130:
                steering = 100
        elif turnPillar == GREEN_PILLAR:
            if centerWallDistance < 80:
                steering = 100
        if steering == 0:
            steering = -carAngle * 20
    else:
        turnPillar = 0
        # if leftWalls != 0 and rightWalls != 0:
        #     total = leftWallDistance + rightWallDistance
        #     if total > 80 / math.cos(carAngle):
        #         leftWallDistance += (100 / math.cos(carAngle) - total) / 2
        #         rightWallDistance += (100 / math.cos(carAngle) - total) / 2
        #     else:
        #         leftWallDistance += (60 / math.cos(carAngle) - total) / 2
        #         rightWallDistance += (60 / math.cos(carAngle) - total) / 2
        if pillar[0] == None:
            if leftWalls != 0 and rightWalls != 0:
                steering = rightWallDistance - leftWallDistance - carAngle * 20
            elif leftWalls != 0 and leftWallDistance < 30:
                steering = 100
            elif rightWalls != 0 and rightWallDistance < 30:
                steering = -100
            else:
                steering = -carAngle * 20
        else:
            xDistance = 0
            yDistance = pillar[Y] - 15
            if leftWalls != 0 and rightWalls != 0:
                if pillar[4] == RED_PILLAR:
                    xDistance = (pillar[X] + rightWallDistance) / 2
                else:
                    xDistance = (pillar[X] - leftWallDistance) / 2
            elif leftWalls != 0 and pillar[4] == GREEN_PILLAR:
                xDistance = (pillar[X] - leftWallDistance) / 2
            elif rightWalls != 0 and pillar[4] == RED_PILLAR:
                xDistance = (pillar[X] + rightWallDistance) / 2
            else:
                xDistance = pillar[X]
                if pillar[4] == RED_PILLAR:
                    xDistance += 10
                else:
                    xDistance -= 10
            waypointX = xDistance
            waypointY = yDistance
            steering = math.atan2(xDistance, yDistance) * 30

    # print("driving: ", time.perf_counter() - start)
    start = time.perf_counter()

    if useServer:
        data = {
            'images': [
                base64.b64encode(cv2.imencode('.png', cv2.merge((leftEdgesImg, gLeftImg, rLeftImg)))[1]).decode(),
                base64.b64encode(cv2.imencode('.png', cv2.merge((rightEdgesImg, gRightImg, rRightImg)))[1]).decode(),
                1,
                1,
                1
            ],
            'distances': [],
            'heights': [leftHeights.tolist(), rightHeights.tolist()],
            'pos': [slam.carX, slam.carY, slam.carAngle],
            'landmarks': slam.storedLandmarks,
            'rawLandmarks': [rContours, gContours, walls],
            'contours': [[rLeftContours, gLeftContours], [rRightContours, gRightContours]],
            'walls': [corners, walls, processedWalls],
            'steering': steering,
            'waypoints': [[], [waypointX, waypointY], 1],
            'raw': [steering, centerWallDistance, leftWallDistance, rightWallDistance, carAngle]
        }
        server.emit('data', data)
    # print("sendserver: ", time.perf_counter() - start)
    
    io.drive.steer(steering)

    print("total: ", time.perf_counter() - totalStart)
    # for points in leftWalls:
    #     x1,y1,x2,y2=points
    #     cv2.line(leftEdgesImg,(x1,y1),(x2,y2),125,2)
    
    # print(leftWalls)

    # return leftEdgesImg

def getDistance(a, b):
    try:
        return math.sqrt(math.pow(a[X] - b[X], 2) + math.pow(a[Y] - b[Y], 2))
    except Exception as e:
        print(e, a, b)

    
def transformCorner(corner):
    corner = list(corner)
    corner[X] = math.sin(-slam.carAngle) * corner[X] + math.cos(-slam.carAngle) * corner[Y]
    corner[Y] = math.cos(-slam.carAngle) * corner[X] + math.sin(-slam.carAngle) * corner[Y]
    return corner