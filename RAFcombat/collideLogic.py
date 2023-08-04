def collideX(actorX, actorY, actorWid, actorHei, obstX, obstY, obstWid, obstHei, actorSpeed):
## This function is not for physics collisions, it is just for walls in videogames

    ## actor: the thing trying to move
    ## (actorX, actorY): actor's top left coordinate
    ## 
    if (actorY + actorHei > obstY and actorY < obstY + obstHei):
        if (actorX + actorWid > obstX and actorX < obstX + actorWid/2):
            return - actorSpeed

        elif(actorX <= obstX + obstWid and actorX > obstX + obstWid - actorWid/2):
            return actorSpeed
            
        else:
            return 0
    else:
        return 0
    

def collideY(actorX, actorY, actorWid, actorHei, obstX, obstY, obstWid, obstHei, actorSpeed):
## This function is not for physics collisions, it is just for walls in videogames

    ## actor: the thing trying to move
    ## (actorX, actorY): actor's top left coordinate
    ## 
    if (actorX + actorWid > obstX and actorX < obstX + obstWid):
        if (actorY + actorHei > obstY and actorY < obstY + actorHei/2):
            return - actorSpeed
        elif(actorY <= obstY + obstHei and actorY > obstY + obstHei - actorHei/2):
            return actorSpeed
            
        else:
            return 0
    else:
        return 0