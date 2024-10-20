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

# TODO: Add IDs that are passed to the predict endpoint
def get_players():
    with hdfs_client.read('/data/players.csv') as f:
        # Read the file into a pandas dataframe
        df = pd.read_csv(f)
    return df['name'].tolist()

def get_clubs():
    with hdfs_client.read('/data/clubs.csv') as f:
        df = pd.read_csv(f)
    return df['name'].tolist()

@app.route('/')
def root():
    players = get_players()
    clubs = get_clubs()
    return render_template('index.html', players=players, clubs=clubs)

@app.route('/predict', methods=['POST'])
def predict():
    # TODO: Which one is being called?
    if request.is_json:
        data = request.get_json()
        print("JSON data:", data)
    else:
        data = request.form.to_dict()
        print("Form data:", data)
    
    player = data.get('player', '')
    team = data.get('team', '')
    
    print(f"Predicting for player: {player}, team: {team}")
    
    time.sleep(2)
    # TODO: Replace with actual prediction
    # Load the Random Forest model from file
    # model = joblib.load('random_forest_model.pkl')
    percentage = random.randint(0, 100)
    return f"{percentage}% \nfor {player} from {team}"

if __name__ == "__main__":
    app.run(debug=True)
