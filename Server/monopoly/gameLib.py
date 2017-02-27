import monopoly.redisLib as r
from monopoly.dice import double_roll
from monopoly import lobby

def pay(gID, uID, rec, amount):
    ret         = {}
    players     = r.getPlayers(gID)
    if players[uID]['money'] >= amount:
        players[uID]['money'] = players[uID]['money'] - amount
        for player in players:
            if player['public']['number'] == rec:
                player['money'] += amount
    else:
        ret['alert'] = "INSUFFICIENT FUNDS"
    return ret

def analysePos(gID, uID, board, pos):
    if board[pos]['category'] == 'property':
        if board[pos]['property']['status'] == "owned":
            ret = pay()
        elif board[pos]['property']['status'] == "mortgaged":
            pass
        else:
            ret                 = {}
            ret['options']      = ['BUY', 'AUCTION']
            player              = r.getPlayer(gID, uID)
            player['options']   += ["BUY"]
            player['options']   += ["AUCTION"]
            return ret
    else:
        ret             = {}
        ret['ignore']   = board[pos]['category']
    return ret


def updateLocation(gID, uID, roll):
    ret         = {}
    player      = r.getPlayer(gID, uID)
    board       = r.getBoard(gID)
    prevPos     = player['public']['position']
    newPos      = prevPos + roll['value']
    if newPos > 39:
        newPos = newPos - 40
    board[prevPos]['playersOn'].remove(player['number'])
    board[newPos]['playersOn'].append(player['number'])
    r.setBoard(gID, board)
    player['public']['position'] = newPos
    r.setPlayer(gID, uID, player)

    ret['board']    = board
    ret['player']   = player

    return ret

#******************************************************************************

def roll(json):
    gID                 = json['gID']
    uID                 = json['uID']
    roll                = double_roll()
    ret                 = updateLocation(gID, uID, roll)

    game                = r.getGame(gID)
    if roll['double']  == True:
        game['double']  = True
        r.setGame(gID, game)
    players             = r.getPlayer(gID, uID)
    player              = players[uID]
    player['options'].remove("ROLL")
    r.setPlayer(gID, uID, player)
    ret['player']       = player
    ret['players']      = {}
    for _uID in players:
        ret['players'][players[_uID]['public']['name']] = players[_uID]['public']
    return ret

def checkTurn(gID, uID):
    game    = r.getGame(gID)
    player  = r.getPlayer(gID, uID)
    if player['number'] == game['turn']:
        return True
    else:
        return False

def ping(json, isTurn):
    ret             = {}
    ret['game']     = r.getGame(json['gID'])
    ret['board']    = r.getBoard(json['gID'])
    ret['options']  = ["MORTGAGE", "TRADE"]

    players = r.getPlayers(json['gID'])

    if isTurn:
        ret['options'] += ["ROLL"]
        players[json['uID']]['options'] = ret['options']
        r.setPlayer(json['gID'], json['uID'], players[json['uID']])
    ret['player']   = players[json['uID']]

    ret['players']  = {}
    for _uID in players:
        ret['players'][players[_uID]['public']['name']] = players[_uID]['public']

    return ret


def game(json):
    isTurn = checkTurn(json['gID', json['uID']])
    if r.validateUID(json['gID'], json['uID']):
        if json['request'] == "PING":
            ret = ping(json, isTurn)
        elif isTurn and json['request'] in r.getPlayer(json['gID'], json['uID'])['options']:
            if json['request'] == "ROLL":
                ret = roll(json)
            # elif json['request'] == 'BUY':
            #     ret
            # elif json['request'] == 'AUCTION':
            #
            # elif json['request'] == 'MORTGAGE':
            #
            # elif json['request'] == 'TRADE':