# ChessEngine.py
import copy

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
        # map piece char -> move generator
        self.moveFunction = {'p':self.getPawnMoves, 'R':self.getRookMoves, 'K':self.getKingMoves,
                             'Q':self.getQueenMoves, 'B':self.getBishopMoves, 'N':self.getKnightMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False   # keep your original name
        self.pins = []
        self.checks = []
        self.enpassantPossible = ()  # (row, col) where en-passant is possible
        # CastlingRights(wks, wqs, bks, bqs)
        self.currentCastlingRights = CastlingRights(True, True, True, True)
        self.castlingRightsLogs = [copy.deepcopy(self.currentCastlingRights)]

        # position history for repetition detection (store a compact key)
        self.positionLog = [self._boardKey()]

    # ---------- helper: board key for repetition ----------
    def _boardKey(self):
        """
        Returns a compact immutable representation of the current position including:
        - board piece placement
        - side to move
        - castling rights
        - enpassant square
        This is sufficient for threefold repetition detection.
        """
        board_repr = tuple(tuple(row) for row in self.board)
        side = 'w' if self.whiteToMove else 'b'
        cr = (self.currentCastlingRights.wks, self.currentCastlingRights.wqs,
              self.currentCastlingRights.bks, self.currentCastlingRights.bqs)
        ep = self.enpassantPossible if self.enpassantPossible else None
        return (board_repr, side, cr, ep)

    def isThreefoldRepetition(self):
        """
        Return True if the current position has occurred three or more times in the game history.
        Uses the positionLog snapshots appended after each makeMove/undoMove.
        """
        key = self._boardKey()
        return self.positionLog.count(key) >= 3

    # --------------- make / undo moves ----------------
    def makeMove(self, move):
        # move piece
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.board[move.start_row][move.start_col] = "--"
        self.moveLog.append(move)

        # update king location
        if move.piece_moved == "wK":
            self.whiteKingLocation = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.blackKingLocation = (move.end_row, move.end_col)

        # handle castling rook movement
        if move.isCastleMove:
            # king-side
            if move.end_col == 6:
                self.board[move.end_row][5] = self.board[move.end_row][7]
                self.board[move.end_row][7] = "--"
            # queen-side
            elif move.end_col == 2:
                self.board[move.end_row][3] = self.board[move.end_row][0]
                self.board[move.end_row][0] = "--"

        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'

        # en-passant capture handling
        if move.isEnPassantMove:
            if move.piece_moved[0] == 'w':
                # white captured black pawn that was behind the target square
                self.board[move.end_row + 1][move.end_col] = "--"
            else:
                self.board[move.end_row - 1][move.end_col] = "--"

        # update en-passant possibility
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.enpassantPossible = ((move.start_row + move.end_row)//2, move.start_col)
        else:
            self.enpassantPossible = ()

        # update castling rights and save snapshot
        self.updateCastlingRights(move)
        self.castlingRightsLogs.append(copy.deepcopy(self.currentCastlingRights))

        # switch turn
        self.whiteToMove = not self.whiteToMove

        # append position key for repetition detection
        self.positionLog.append(self._boardKey())

    def undoMove(self):
        if len(self.moveLog) == 0:
            return
        move = self.moveLog.pop()
        self.board[move.start_row][move.start_col] = move.piece_moved
        self.board[move.end_row][move.end_col] = move.piece_captured
        self.whiteToMove = not self.whiteToMove

        # update kings
        if move.piece_moved == "wK":
            self.whiteKingLocation = (move.start_row, move.start_col)
        elif move.piece_moved == "bK":
            self.blackKingLocation = (move.start_row, move.start_col)

        # undo en-passant captured pawn
        if move.isEnPassantMove:
            # the captured pawn is placed behind the end square
            if move.piece_moved[0] == 'w':
                self.board[move.end_row + 1][move.end_col] = 'bp'
            else:
                self.board[move.end_row - 1][move.end_col] = 'wp'
            self.board[move.end_row][move.end_col] = "--"

        # undo castling rook movement
        if move.isCastleMove:
            if move.end_col == 6:
                self.board[move.end_row][7] = self.board[move.end_row][5]
                self.board[move.end_row][5] = "--"
            elif move.end_col == 2:
                self.board[move.end_row][0] = self.board[move.end_row][3]
                self.board[move.end_row][3] = "--"

        # restore en-passant possibility to previous move, if any
        if len(self.moveLog) > 0:
            prev = self.moveLog[-1]
            if prev.piece_moved[1] == 'p' and abs(prev.start_row - prev.end_row) == 2:
                self.enpassantPossible = ((prev.start_row + prev.end_row)//2, prev.start_col)
            else:
                self.enpassantPossible = ()
        else:
            self.enpassantPossible = ()

        # restore castling rights snapshot
        self.castlingRightsLogs.pop()
        if len(self.castlingRightsLogs) > 0:
            self.currentCastlingRights = copy.deepcopy(self.castlingRightsLogs[-1])
        else:
            self.currentCastlingRights = CastlingRights(True, True, True, True)

        # pop last position key
        if len(self.positionLog) > 0:
            self.positionLog.pop()

    # --------------- castling rights updates ----------------
    def updateCastlingRights(self, move):
        # if king moves: lose both castling rights for that color
        if move.piece_moved == "wK":
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.piece_moved == "bK":
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False

        # if rook moves: lose corresponding rook side
        if move.piece_moved == "wR":
            if move.start_row == 7 and move.start_col == 0:
                self.currentCastlingRights.wqs = False
            elif move.start_row == 7 and move.start_col == 7:
                self.currentCastlingRights.wks = False
        elif move.piece_moved == "bR":
            if move.start_row == 0 and move.start_col == 0:
                self.currentCastlingRights.bqs = False
            elif move.start_row == 0 and move.start_col == 7:
                self.currentCastlingRights.bks = False

        # if rook is captured, lose rights too
        if move.piece_captured == "wR":
            if move.end_row == 7 and move.end_col == 0:
                self.currentCastlingRights.wqs = False
            elif move.end_row == 7 and move.end_col == 7:
                self.currentCastlingRights.wks = False
        elif move.piece_captured == "bR":
            if move.end_row == 0 and move.end_col == 0:
                self.currentCastlingRights.bqs = False
            elif move.end_row == 0 and move.end_col == 7:
                self.currentCastlingRights.bks = False

    # --------------- move generation / validation ----------------
    def getValidMoves(self):
        """
        Generate all possible moves, then remove moves that leave mover's king in check
        """
        tempEnPassant = self.enpassantPossible
        tempCastRights = copy.deepcopy(self.currentCastlingRights)

        self.pins, self.checks = self.checkForPinsAndChecks()

        # generate all possible moves (including castles)
        moves = self.getAllPossibleMoves(include_castles=True)

        # filter out illegal moves by making them and checking king safety
        for i in range(len(moves)-1, -1, -1):
            move = moves[i]
            self.makeMove(move)
            # get mover color and corresponding king location AFTER the move
            mover_color = move.piece_moved[0]  # 'w' or 'b'
            if mover_color == 'w':
                king_r, king_c = self.whiteKingLocation
            else:
                king_r, king_c = self.blackKingLocation

            # if the mover's king is under attack now, move is illegal
            if self.squareUnderAttack(king_r, king_c, ally_color=mover_color):
                moves.remove(move)

            self.undoMove()

        # update checkMate / staleMate flags
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        # restore en passant and castling rights
        self.enpassantPossible = tempEnPassant
        self.currentCastlingRights = tempCastRights
        return moves

    def getAllPossibleMoves(self, include_castles=True):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    if piece == 'K':
                        self.getKingMoves(r, c, moves, include_castles)
                    else:
                        self.moveFunction[piece](r, c, moves)
        return moves

    # ------------ pins and checks detection ----------------
    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        if self.whiteToMove:
            enemy_color = "b"
            ally_color = "w"
            start_row, start_col = self.whiteKingLocation
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row, start_col = self.blackKingLocation

        directions = ((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()
            for i in range(1,8):
                end_row = start_row + d[0]*i
                end_col = start_col + d[1]*i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != 'K':
                        if possible_pin == ():
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:
                            break
                    elif end_piece[0] == enemy_color:
                        t = end_piece[1]
                        # rook/queen orthogonal, bishop/queen diagonal, pawn (one diag away), king (one away)
                        if (0 <= j <= 3 and t == 'R') or \
                           (4 <= j <= 7 and t == 'B') or \
                           (t == 'Q') or \
                           (i == 1 and t == 'K') or \
                           (i == 1 and t == 'p' and ((enemy_color == 'w' and 6 <= j <=7) or (enemy_color == 'b' and 4 <= j <=5))):
                            if possible_pin == ():
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:
                                pins.append(possible_pin)
                                break
                        else:
                            break
                else:
                    break

        # knight checks
        knight_moves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        for m in knight_moves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == 'N':
                    checks.append((end_row, end_col, m[0], m[1]))

        return pins, checks

    def inCheck(self):
        if self.whiteToMove:
            r,c = self.whiteKingLocation
            return self.squareUnderAttack(r,c, ally_color='w')
        else:
            r,c = self.blackKingLocation
            return self.squareUnderAttack(r,c, ally_color='b')

    # --------------- square under attack (non-recursive) ----------------
    def squareUnderAttack(self, r, c, ally_color=None):
        """
        Return True if square (r,c) is attacked by the opponent.
        ally_color: 'w' or 'b' - the side considered allied on that square.
        If ally_color is None, determine from self.whiteToMove (the side to move).
        This function scans rays, knight moves and pawn attacks. It does NOT call getAllPossibleMoves.
        """
        if ally_color is None:
            ally_color = 'w' if self.whiteToMove else 'b'
        enemy_color = 'w' if ally_color == 'b' else 'b'

        # directions: orthogonal then diagonal
        directions = ((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))
        for j, d in enumerate(directions):
            for i in range(1,8):
                end_row = r + d[0]*i
                end_col = c + d[1]*i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        continue
                    if end_piece[0] == ally_color:
                        # blocked by ally
                        break
                    # enemy piece found
                    p_type = end_piece[1]
                    # rook orthogonal (j 0..3), bishop diagonal (4..7), queen any, king one square, pawns special-case
                    if (0 <= j <= 3 and p_type == 'R') or \
                       (4 <= j <= 7 and p_type == 'B') or \
                       (p_type == 'Q') or \
                       (i == 1 and p_type == 'K'):
                        return True
                    else:
                        # enemy that doesn't attack in this direction blocks ray
                        break
                else:
                    break

        # knight attacks
        knight_moves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == 'N':
                    return True

        # pawn attacks (direction depends on pawn color)
        if ally_color == 'w':
            # black pawns attack from r-1
            if r - 1 >= 0:
                if c - 1 >= 0 and self.board[r-1][c-1] == 'bp':
                    return True
                if c + 1 < 8 and self.board[r-1][c+1] == 'bp':
                    return True
        else:
            # white pawns attack from r+1
            if r + 1 < 8:
                if c - 1 >= 0 and self.board[r+1][c-1] == 'wp':
                    return True
                if c + 1 < 8 and self.board[r+1][c+1] == 'wp':
                    return True

        return False

    # --------------- per-piece move generators ----------------
    def getPawnMoves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            # one-square forward
            if r-1 >= 0 and self.board[r-1][c] == "--":
                if not piece_pinned or pin_direction == (-1,0):
                    moves.append(Move((r,c),(r-1,c), self.board))
                    # two-square from starting rank
                    if r == 6 and self.board[r-2][c] == "--":
                        moves.append(Move((r,c),(r-2,c), self.board))
            # captures
            if c-1 >= 0:
                if not piece_pinned or pin_direction == (-1,-1):
                    if self.board[r-1][c-1][0] == 'b':
                        moves.append(Move((r,c),(r-1,c-1), self.board))
            if c+1 <= 7:
                if not piece_pinned or pin_direction == (-1,1):
                    if self.board[r-1][c+1][0] == 'b':
                        moves.append(Move((r,c),(r-1,c+1), self.board))
            # en-passant
            if self.enpassantPossible:
                if (r-1, c-1) == self.enpassantPossible:
                    if not piece_pinned or pin_direction == (-1,-1):
                        moves.append(Move((r,c),(r-1,c-1), self.board, isEnPassantMove=True))
                if (r-1, c+1) == self.enpassantPossible:
                    if not piece_pinned or pin_direction == (-1,1):
                        moves.append(Move((r,c),(r-1,c+1), self.board, isEnPassantMove=True))
        else:
            # black pawn moves downwards
            if r+1 <= 7 and self.board[r+1][c] == "--":
                if not piece_pinned or pin_direction == (1,0):
                    moves.append(Move((r,c),(r+1,c), self.board))
                    if r == 1 and self.board[r+2][c] == "--":
                        moves.append(Move((r,c),(r+2,c), self.board))
            if c-1 >= 0:
                if not piece_pinned or pin_direction == (1,-1):
                    if self.board[r+1][c-1][0] == 'w':
                        moves.append(Move((r,c),(r+1,c-1), self.board))
            if c+1 <= 7:
                if not piece_pinned or pin_direction == (1,1):
                    if self.board[r+1][c+1][0] == 'w':
                        moves.append(Move((r,c),(r+1,c+1), self.board))
            # en-passant
            if self.enpassantPossible:
                if (r+1, c-1) == self.enpassantPossible:
                    if not piece_pinned or pin_direction == (1,-1):
                        moves.append(Move((r,c),(r+1,c-1), self.board, isEnPassantMove=True))
                if (r+1, c+1) == self.enpassantPossible:
                    if not piece_pinned or pin_direction == (1,1):
                        moves.append(Move((r,c),(r+1,c+1), self.board, isEnPassantMove=True))

    def getRookMoves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1,0),(0,-1),(1,0),(0,1))
        enemy = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                end_row = r + d[0]*i
                end_col = c + d[1]*i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":
                            moves.append(Move((r,c),(end_row,end_col), self.board))
                        elif end_piece[0] == enemy:
                            moves.append(Move((r,c),(end_row,end_col), self.board))
                            break
                        else:
                            break
                    else:
                        break
                else:
                    break

    def getBishopMoves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1,-1),(-1,1),(1,-1),(1,1))
        enemy = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                end_row = r + d[0]*i
                end_col = c + d[1]*i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":
                            moves.append(Move((r,c),(end_row,end_col), self.board))
                        elif end_piece[0] == enemy:
                            moves.append(Move((r,c),(end_row,end_col), self.board))
                            break
                        else:
                            break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        piece_pinned = False
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
        if piece_pinned:
            return

        knight_moves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        ally = 'w' if self.whiteToMove else 'b'
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally:
                    moves.append(Move((r,c),(end_row,end_col), self.board))

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)

    def getKingMoves(self, r, c, moves, include_castles=True):
        # normal king moves (note: this does not yet check for moving into check)
        king_moves = ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
        ally = 'w' if self.whiteToMove else 'b'
        for m in king_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally:
                    # temporarily set king location to check square safety (avoid adding moves that move into attack)
                    orig_wk = self.whiteKingLocation
                    orig_bk = self.blackKingLocation
                    if ally == 'w':
                        self.whiteKingLocation = (end_row, end_col)
                    else:
                        self.blackKingLocation = (end_row, end_col)

                    if not self.squareUnderAttack(end_row, end_col, ally):
                        moves.append(Move((r,c),(end_row,end_col), self.board))

                    # restore kings
                    self.whiteKingLocation = orig_wk
                    self.blackKingLocation = orig_bk

        # castling moves
        if include_castles:
            # can't castle if currently in check
            if self.squareUnderAttack(r, c, ally):
                return
            # king-side castling
            if (ally == 'w' and self.currentCastlingRights.wks) or (ally == 'b' and self.currentCastlingRights.bks):
                # squares between king and rook must be empty and not under attack: f (c+1) and g (c+2)
                if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
                    if not self.squareUnderAttack(r, c+1, ally) and not self.squareUnderAttack(r, c+2, ally):
                        moves.append(Move((r,c),(r, c+2), self.board, isCastleMove=True))
            # queen-side castling
            if (ally == 'w' and self.currentCastlingRights.wqs) or (ally == 'b' and self.currentCastlingRights.bqs):
                # squares between king and rook must be empty: d (c-1), c (c-2), b (c-3)
                if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
                    if not self.squareUnderAttack(r, c-1, ally) and not self.squareUnderAttack(r, c-2, ally):
                        moves.append(Move((r,c),(r, c-2), self.board, isCastleMove=True))


class CastlingRights:
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks  # white king-side
        self.wqs = wqs  # white queen-side
        self.bks = bks  # black king-side
        self.bqs = bqs  # black queen-side


class Move:
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, isEnPassantMove=False, isCastleMove=False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.isPawnPromotion = False

        # pawn promotion
        if (self.piece_moved == 'wp' and self.end_row == 0) or (self.piece_moved == 'bp' and self.end_row == 7):
            self.isPawnPromotion = True

        # en-passant
        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove:
            # captured pawn sits behind destination
            if self.piece_moved[0] == 'w':
                self.piece_captured = 'bp'
            else:
                self.piece_captured = 'wp'

        # castle
        self.isCastleMove = isCastleMove

        # unique id
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    # original snake_case method (your UI called this in many places)
    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
