#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *

def testDeleteMatches():
    deleteMatches()
    print "1. Old matches can be deleted."


def testDelete():
    deleteMatches()
    deletePlayers()
    print "2. Player records can be deleted."


def testCount():
    deleteMatches()
    deletePlayers()
    c = countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers() returns zero."


def testRegister():
    deleteMatches()
    deletePlayers()
    registerPlayer("Chandra Nalaar")
    c = countPlayers()
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterCountDelete():
    deleteMatches()
    deletePlayers()
    registerPlayer("Markov Chaney")
    registerPlayer("Joe Malik")
    registerPlayer("Mao Tsu-hsi")
    registerPlayer("Atlanta Hope")
    c = countPlayers()
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deletePlayers()
    c = countPlayers()
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches():
    deleteMatches()
    deletePlayers()
    registerPlayer("Melpomene Murray")
    registerPlayer("Randy Schwartz")
    standings = playerStandings()
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns.")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings

    # Modified the test to allow for tied scores. Since wins1 and wins2 are now floats, they are not == 0
    if matches1 != 0 or matches2 != 0 or int(wins1) != 0 or int(wins2) != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."


def testReportMatches():
    deleteMatches()
    deletePlayers()
    registerPlayer("Bruno Walton")
    registerPlayer("Boots O'Neal")
    registerPlayer("Cathy Burton")
    registerPlayer("Diane Grant")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    standings = playerStandings()
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    print "7. After a match, players have updated standings."


def testPairings():
    deleteMatches()
    deletePlayers()
    registerPlayer("Twilight Sparkle")
    registerPlayer("Fluttershy")
    registerPlayer("Applejack")
    registerPlayer("Pinkie Pie")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    pairings = swissPairings()
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."

def testSecondRoundPairings():
    deleteMatches()
    deletePlayers()
    registerPlayer("Twilight Sparkle")
    registerPlayer("Fluttershy")
    registerPlayer("Applejack")
    registerPlayer("Pinkie Pie")
    pairings = swissPairings()
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    reportMatch(pid1, pid2)
    reportMatch(pid3, pid4)
    
    #make next pairs
    pairings = swissPairings()
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    reportMatch(pid1, pid2, True)
    reportMatch(pid3, pid4)

    #Get standings after round 1
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]

    #Get third round pairings
    pairings = swissPairings()
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    
    correct_pairs = set([frozenset([id1, id2]), frozenset([id3, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After two matches, players with one win and one tie should be paired.")
    print "9. After two matches, players with one win and one tie are paired."

def testEightPlayerTourney():
    deleteMatches()
    deletePlayers()
    registerPlayer("Twilight Sparkle")
    registerPlayer("Fluttershy")
    registerPlayer("Applejack")
    registerPlayer("Pinkie Pie")
    registerPlayer("Bob")
    registerPlayer("Joe")
    registerPlayer("Anne")
    registerPlayer("Ned")

    pairings = swissPairings()
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4), (pid5, pname5, pid6, pname6), (pid7, pname7, pid8, pname8)] = pairings
    reportMatch(pid1, pid2)
    reportMatch(pid3, pid4)
    reportMatch(pid5, pid6, True)
    reportMatch(pid7, pid8)# Ned loses first Match
    
    pairings = swissPairings()
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4), (pid5, pname5, pid6, pname6), (pid7, pname7, pid8, pname8)] = pairings
    reportMatch(pid1, pid2, True)
    reportMatch(pid3, pid4, True)
    reportMatch(pid6, pid5, True)
    reportMatch(pid8, pid7)# Ned wins second match

    pairings = swissPairings()
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4), (pid5, pname5, pid6, pname6), (pid7, pname7, pid8, pname8)] = pairings
    reportMatch(pid2, pid1, True)
    reportMatch(pid4, pid3, True)
    reportMatch(pid6, pid5)# Ned wins third match
    reportMatch(pid8, pid7)

    pairings = swissPairings()
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4), (pid5, pname5, pid6, pname6), (pid7, pname7, pid8, pname8)] = pairings
    reportMatch(pid2, pid1)# Ned wins fourth match: 3 points
    reportMatch(pid4, pid3)
    reportMatch(pid6, pid5)
    reportMatch(pid8, pid7)

    #Get standings after round 1
    standings = playerStandings()

    winner = 'Ned'
    
    if standings[0][1] != winner:
        raise ValueError(
            "Expecting 8 player winner "+ winner +" got winner "+ standings[0][1])
    print "10. Got expected 8 player winner "+ winner


def testSevenPlayerTourney():
    deleteMatches()
    deletePlayers()
    registerPlayer("Twilight Sparkle")
    registerPlayer("Fluttershy")
    registerPlayer("Applejack")
    registerPlayer("Pinkie Pie")
    registerPlayer("Bob")
    registerPlayer("Joe")
    registerPlayer("Anne")
    
    pairings = swissPairings()
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4), (pid5, pname5, pid6, pname6), (pid7, pname7, pid8, pname8)] = pairings
    reportMatch(pid1, pid2)
    reportMatch(pid3, pid4)
    reportMatch(pid5, pid6, True)
    reportMatch(pid7, pid8)# Anne receives the Bye in the first round
    
    pairings = swissPairings()
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4), (pid5, pname5, pid6, pname6), (pid7, pname7, pid8, pname8)] = pairings
    reportMatch(pid1, pid2, True)
    reportMatch(pid3, pid4, True)
    reportMatch(pid6, pid5, True)
    reportMatch(pid8, pid7)# A Bye cannot win

    pairings = swissPairings()
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4), (pid5, pname5, pid6, pname6), (pid7, pname7, pid8, pname8)] = pairings
    reportMatch(pid2, pid1, True)
    reportMatch(pid4, pid3, True)
    reportMatch(pid6, pid5)
    reportMatch(pid8, pid7)

    pairings = swissPairings()
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4), (pid5, pname5, pid6, pname6), (pid7, pname7, pid8, pname8)] = pairings
    reportMatch(pid2, pid1, True)
    reportMatch(pid4, pid3)
    reportMatch(pid6, pid5)
    reportMatch(pid8, pid7)

    #Get standings after round 1
    standings = playerStandings()
    
    winner = 'Anne'
    
    if standings[0][1] != winner:
        raise ValueError(
            "Expecting 7 player winner "+ winner +" got winner "+ standings[0][1])
    print "11. Got expected 7 player winner "+ winner

if __name__ == '__main__':
    testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    testSecondRoundPairings()
    testEightPlayerTourney()
    testSevenPlayerTourney()
    print "Success!  All tests pass!"


