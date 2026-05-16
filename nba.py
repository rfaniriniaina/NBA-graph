import pandas as pd
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "Zaravola31")

def load_clean_data():
    df_players = pd.read_csv('players.csv')
    df_players['TEAM_ID'] = df_players['TEAM_ID'].astype(int)
    df_players['PLAYER_ID'] = df_players['PLAYER_ID'].astype(int)
    df_players['SEASON'] = df_players['SEASON'].astype(int)

    """chargement de teams.csv"""
    df_teams = pd.read_csv('teams.csv')
    df_teams['TEAM_ID'] = df_teams['TEAM_ID'].astype(int)

    """chargement de games.csv"""
    df_games = pd.read_csv('games.csv')
    df_games['GAME_ID'] = df_games['GAME_ID'].astype(int)
    df_games['HOME_TEAM_ID'] = df_games['HOME_TEAM_ID'].astype(int)
    df_games['VISITOR_TEAM_ID'] = df_games['VISITOR_TEAM_ID'].astype(int)
    df_games['SEASON'] = df_games['SEASON'].astype(int)

    """conversion des colonnes de stats en types numeriques"""
    numeric_cols = ['PTS_home', 'FG_PCT_home', 'FT_PCT_home', 'FG3_PCT_home', 'AST_home', 'REB_home',
                    'PTS_away', 'FG_PCT_away']
    for col in numeric_cols:
        if col in df_games.columns:
            df_games[col] = pd.to_numeric(df_games[col], errors='coerce').fillna(0.0)
    
    return df_players, df_teams, df_games

def create_constraints(session):
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Player) REQUIRE p.id IS UNIQUE ")    
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (t:Team) REQUIRE t.id IS UNIQUE")
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (g:Game) REQUIRE g.id IS UNIQUE")
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Coach) REQUIRE c.name IS UNIQUE")

def execute_import(tx, df_players, df_teams, df_games):
    teams_records = df_teams.to_dict(orient='records')
    cypher_teams = """
    UNWIND $rows AS row
    MERGE (t:Team {id: toInteger(row.TEAM_ID)})
    SET t.league_id = row.teaLEAGUE_ID,
        t.abbreviation = row.ABBREVIATION,
        t.nickname = row.NICKNAME,
        t.city = row.CITY,
        t.arena = row.ARENA, 
        t.arena_capacity = toInteger(row.ARENACAPACITY),
        t.owner = row.OWNER,
        t.general_manager = row.GENERALMANAGER,
        t.d_league_affiliation = row.DLEAGUEAFFILIATION,
        t.year_founded = toInteger(row.YEARFOUNDER)

    WITH t,row
    WHERE row.HEADCOACH <> ''
    MERGE (c:Coach {name: row.HEADCOACH})
    MERGE (t)-[:COACHED_BY]->(c)
    """
    tx.run(cypher_teams, rows=teams_records)

    #import des joueurs et relations avec l'equipe
    players_records = df_players.to_dict(orient='records')
    cypher_players = """
    UNWIND $rows AS row
    MERGE (p:Player {id: toInteger(row.PLAYER_ID)})
    SET p.name = row.PLAYER_NAME

    WITH p, row
    MATCH (t:Team {id: row.TEAM_ID})
    MERGE (p)-[r:PLAYS_FOR]->(t)
    SET r.season = row.SEASON
    """
    tx.run(cypher_players, rows=players_records)

    #import des matchs et statistiques
    games_records = df_games.to_dict(orient='records')
    cypher_games = """
    UNWIND $rows AS row
    MERGE (g:Game {id: toInteger(row.GAME_ID)})
    SET g.date = row.GAME_DATE_EST,
        g.status = row.GAME_STATUS_TEXT,
        g.season = toInteger(row.SEASON)

    WITH g, row
    MATCH (home:Team {id: toInteger(row.HOME_TEAM_ID)})
    MATCH (away:Team {id: toInteger(row.VISITOR_TEAM_ID)})
    MERGE (g)-[:HOME_TEAM]->(home)
    MERGE (g)-[:VISITOR_TEAM]->(away)
    
    //stockage des performances d'equipe
    MERGE (home)-[rh:PLAYED_IN_GAME]->(g)
    SET rh.points = row.PTS_home,
        rh.field_goal_pct = row.FG_PCT_home,
        rh.free_throw_pct = row.FT_PCT_home,
        rh.three_point_pct = row.FG3_PCT_home,
        rh.assists = row.AST_home,
        rh.rebounds = row.REB_home
    
    MERGE (away)-[ra:PLAYED_IN_GAME]->(g)
    SET ra.points = row.PTS_away,
        ra.field_goal_pct = row.FG_PCT_away
    """
    tx.run(cypher_games, rows=games_records)

if __name__ == "__main__":
    driver = GraphDatabase.driver(URI, auth=AUTH)
    df_players, df_teams, df_games = load_clean_data()

    with driver.session() as session:
        create_constraints(session)
        session.execute_write(execute_import, df_players, df_teams, df_games)
    
    driver.close()









































































































































































































































































