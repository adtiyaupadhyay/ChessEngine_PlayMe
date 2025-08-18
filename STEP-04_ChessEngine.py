"""
This Class is responsible for storing all the information about the current state of the chess game.Also
responsible for determining all the valid movesat the current state. It will also keep a move log
"""
from operator import truediv

from fontTools.varLib.models import piecewiseLinearMap
from six import moves


class GameState():
    def __init__(self):
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"],
        ]
        self.moveFunction = {'p':self.getPawnMoves , 'R':self.getRookMoves , 'K':self.getKingMoves ,
                             'Q':self.getQueenMoves , 'B':self.getBishopMoves , 'N':self.getKnightMoves,
                             }
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkMate = False
        self.stalemate = False

    def makeMove(self , move):
        self.board[move.start_row][move.start_col] = "--";
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

        if move.piece_moved == 'wK':
            self.whiteKingLocation = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.blackKingLocation = (move.end_row, move.end_col)

    def undoMove(self):
        if len(self.moveLog) != 0:
            move =  self.moveLog.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.whiteToMove = not self.whiteToMove #switch turn to black

            if move.piece_moved == 'wK':
                self.whiteKingLocation = (move.start_row , move.start_col)
            elif move.piece_moved == 'bK':
                self.blackKingLocation = (move.start_row , move.start_col)

    #All moves considering check
    def getValidMoves(self):
        '''
        Naive Algrithm..................................................
           1.generate all possible moves
           2.for each move,make the move
           3.generate all opponents moves
           4.for each opponent moves, see if they attack the king
           5.if they do attack your king, then it's not a valid moves
        '''
        ''' NAIVE ALGORITHM IMPLEMENTATION'''
        moves = self.getAllPossibleMoves()

        #whenever iterate try to do it backward.....
        for i in range(len(moves)-1 , -1 , -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        if len(moves) == 0:
            if self.inCheck():
                self.stalemate = True
            else:
                self.stalemate = True
        else:
            self.checkMate = False
            self.stalemate = False

        return moves

    #Determine if current player is in check
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0] , self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0] , self.blackKingLocation[1])


    #Determine if the square is under attack
    def squareUnderAttack(self,r,c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.end_row == r and move.end_col == c: #Square is under attack
                return True
        return False


    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board)):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    #Calls appropriate move function based on move type
                    self.moveFunction[piece](r,c,moves)
        return moves

    def getPawnMoves(self , r  , c , moves):
        if self.whiteToMove:
            if r-1 >= 0 and self.board[r - 1][c] == "--":  # move one square forward
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":  # move two squares from start
                    moves.append(Move((r, c), (r - 2, c), self.board))
            # captures
            if r-1 >= 0 and c - 1 >= 0:  # capture to the left
                if self.board[r - 1][c - 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
            if r-1 >= 0 and c + 1 <= 7:  # capture to the right
                if self.board[r - 1][c + 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
        else:
            if r+1 <= 7 and self.board[r + 1][c] == "--":  # move one square forward
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # move two squares from start
                    moves.append(Move((r, c), (r + 2, c), self.board))
            # captures
            if r+1 <= 7 and c - 1 >= 0:  # capture to the left
                if self.board[r + 1][c - 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if r+1 <= 7 and  c + 1 <= 7:  # capture to the right
                if self.board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))

            #Pawn Promotion will be done later

    def getRookMoves(self , r , c , moves):
        directions = ((-1,0) , (0,-1) , (1,0) , (0,1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--': # Empty space is available so move
                        moves.append(Move((r,c),(endRow,endCol) , self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r,c),(endRow,endCol) , self.board))
                        break
                    else: # Friendly piece
                        break
                else: # Off board
                    break

    def getBishopMoves(self , r , c , moves):
        directions = ((1,1) , (-1,-1) , (1,-1) , (-1,1)) # 4 diagonals
        enemyPiece = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':
                        moves.append(Move((r,c) ,(endRow,endCol) , self.board))
                    elif endPiece[0] == enemyPiece:
                        moves.append(Move((r,c),(endRow,endCol) , self.board))
                        break
                    else: # Friendly Piece
                        break
                else: #Off Board
                    break

    def getKnightMoves(self , r , c , moves):
        knightMoves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,1),(2,-1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece == '--' or endPiece[0] != allyColor:    #endPiece[0] != allyColor :
                    moves.append(Move((r,c) , (endRow,endCol) , self.board))


    def getQueenMoves(self , r , c , moves):
        self.getRookMoves(r , c , moves)
        self.getBishopMoves(r , c , moves)


    def getKingMoves(self , r , c , moves):
        kingMoves = ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece == '--' or endPiece[0] != allyColor:
                    moves.append(Move((r,c) , (endRow,endCol) , self.board))




class Move():
    rankToRows = {"1":7 , "2":6 , "3":5 , "4":4 ,
                  "5":3 , "6":2 , "7":1 , "8":0}
    rowToRanks = {v : k for k, v in rankToRows.items()}
    filesToCols = {"a":0 , "b":1 , "c":2 , "d":3,
                   "e":4 , "f":5 , "g":6 , "h":7}
    colsToFiles = {v : k for k, v in filesToCols.items()}
    def __init__(self,start_sq , end_sq , board):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.moveId = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
    def __eq__(self, other):
        if isinstance(other,Move):
            return self.moveId == other.moveId
        return False


    def getChessNotation(self):
        return self.getFileRank(self.start_row , self.start_col) + self.getFileRank(self.end_row , self.end_col)
    def getFileRank(self,r,c):
        return self.colsToFiles[c] + self.rowToRanks[r]
