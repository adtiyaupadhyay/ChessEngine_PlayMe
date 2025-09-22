"""
Main Driver file - Responsible for handling user input and displaying the current gameState object
"""
import pygame as p
import os
from Chess import ChessEngine
from Chess import SmartMoveFinder

p.init()
WIDTH = HEIGHT = 600
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
colors = [p.Color(245, 245, 245) , p.Color(181, 136, 99)]


"""
Initialize a Global dictionary of images. This will be called exactly once in main 
"""
def load_Images():
    pieces = ["bp","bR","bN","bB","bQ","bK","wp","wR","wN","wB","wQ","wK"]
    for piece in pieces:
        image_path = os.path.join("Images", piece + ".png")
        image  = p.image.load(image_path)
        IMAGES[piece] = p.transform.smoothscale(image,(SQ_SIZE,SQ_SIZE))

def drawBoard(screen):
    colors = [p.Color(245, 245, 245) , p.Color(181, 136, 99)]
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

def drawGameState(screen, gs , validMoves , sqSelected):
     drawBoard(screen)
     highlightSquares(screen, gs, validMoves, sqSelected)
     drawPieces(screen, gs.board) # draw pieces on top of sqSelected


# Highlight square selected and moves for piece selected
def highlightSquares(screen , gs , validMoves , sqSelected):
    if sqSelected != ():
        r , c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            #highlight Square
            s = p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(150)
            s.fill(p.Color('blue'))
            screen.blit(s , (c*SQ_SIZE , r*SQ_SIZE))
            #highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.start_row == r and  move.start_col == c:
                    screen.blit(s,(move.end_col*SQ_SIZE , move.end_row*SQ_SIZE))


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

    dragging = False
    drag_piece = None
    drag_start_pos = None

    sq_Selected = ()
    player_clicks = []
    gameOver = False
    running = True


    playerOne = True #if human is playing with white, then this is True otherWise False
    playerTwo = False #if human is playing with black, then this is True otherwise False


    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #Mouse Handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
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
                        print(move.get_chess_notation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                #validMoves = gs.getValidMoves()
                                moveMade = True
                                sq_Selected = () #reset your click
                                player_clicks = []
                                break

            #key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    validMoves = gs.getValidMoves()
                    moveMade = True
                elif e.key == p.K_r:  # restart game
                    gs = ChessEngine.GameState()  # reset board
                    validMoves = gs.getValidMoves()
                    sq_Selected = ()
                    player_clicks = []
                    moveMade = False
        # Ai move finder
        if not gameOver and not humanTurn:
            AIMove = SmartMoveFinder.findBestMoveMinMax(gs , validMoves)
            if AIMove is None:
                AIMove = SmartMoveFinder.findRandomMove(validMoves)
            if AIMove is not None:
                gs.makeMove(AIMove)
                moveMade = True
            #animation(AIMove, screen, gs.board, clock)
        if moveMade:
            animation(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen , gs , validMoves , sq_Selected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                draw_text_line(screen , 'Black wins by CheckMate')
            else:
                draw_text_line(screen , 'White wins by CheckMate')
        elif gs.staleMate:
            gameOver = True
            draw_text_line(screen , 'Stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()
    p.quit()


def draw_text_line(screen, text):
    font = p.font.SysFont("Arial", 32, True, False)  # font name, size, bold, italic
    font.set_bold(True)
    text_object = font.render(text, True, p.Color("Black"))  # render text
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH//2 - text_object.get_width()//2,
                                                     HEIGHT//2 - text_object.get_height()//2)
    screen.blit(text_object, text_location)


#Animating a move
def animation(move , screen , board , clock):
    coords = []  # list of coordinates animation will move through
    dR = move.end_row - move.start_row
    dC = move.end_col - move.start_col
    framesPerSquare = 5  # frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare

    for frame in range(frameCount + 1):
        r = move.start_row + dR * frame / frameCount
        c = move.start_col + dC * frame / frameCount

        drawBoard(screen)
        drawPieces(screen, board)

        # erase the piece moved from its ending square
        color = colors[(move.end_row + move.end_col) % 2]
        endSquare = p.Rect(move.end_col * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        # draw captured piece
        if move.piece_captured != "--":
            screen.blit(IMAGES[move.piece_captured], endSquare)

        # draw moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


if __name__ ==  "__main__":
    main()
