# -*- coding: utf-8 -*-
from pymol.cgo import *
from pymol import cmd
from random import randint
#from string import split

#############################################################################
#
# drawMinBoundingBox.py -- Draws the smallest box surrounding a selection
#
# AUTHOR: Jason Vertrees
# DATE  : 2/20/2009
# NOTES : See comments below.
#
#############################################################################
def drawMinBoundingBoxtr(sel="(all)", xtr=0.0, ytr=0.0, ztr=0.0, lineWidth=2.0, r=1.0, g=1.0, b=1.0):
    """
    DESCRIPTION
        Given sel, draw the minimum bounding box around it.

    USAGE:
        drawMinBoundingBoxtr [sel, [lineWidth, [r, [g, b]]]]

    PARAMETERS:
        sel,            the selection to enboxen.  :-)
                        defaults to (all)

        lineWidth,      width of box lines
                        defaults to 2.0

        r,              red color component, valid range is [0.0, 1.0]
                        defaults to 1.0

        g,              green color component, valid range is [0.0, 1.0]
                        defaults to 1.0

        b,              blue color component, valid range is [0.0, 1.0]
                        defaults to 1.0

    RETURNS
        string, the name of the CGO box

    NOTES
        * This function creates a randomly named CGO box that minimally spans the protein.  The
        user can specify the width of the lines and also the color.

        * Maybe add a padding function?  This might help docking folks -- eg. add a 5 Ang border around
          the protein then draw the box there?
    """

    ([minX, minY, minZ],[maxX, maxY, maxZ]) = cmd.get_extent(sel)
    minX=minX+float(xtr)
    minY=minY+float(ytr)
    minZ=minZ+float(ztr)
    maxX=maxX+float(xtr)
    maxY=maxY+float(ytr)
    maxZ=maxZ+float(ztr)
    print ("center_x = ", (maxX+minX)/2) 
    print ("center_y = ", (maxY+minY)/2)
    print ("center_z = ", (maxZ+minZ)/2)
    print ("")
    print ("size_x = ", maxX-minX)
    print ("size_y = ", maxY-minY)
    print ("size_z = ", maxZ-minZ)


    minBB = [
        LINEWIDTH, float(lineWidth),

        BEGIN, LINES,
        COLOR, float(r), float(g), float(b),

        VERTEX, minX, minY, minZ,   #1
        VERTEX, minX, minY, maxZ,   #2

        VERTEX, minX, maxY, minZ,   #3
        VERTEX, minX, maxY, maxZ,   #4

        VERTEX, maxX, minY, minZ,   #5
        VERTEX, maxX, minY, maxZ,   #6

        VERTEX, maxX, maxY, minZ,   #7
        VERTEX, maxX, maxY, maxZ,   #8


        VERTEX, minX, minY, minZ,   #1
        VERTEX, maxX, minY, minZ,   #5 

        VERTEX, minX, maxY, minZ,   #3
        VERTEX, maxX, maxY, minZ,   #7

        VERTEX, minX, maxY, maxZ,   #4
        VERTEX, maxX, maxY, maxZ,   #8

        VERTEX, minX, minY, maxZ,   #2
        VERTEX, maxX, minY, maxZ,   #6


        VERTEX, minX, minY, minZ,   #1
        VERTEX, minX, maxY, minZ,   #3

        VERTEX, maxX, minY, minZ,   #5 
        VERTEX, maxX, maxY, minZ,   #7

        VERTEX, minX, minY, maxZ,   #2
        VERTEX, minX, maxY, maxZ,   #4

        VERTEX, maxX, minY, maxZ,   #6
        VERTEX, maxX, maxY, maxZ,   #8

        END
    ]

    curName = "minBB_" + str(sel)+"_tr"

    cmd.load_cgo(minBB,curName)

cmd.extend('drawMinBoundingBoxtr', drawMinBoundingBoxtr)