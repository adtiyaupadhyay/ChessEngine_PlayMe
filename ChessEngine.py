"""
This Class is responsible for storing all the information about the current state of the chess game.Also
responsible for determining all the valid movesat the current state. It will also keep a move log
"""
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
        self.whiteToMove = True
        self.moveLog = []
    def makeMove(self , move):
        self.board[move.start_row][move.start_col] = "--";
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

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

    def getChessNotation(self):
        return self.getFileRank(self.start_row , self.start_col) + self.getFileRank(self.end_row , self.end_col)
    def getFileRank(self,r,c):
        return self.colsToFiles[c] + self.rowToRanks[r]
