# Implémentation des Bases de Donnnées Graphe NBA sous Neo4j

## Présentation du projet
Ce projet est centré sur la conception, la modélisation et l'implémentation d'une base de données dédiée au championnat de la NBA, développée au sein de l'environnement **Neo4j Desktop. À l'aide d'un script d'automatisation en Python, le projet assure le chargement et la transition de fichiers de données brutes (CSV) vers une structure de réseau sémantique dynamique.

## 1. Les Noeuds (Labels)
* `Player` : Représente un joueur de la NBA.
* `Team` : Représente une équipe.
* `Game` : Représente un match joué.
  `Coach` : Représente le coach principal.

## 2. Les Relations (Edges) et Propriétés
* `(:Player)-[:PLAYS_FOR {season: int}]->(:Team)`
* `(:Team)-[:COACHED_BY]->(:Coach)`
* `(:Team)-[:PLAYED_IN_GAME]->(:Game)`
* `(:Game)-[:HOME_TEAM]->(:Team)`
* `(:Game)-[:VISITOR_TEAM]->(:Team)`

---

## Configuration et Prérequis

### 1. Structure du Répertoire Local
nba-graph/
|__ nba.py  
|__ README.md
|__ .gitignore
|__ players.csv # dans https://www.kaggle.com/datasets/nathanlauga/players.csv
|__ teams.csv # dans https://www.kaggle.com/datasets/nathanlauga/teams.csv
|__ games.csv  # dans https://www.kaggle.com/datasets/nathanlauga/games.csv

### 2. Dépendances Python
Les bibliothèques requises doivent être installées en amont dans l'environnement virtuel
pip install pandas neo4j 

Utilisation et Injection:
  Demarrer votre instance de base de donnees locale sur Neo4j Desktop
  Assurer que l'URL de connexion (bolt://localhost:7687) et l'identifiant d'authentification concordent avec la configuration au debut du script nba.py.
  Depuis le terminal Linux, lancer: python3 nba.py


