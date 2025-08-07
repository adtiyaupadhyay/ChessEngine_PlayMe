"""
Main Driver file - Responsible for handling user input and displaying the current gameState object
"""

from operator import truediv

import pygame as p
import os

from jupyterlab.semver import valid
from nbformat.validator import get_validator

from Chess import ChessEngine

p.init()
WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

"""
Initialize a Global dictionary of images. This will be called exactly once in main 
"""
def load_Images():
    pieces = ["bp","bR","bN","bB","bQ","bK","wp","wR","wN","wB","wQ","wK"]
    for piece in pieces:
        image_path = os.path.join("Images", piece + ".png")
        image  = p.image.load(image_path)
        IMAGES[piece] = p.transform.scale(image,(SQ_SIZE,SQ_SIZE))

def drawBoard(screen):
    colors = [p.Color("gray") , p.Color("blue")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen , color , p.Rect(c*SQ_SIZE , r*SQ_SIZE ,SQ_SIZE , SQ_SIZE ))

def drawPieces(screen , board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece] , p.Rect(c*SQ_SIZE , r*SQ_SIZE , SQ_SIZE , SQ_SIZE))

def drawGameState(screen, gs):
     drawBoard(screen)
     drawPieces(screen, gs.board)

"""
The main driver for our code. This will handle user input and updating the graphics
"""
def main():
    screen = p.display.set_mode((WIDTH , HEIGHT))
    p.display.set_caption("Chess")
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False

    load_Images() #only do this once before the while loop
    sq_Selected = ()
    player_clicks = []
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #Mouse Handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if(sq_Selected == (row , col)): #User clicked same square twice
                    sq_Selected = ()
                    player_clicks = []
                else:
                    sq_Selected = (row , col)
                    player_clicks.append(sq_Selected)
                if len(player_clicks) == 2:
                    move = ChessEngine.Move(player_clicks[0],player_clicks[1],gs.board)
                    print(move.getChessNotation())
                    if move in validMoves:
                        gs.makeMove(move)
                        validMoves = gs.getValidMoves()
                        moveMade = True
                        sq_Selected = ()
                        player_clicks = []
                    else:
                        player_clicks = [sq_Selected]
            #key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    validMoves = gs.getValidMoves()
                    moveMade = True

        drawGameState(screen , gs)
        clock.tick(MAX_FPS)
        p.display.flip()
    p.quit()


if __name__ ==  "__main__":
    main()
