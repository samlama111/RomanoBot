from flask import Flask, render_template
import time
import random

app = Flask(__name__, template_folder='./templates')

def get_players():
    return ["Kilian Mbappe", "Lionel Messi", "Cristiano Ronaldo", "Antoine Griezmann", "Neymar Jr", "Karim Benzema", "Mohamed Salah", "Kevin De Bruyne", "Harry Kane", "Robert Lewandowski"]

def get_clubs():
    return ["PSG", "FC Barcelona", "Juventus", "Atletico Madrid", "Real Madrid", "FC Liverpool", "Manchester City", "Tottenham", "FC Bayern Munich"]

@app.route('/')
def root():
    players = get_players()
    clubs = get_clubs()
    return render_template('index.html', players=players, clubs=clubs)

@app.route('/predict')
def example():
    time.sleep(2)
    percentage = random.randint(0, 100)
    return f"{percentage}%"

if __name__ == "__main__":
    app.run(debug=True)