from flask import Flask, render_template, request, redirect, url_for
from tmdb import get_random_movies
from database import movie_info as movie_collection
import os

app = Flask(__name__)

@app.route('/')
def index():
    movies = movie_collection.find().sort('votes', -1)
    total_votes = movie_collection.aggregate([
        {
            '$group': {
                '_id': None,
                'totalVotes': {'$sum': '$votes'}
            }
        }
    ]).next()['totalVotes']
    return render_template('index.html', movies=movies, total_votes=total_votes)





@app.route('/compare')
def compare():
    random_movies = get_random_movies()
    return render_template('comparison.html', movie1=random_movies[0], movie2=random_movies[1])

@app.route('/vote', methods=['POST'])
def vote():
    winner_id = request.form['winner_id']
    winner_title = request.form['winner_title']
    non_winner_id = request.form['non_winner_id']

    # Update vote count for the winner in MongoDB
    movie = movie_collection.find_one({'id': winner_id})
    non_winner = movie_collection.find_one({'id': non_winner_id})
    if non_winner:
        non_winner_votes = non_winner.get('votes')
        add_votes = non_winner_votes//2
        if add_votes == 0:
            add_votes = 1
        if movie:
            movie_collection.update_one({'id': winner_id}, {'$inc': {'votes': add_votes}})
        else:
            movie_collection.insert_one({'id': winner_id, 'title': winner_title, 'votes': add_votes})
    else:
        movie_collection.insert_one({'id': winner_id, 'title': winner_title, 'votes': 1})

    return redirect(url_for('compare'))

@app.route('/skip', methods=['POST'])
def skip():
    return redirect(url_for('compare'))

if __name__ == '__main__':
    app.run(debug=True)
