import joblib
import pandas as pd
import numpy as np
import sklearn
import hashlib

from flask import Flask, render_template, request, jsonify
from hdfs import InsecureClient

app = Flask(__name__, template_folder="./templates")

hdfs_client = InsecureClient(url="http://namenode:9870", user="root")

player_df, club_df = None, None

model = joblib.load("random_forest_model.pkl")


def load_data():
    global player_df, club_df, competitions_df
    with hdfs_client.read("/data/players.csv") as f:
        player_df = pd.read_csv(f)
    with hdfs_client.read("/data/clubs.csv") as f:
        club_df = pd.read_csv(f)
    with hdfs_client.read("/data/competitions.csv") as f:
        competitions_df = pd.read_csv(f)
    return player_df, club_df


def get_players():
    global player_df
    if player_df is None:
        player_df, _ = load_data()
    # Return a ID-name dictionary
    return dict(zip(player_df["player_id"], player_df["name"]))


def get_clubs():
    global club_df
    if club_df is None:
        _, club_df = load_data()
    # Return a ID-name dictionary
    return dict(zip(club_df["club_id"], club_df["name"]))


def create_embedding(item, size=10):
    # Create a hash of the item
    hash_object = hashlib.md5(str(item).encode())
    hash_hex = hash_object.hexdigest()

    # Convert the hash to a list of floats
    return [int(hash_hex[i : i + 2], 16) / 255.0 for i in range(0, size * 2, 2)]


def prepare_player_data(player_data):
    global competitions_df
    prepared_data = {}

    # Numeric fields
    prepared_data["player_id"] = player_data["player_id"]
    prepared_data["from_club_id"] = player_data["current_club_id"]
    prepared_data["market_value_in_eur"] = player_data["market_value_in_eur"]
    prepared_data["highest_market_value_in_eur"] = player_data[
        "highest_market_value_in_eur"
    ]

    # Date fields
    prepared_data["transfer_season_end_year"] = 2026
    prepared_data["contract_expiration_date"] = pd.to_datetime(
        player_data["contract_expiration_date"]
    ).year

    print(prepared_data)

    # Embedding fields
    embedding_fields = [
        "from_country_name",
        "to_country_name",
        "country_of_citizenship",
        "position",
        "sub_position",
    ]

    for field in embedding_fields:
        if field == "from_country_name":
            # Get the competition_id for the current club
            club_competition_id = player_data["current_club_domestic_competition_id"]
            # Find the country name for the current club's competition
            club_country = competitions_df[
                competitions_df["competition_id"] == club_competition_id
            ]["country_name"].values
            value = club_country[0] if len(club_country) > 0 else "Unknown"
        elif field == "to_country_name":
            value = "Unknown"  # This will be replaced with the target club's country in the prediction function
        else:
            value = player_data[field]

        embedding = create_embedding(value)
        for i, emb_value in enumerate(embedding):
            prepared_data[f"{field}_emb_{i}"] = emb_value

    return prepared_data


def predict_transfer_probability(player_data, target_club_id, model, feature_names):
    # Prepare the player data
    prepared_data = prepare_player_data(player_data)
    print(prepared_data)

    # Add the target club's country embedding
    target_club_competition_id = club_df[club_df["club_id"] == target_club_id][
        "domestic_competition_id"
    ].values[0]
    target_club_country = competitions_df[
        competitions_df["competition_id"] == target_club_competition_id
    ]["country_name"].values[0]
    target_country_embedding = create_embedding(target_club_country)
    for i, emb_value in enumerate(target_country_embedding):
        prepared_data[f"to_country_name_emb_{i}"] = emb_value

    # Ensure all required features are present
    for feature in feature_names:
        if feature not in prepared_data:
            raise ValueError(f"Missing feature: {feature}")

    # Create a DataFrame with a single row
    input_df = pd.DataFrame([prepared_data], columns=feature_names)

    # Get probabilities for all classes
    probabilities = model.predict_proba(input_df)[0]

    # Find the index of the target club ID in the classes
    target_index = np.where(model.classes_ == target_club_id)[0]

    # Return the probability for the target club
    if len(target_index) > 0:
        return probabilities[target_index[0]]
    else:
        return 0.0  # Return 0 if the club ID is not in the training data


@app.route("/")
def root():
    players = get_players()
    clubs = get_clubs()
    return render_template("index.html", players=players, clubs=clubs)


@app.route("/search_players", methods=["POST"])
def search_players():
    query = request.form.get("player_search", "").lower()
    results = player_df[player_df["name"].str.lower().str.contains(query)].head(5)
    html = '<div class="search-results">'
    for _, player in results.iterrows():
        html += f'<div class="search-result-item" data-type="player" data-id="{player.name}">{player["name"]}</div>'
    html += "</div>"
    return html


@app.route("/search_teams", methods=["POST"])
def search_teams():
    query = request.form.get("team_search", "").lower()
    results = club_df[club_df["name"].str.lower().str.contains(query)].head(5)
    html = '<div class="search-results">'
    for _, team in results.iterrows():
        html += f'<div class="search-result-item" data-type="club" data-id="{team.name}">{team["name"]}</div>'
    html += "</div>"
    return html


@app.route("/predict", methods=["POST"])
def predict():
    global player_df, club_df

    data = request.form.to_dict()
    player_id = data.get("player_id", "")
    club_id = data.get("club_id", "")

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

    print(player)

    train_features = [
        "player_id",
        "from_club_id",
        "market_value_in_eur",
        "transfer_season_end_year",
        "contract_expiration_date",
        "highest_market_value_in_eur",
    ]

    # Add embedding columns
    for col in [
        "from_country_name",
        "to_country_name",
        "country_of_citizenship",
        "position",
        "sub_position",
    ]:
        train_features.extend([f"{col}_emb_{i}" for i in range(10)])

    # Make a prediction
    percentage = predict_transfer_probability(player, club_id, model, train_features)
    print(percentage)
    return f"{percentage:.2%}% \nfor {player['name']} to {team['name']}"


if __name__ == "__main__":
    app.run(debug=True)
