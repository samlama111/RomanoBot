import time
import random
import joblib
import pandas as pd

from flask import Flask, render_template, request, jsonify
from hdfs import InsecureClient

app = Flask(__name__, template_folder='./templates')

hdfs_client = InsecureClient(
    url='http://namenode:9870',
    user='root'
)

player_df, club_df = None, None

def load_data():
    global player_df, club_df
    with hdfs_client.read('/data/players.csv') as f:
        player_df = pd.read_csv(f)
    with hdfs_client.read('/data/clubs.csv') as f:
        club_df = pd.read_csv(f)
    return player_df, club_df


# TODO: Add IDs that are passed to the predict endpoint
def get_players():
    global player_df
    if player_df is None:
        player_df, _ = load_data()
    # Return a ID-name dictionary
    return dict(zip(player_df['player_id'], player_df['name']))

def get_clubs():
    global club_df
    if club_df is None:
        _, club_df = load_data()
    # Return a ID-name dictionary
    return dict(zip(club_df['club_id'], club_df['name']))

@app.route('/')
def root():
    players = get_players()
    clubs = get_clubs()
    return render_template('index.html', players=players, clubs=clubs)

@app.route('/search_players', methods=['POST'])
def search_players():
    query = request.form.get('player_search', '').lower()
    results = player_df[player_df['name'].str.lower().str.contains(query)].head(5)
    html = '<div class="search-results">'
    for _, player in results.iterrows():
        html += f'<div class="search-result-item" data-type="player" data-id="{player.name}">{player["name"]}</div>'
    html += '</div>'
    return html

@app.route('/search_teams', methods=['POST'])
def search_teams():
    query = request.form.get('team_search', '').lower()
    results = club_df[club_df['name'].str.lower().str.contains(query)].head(5)
    html = '<div class="search-results">'
    for _, team in results.iterrows():
        html += f'<div class="search-result-item" data-type="club" data-id="{team.name}">{team["name"]}</div>'
    html += '</div>'
    return html

@app.route('/predict', methods=['POST'])
def predict():
    global player_df, club_df

    data = request.form.to_dict()    
    player_id = data.get('player_id', '')
    club_id = data.get('club_id', '')
    
    try:
        player_id = int(player_id)
        club_id = int(club_id)
    except ValueError:
        return "Invalid player or club ID", 400

    try:
        player = player_df.loc[player_id]
        team = club_df.loc[club_id]
    except KeyError:
        return "Player or club not found", 404
    
    time.sleep(2)
    # TODO: Replace with actual prediction
    # Load the Random Forest model from file
    # model = joblib.load('random_forest_model.pkl')
    percentage = random.randint(0, 100)
    return f"{percentage}% \nfor {player['name']} to {team['name']}"

if __name__ == "__main__":
    app.run(debug=True)
