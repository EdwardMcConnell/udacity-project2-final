#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import datetime
import sys

current_round = 0
current_tournament = False

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    global current_round
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM matches WHERE tournament_id = %s", (getTournament(),))
    conn.commit()
    conn.close()
    # Reset to start of tournament
    current_round = 0


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM players")
    cur.execute("DELETE FROM registered_players WHERE tournament_id = %s",(getTournament(),))
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(player_id) FROM registered_players WHERE tournament_id = %s GROUP BY tournament_id", (getTournament(),))
    players = cur.fetchone()
    conn.close()

    player_ct = 0
    if players != None:
        player_ct = players[0]
    
    return player_ct


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO players (name) VALUES (%s) RETURNING player_id", (name,))
    cur.execute("INSERT INTO registered_players (tournament_id, player_id) VALUES (%s, %s)", (getTournament(), cur.fetchone()[0]))
    conn.commit()
    conn.close()

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.player_id, p.name, l.score, l.total_matches 
        FROM leaderboard l 
        JOIN players p on p.player_id = l.player_id 
        WHERE tournament_id = %s AND p.player_id > 0
        ORDER BY score DESC, tiebreak DESC, p.player_id ASC
    """, (getTournament(),))

    players = [(row[0],row[1],row[2],int(row[3])) for row in cur.fetchall()]
    
    conn.close()
    return players



def reportMatch(winner, loser, tie = False):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    global current_round
    p1 = 1
    p2 = 0

    if winner == 0:
        # If the winner reported is a bye, then it 
        # must be recorded as the loser
        winner = loser
        loser = 0
    
    if loser == 0 and tie == True:
        # If this is a tie, and the loser is a bye, 
        # it should count as a whole point
        tie = False

    if tie == True:
        p1 = 0.5
        p2 = 0.5

    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO matches (tournament_id, round, player_1_id, player_2_id, player_1_score, player_2_score) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (getTournament(), current_round, winner, loser, p1, p2))
    conn.commit()
    conn.close()
 
 
def swissPairings(give_bye_to = False):
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    global current_round
    
    # Since we're using standings, there's no need to query the DB again
    leaders = playerStandings()

    pairs = []

    if give_bye_to != False:
        #move the person getting the bye to the end of the list of leaders
        idx = [leader[0] for leader in leaders].index(give_bye_to)
        leaders.insert(len(leaders)-1, leaders.pop(idx))
    
    for i in range(0,len(leaders)):
        if (i+1) % 2 == 0:
            ldr1 = leaders[i-1][:2]
            ldr2 = leaders[i][:2]
            pairs.append((ldr1 + ldr2))

    # Test for a Bye
    if len(leaders) % 2 > 0:
        # okay we should have a bye
        ldr1 = leaders[-1][:2]
        
        # But wait, has this player had a bye?
        # Also, make sure we aren't forcing a bye already
        if give_bye_to == False:
            no_byes = getPlayersWithNoBye()
            if ldr1[0] not in no_byes and len(no_byes) > 0:
                return swissPairings(no_byes[0])

        # Add the bye to the last person on the lise
        ldr2 = (0, 'Bye')
        pairs.append((ldr1 + ldr2))

    # Increment the current global round so that multiple round tournaments work
    current_round = current_round + 1

    return pairs

def createTournament():
    """Creates a tournament and returns its tournament_id"""

    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO tournaments (t_date) VALUES (%s) RETURNING tournament_id", (datetime.datetime.now(),))
    tournament_id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return tournament_id

def getTournament():
    """Gets the current tournament or will call to create a tournament if one doesn't exist"""
    global current_tournament, current_round
    if current_tournament == False:
        current_tournament = createTournament()
        current_round = 0

    return current_tournament

def getPlayersWithNoBye():
    """Gets all player ids for this tournament who have not received a bye in order by lowest rank"""

    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT rp.player_id FROM registered_players rp
        JOIN leaderboard l ON l.player_id = rp.player_id and l.tournament_id = rp.tournament_id
        LEFT JOIN matches m ON m.player_1_id = l.player_id AND m.player_2_id = 0 AND m.tournament_id = l.tournament_id
        WHERE l.tournament_id = %s AND m.player_1_id IS NULL
        ORDER BY score ASC, tiebreak ASC, player_id DESC
    """, (getTournament(),))
    no_byes = [row[0] for row in cur.fetchall()]
    conn.close()

    return no_byes

current_tournament = getTournament()
