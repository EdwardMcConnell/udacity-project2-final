# udacity-project2-final
Final submission for Udacity Full Stack Web Developer Nanodegree - Project 2

## Mission
Build a system that will allow for Swiss-System tournament pairing and scoring. Allow for Byes when an odd number of players register for the tournament. No player may receive a Bye more than once, unless all players have received a Bye. Tournament scoring should allow for tied matches and tiebreaks for overall leaders.

## Requirements
* Python 2.7.9
* PostgreSQL 9.3.6
* psql 9.3.6

## Testing
To run the tests, change to the project directory and run: 
```{Shell}
$: psql -f tournament.sql #create the database
$: python tournament_test.py #run the test suite
```
