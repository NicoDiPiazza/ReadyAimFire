import pygame
from collideLogic import collideX, collideY
from math import sin, cos, atan, sqrt
from numpy import zeros, pi

pygame.init()

## variable
screenWidth = 1000
screenHeight = 600

targetLocX = screenWidth/2 + 10
targetLocY = screenHeight/2 + 10

playerX = screenWidth/2
playerY = screenHeight/2
playerRad = 20
playerSpeed = 5
playerColor = 250

cameraX = 0
cameraY = 0

dt = 60

clock = pygame.time.Clock()

# number of lines in the line-of-sight radar
nRadLines = 100

# angles from player to each corner
topLeftTheta = - atan(playerY/-playerX)
topRightTheta = atan(playerY/(screenWidth - playerX))
bottomRightTheta = atan(-(screenHeight - playerY)/(screenWidth - playerX))
bottomLeftTheta = - atan(-(screenHeight - playerY)/-playerX)

#all de lines of vision

LOSradar = []
for i in range(nRadLines):
    # Radar EndPoint in the X, ditto Y
    radarTheta = 2 * pi * i/nRadLines + 0.1
    repx = playerX + screenWidth * cos(radarTheta) + 0.1
    repy = playerY + screenWidth * sin(radarTheta)
    # m here means slope
    m = (repy - playerY)/(repx - playerX)
    b = playerY - (m * playerX)

    LOSradar.append([playerX, playerY, repx, repy, m, b, False])


pygame.event.get()
keys = pygame.key.get_pressed()
mouseDown = pygame.mouse.get_pressed(num_buttons=3)
mouseX, mouseY = pygame.mouse.get_pos()

screen_size = [ screenWidth, screenHeight]
screen = pygame.display.set_mode(screen_size)

## Classes

class Wall():
    def __init__ (self, x:float, y:float, width:float, height:float):
         self.x = x
         self.y = y
         self.width = width
         self.height = height
         
wall1 = Wall(cameraX + screenWidth * 0.5, cameraY + screenHeight * 1/7,screenWidth / 10, screenHeight / 3)
wall2 = Wall(cameraX + screenWidth * 0.25, cameraY + screenHeight * 0.5,screenWidth / 2, screenHeight / 6)
wall3 = Wall(cameraX + screenWidth * 1.2, cameraY + screenHeight * 1,screenWidth / 3, screenHeight / 3)
wall4 = Wall(cameraX + screenWidth * 0.1, cameraY + screenHeight * 0.1,screenWidth / 6, screenHeight / 1.5)

wallArray = [wall1, wall2, wall3, wall4]


while (keys[pygame.K_q] != True):
    ## inputs
    pygame.event.get()
    keys = pygame.key.get_pressed()
    mouseDown = pygame.mouse.get_pressed(num_buttons=3)
    mouseX, mouseY = pygame.mouse.get_pos()

    ## BEGIN MOVEMENT SCRIPT
    if ((mouseDown[2] == True)):
         targetLocX, targetLocY = mouseX, mouseY

    if (sqrt(((targetLocY - playerY)**2) + (targetLocX - playerX)**2) > playerSpeed):
            #x component and y component
            # the .5 is there to prevent a division by 0 error
            XComp = playerSpeed * abs(cos(atan((targetLocY - playerY)/(targetLocX - playerX + 0.5))))
            YComp = playerSpeed * abs(sin(atan((targetLocY - playerY)/(targetLocX - playerX + 0.5))))
            if (playerX < targetLocX):
                targetLocX = targetLocX - XComp
                cameraX = cameraX - XComp
                
            else:
                 targetLocX = targetLocX + XComp
                 cameraX = cameraX + XComp
            
            if (playerY < targetLocY):     
                targetLocY = targetLocY - YComp
                cameraY = cameraY - YComp
            else:
                targetLocY = targetLocY + YComp
                cameraY = cameraY + YComp
            for i in range(len(wallArray)):
                wallX = wallArray[i].x + cameraX
                wallY = wallArray[i].y + cameraY
                wallWidth = wallArray[i].width
                wallHeight = wallArray[i].height
                targetLocY = targetLocY - collideY(playerX - playerRad, playerY - playerRad, playerRad * 2, playerRad * 2, wallX, wallY, wallWidth, wallHeight, YComp)
                cameraY = cameraY - collideY(playerX - playerRad, playerY - playerRad, playerRad * 2, playerRad * 2, wallX, wallY, wallWidth, wallHeight, YComp)
                targetLocX = targetLocX - collideX(playerX - playerRad, playerY - playerRad, playerRad * 2, playerRad * 2, wallX, wallY, wallWidth, wallHeight, XComp)
                cameraX = cameraX - collideX(playerX - playerRad, playerY - playerRad, playerRad * 2, playerRad * 2, wallX, wallY, wallWidth, wallHeight, XComp)
    else:
        targetLocX = playerX
        targetLocY = playerY

    ## END MOVEMENT SCRIPT

    ## calculating the LOS fog

    #vision obstructions array
    visionObsts = []
    for i in range(len(wallArray)):
        # this logic assumes that the walls are rectangles, and thus endeavors to make 4 lines out of them. I should generalize this to any size of polygon, 
        # but I'm not, because the Wall class only accounts for rectsangles, so... 
        # (maybe I should do triangles? they're more popular... Then I could make everything out of triangles, like most people do. It would only add one more line...)
        #ok yup i should defionitely refactor everything to be based around triangles. then slanted walls would be waaaayyy easier. But that's an overhaul for later

        #0 indicates horizontal, 1 indicates vertical
        visionObsts.append([0, wallArray[i].x + cameraX, wallArray[i].y + cameraY, wallArray[i].x + wallArray[i].width + cameraX]) #top
        visionObsts.append([1, wallArray[i].y + cameraY, wallArray[i].x + cameraX, wallArray[i].y + wallArray[i].height + cameraY]) #left
        visionObsts.append([0, wallArray[i].x + cameraX, wallArray[i].y + wallArray[i].height + cameraY, wallArray[i].x + wallArray[i].width + cameraX]) # bottom
        visionObsts.append([1, wallArray[i].y + cameraY, wallArray[i].x + wallArray[i].width + cameraX, wallArray[i].y + wallArray[i].height + cameraY]) # right


    #line-of-sight-intersections
    LOSinter = []
    intersectionOrder = []

    # for each line in the radar, we check each line in the vision obstructions array for an intersection
    # i'd like to reiterate here that this is EXCLUSIVELY for horizontal and vertical lines, and will need to be reworked to handle all other lines when triangles are added
    for i in range(len(LOSradar)):

        hitSomething = False
        # m here means slope
        m = LOSradar[i][4]
        b = LOSradar[i][5]
        for j in range(len(visionObsts)):
            
            if (visionObsts[j][0] == 0):

                # now we solve for y/m, and put it in the array
                xIntersection = (visionObsts[j][2] - b)/m
                newPoint = [xIntersection, visionObsts[j][2]]

                #checking that it's on the raycast, and not its inverse
                onRaycastX = abs(playerX - LOSradar[i][2]) >= abs(playerX - xIntersection)

                if onRaycastX:

                    if visionObsts[j][2] > playerY:
                        onRaycastY = visionObsts[j][2] <= LOSradar[i][3]
                    else:
                        onRaycastY = visionObsts[j][2] >= LOSradar[i][3]

                onRaycast = onRaycastX and onRaycastY
                if (xIntersection >= visionObsts[j][1] and xIntersection <= visionObsts[j][3] and onRaycast):
                    if hitSomething != True:
                        LOSinter.append(newPoint)
                        hitSomething = True
                        #elif (the distance from the new point to the player) > (the distance from the old point to the player)
                    elif((abs(newPoint[0] - playerX)+ abs(newPoint[1] - playerY)) < (abs(LOSinter[-1][0] - playerX) + abs(LOSinter[-1][1] - playerY))):
                        LOSinter[-1] = newPoint     

            else:
                yIntersection = (m * visionObsts[j][2]) + b
                newPoint = [visionObsts[j][2], yIntersection]

                onRaycastY = abs(playerY - LOSradar[i][3]) >= abs(playerY - yIntersection)

                if onRaycastY:
                    if visionObsts[j][2] > playerX:
                        onRaycastX = visionObsts[j][2] <= LOSradar[i][2]
                    else:
                        onRaycastX = visionObsts[j][2] >= LOSradar[i][2]


                onRaycast = onRaycastX and onRaycastY
                if (yIntersection >= visionObsts[j][1] and yIntersection <= visionObsts[j][3] and onRaycast):
                    if hitSomething != True:
                        LOSinter.append(newPoint)
                        hitSomething = True
                        #elif (the distance from the new point to the player) > (the distance from the old point to the player)
                    elif((abs(newPoint[0] - playerX) + abs(newPoint[1] - playerY)) < (abs(LOSinter[-1][0] - playerX) + abs(LOSinter[-1][1] - playerY))):
                        LOSinter[-1] = newPoint

        if hitSomething == False:
            LOSinter.append(0)
        LOSradar[i][6] = hitSomething




## display
    pygame.draw.polygon(screen, (150, 150, 150), [(0, 0), (screenWidth, 0), (screenWidth, screenHeight), (0, screenHeight)], 0)

    for i in range(len(LOSinter)):
        if LOSradar[i][6] and LOSradar[i-1][6]:
            pygame.draw.polygon(screen, (40, 60, 100), [(LOSinter[i][0], LOSinter[i][1]),(LOSinter[i-1][0], LOSinter[i-1][1]), 
                                                        (LOSradar[i-1][2], LOSradar[i-1][3]), (LOSradar[i][2], LOSradar[i][3])], 0)
        """ pygame.draw.circle(screen, (250, 0, 0), [LOSinter[i][0], LOSinter[i][1]], 5, 0)
        pygame.draw.line(screen, (0, 0, 0), [LOSradar[i][0], LOSradar[i][1]], [LOSradar[i][2], LOSradar[i][3]]) """

    #drawing all the walls
    for i in range(len(wallArray)):     
        pygame.draw.polygon(screen, (80, 40, 60), [(cameraX + wallArray[i].x, cameraY + wallArray[i].y),
                                                    (cameraX + wallArray[i].x + wallArray[i].width, cameraY + wallArray[i].y),
                                                   (cameraX + wallArray[i].x + wallArray[i].width, cameraY + wallArray[i].y + wallArray[i].height), 
                                                   (cameraX + wallArray[i].x, cameraY + wallArray[i].y + wallArray[i].height)], 0)


    pygame.draw.circle(screen, (250, playerColor, 250), [playerX, playerY], playerRad, 0)

    print(clock.get_fps())

    clock.tick(dt)
    pygame.display.update()