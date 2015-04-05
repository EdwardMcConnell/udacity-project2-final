-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

create database tournament;

-- When running this script via command line, after creating the tournament
-- database, I couldn't find any other way to get PostgreSQL to use the
-- correct database. I know this is not a SQL command and makes this SQL script
-- non-portable, but, then again, so does the SERIAL data type...
\connect tournament;

-- Table tournaments holds all tournaments with their create date (t_date)
create table tournaments (
 tournament_id serial PRIMARY KEY,
 t_date timestamp
);

-- Table players holds all players
create table players (
 player_id serial PRIMARY KEY,
 name text
);

-- Table registered_players holds all players registered in a given tournament
create table registered_players (
 tournament_id integer REFERENCES tournaments (tournament_id) ON DELETE CASCADE,
 player_id integer REFERENCES players (player_id) ON DELETE CASCADE,
 UNIQUE(tournament_id, player_id)
);

-- Table matches holds the results of all matches between two players or a player and a bye
create table matches (
 match_id serial PRIMARY KEY,
 tournament_id integer REFERENCES tournaments (tournament_id) ON DELETE CASCADE,
 round integer,
 player_1_id integer,
 player_2_id integer,
 player_1_score real,
 player_2_score real
);

-- The tournament_totals view will calculate the score for all players
create view tournament_totals as
(SELECT rp.tournament_id, 
 player_id,
 SUM(
  CASE WHEN player_1_id = player_id 
   THEN player_1_score 
  WHEN player_2_id = player_id 
   THEN player_2_score 
  ELSE 0 END) as score
 FROM registered_players as rp
 LEFT JOIN matches as m ON m.tournament_id = rp.tournament_id AND (m.player_1_id = rp.player_id OR m.player_2_id = rp.player_id)
 GROUP BY rp.tournament_id,
  rp.player_id
 ORDER BY score DESC
);

-- The leaderboard view will calculate the tiebreak points and total matches for all players
-- At scale I would presume that this method of leaderboard calculation
-- would be less than ideal
create view leaderboard as
(SELECT t.tournament_id,
  t.player_id,
  t.score,
  SUM(
   CASE WHEN player_1_id = t.player_id AND player_1_score > player_2_score THEN tt.score
   WHEN player_2_id = t.player_id AND player_2_score > player_1_score THEN tt.score
   ELSE 0 END
  ) as tiebreak,
  COUNT(matches.match_id) as total_matches
  FROM tournament_totals t
  LEFT JOIN matches ON matches.tournament_id = t.tournament_id AND (player_1_id = player_id OR player_2_id = player_id)
  LEFT JOIN tournament_totals tt ON matches.tournament_id = tt.tournament_id AND (CASE WHEN player_1_id = t.player_id THEN tt.player_id = player_2_id ELSE tt.player_id = player_1_id END)
  GROUP BY t.tournament_id,
   t.player_id, t.score
  ORDER BY t.score DESC, tiebreak DESC
);

