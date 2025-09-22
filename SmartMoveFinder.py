# SmartMoveFinder.py
import random

# piece values
pieceScore = {'p': 1, 'B': 3, 'N': 3, 'K': 0, 'Q': 10, 'R': 5}
checkMate = 1000
staleMate = 0
DEPTH = 2  # default search depth (adjust as you like)


def findRandomMove(validMoves):
    return random.choice(validMoves)


def scoreMaterial(board):
    """Score based on material only. Positive favors white, negative favors black."""
    score = 0
    for row in board:
        for square in row:
            if square == '--':
                continue
            color = square[0]
            p_type = square[1]
            val = pieceScore.get(p_type, 0)
            if color == 'w':
                score += val
            else:
                score -= val
    return score


def scoreBoard(gs):
    """
    Evaluate the current game state.
    Positive => advantage for White; Negative => advantage for Black.
    NOTE: Uses the GameState attribute name `staleMate` (capital M) to match your GameState.
    """
    if gs.checkMate:
        # If current side to move is in checkmate then the *opponent* just delivered mate.
        # So if it's white's turn and checkMate True => white is checkmated => return -checkMate
        if gs.whiteToMove:
            return -checkMate
        else:
            return checkMate
    if gs.staleMate:
        return staleMate
    # Otherwise return material score
    return scoreMaterial(gs.board)


def minimax(gs, depth):
    """
    Simple minimax that returns evaluation score.
    Uses gs.whiteToMove to decide maximizing or minimizing at each node.
    """
    if depth == 0:
        return scoreBoard(gs)

    moves = gs.getValidMoves()
    if not moves:
        # no legal moves: scoreBoard already handles checkmate/stalemate
        return scoreBoard(gs)

    if gs.whiteToMove:
        maxScore = -float('inf')
        for move in moves:
            gs.makeMove(move)
            score = minimax(gs, depth - 1)
            gs.undoMove()
            if score > maxScore:
                maxScore = score
        return maxScore
    else:
        minScore = float('inf')
        for move in moves:
            gs.makeMove(move)
            score = minimax(gs, depth - 1)
            gs.undoMove()
            if score < minScore:
                minScore = score
        return minScore


def findBestMoveMinMax(gs, validMoves, depth=DEPTH):
    """
    Root-level function to pick best move using minimax (fixed depth).
    Returns the best Move object (or None if no moves).
    """
    if not validMoves:
        return None

    isWhiteToMove = gs.whiteToMove
    bestMove = None

    if isWhiteToMove:
        bestScore = -float('inf')
        for move in validMoves:
            gs.makeMove(move)
            score = minimax(gs, depth - 1)
            gs.undoMove()
            # prefer higher score for white
            if score > bestScore or (score == bestScore and random.random() < 0.5):
                bestScore = score
                bestMove = move
    else:
        bestScore = float('inf')
        for move in validMoves:
            gs.makeMove(move)
            score = minimax(gs, depth - 1)
            gs.undoMove()
            # prefer lower score for black
            if score < bestScore or (score == bestScore and random.random() < 0.5):
                bestScore = score
                bestMove = move

    return bestMove


# optional helper kept for backward compatibility with older code that calls this name
def findBestMove(gs, validMoves):
    """Greedy 1-ply — select the move that gives best immediate material score."""
    bestScore = -float('inf') if gs.whiteToMove else float('inf')
    bestMove = None
    for move in validMoves:
        gs.makeMove(move)
        score = scoreBoard(gs)
        gs.undoMove()
        if gs.whiteToMove:
            # after makeMove, gs.whiteToMove toggles; we want the score after the move
            if score > bestScore:
                bestScore = score
                bestMove = move
        else:
            if score < bestScore:
                bestScore = score
                bestMove = move
    return bestMove

