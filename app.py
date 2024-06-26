from flask import Flask, render_template, request, redirect, url_for
from tmdb import get_random_movies
from database import movie_info as movie_collection
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Fetch movies from MongoDB sorted by votes in descending order
    movies = list(movie_collection.find().sort([('votes', -1)]))
    return render_template('index.html', movies=movies)

@app.route('/compare')
def compare():
    random_movies = get_random_movies()
    return render_template('comparison.html', movie1=random_movies[0], movie2=random_movies[1])

@app.route('/vote', methods=['POST'])
def vote():
    winner_id = request.form['winner_id']
    winner_title = request.form['winner_title']

    # Update vote count for the winner in MongoDB
    # Try to find the movie by ID, if not found, create a new document
    movie = movie_collection.find_one({'id': winner_id})
    if movie:
        movie_collection.update_one({'id': winner_id}, {'$inc': {'votes': 1}})
    else:
        movie_collection.insert_one({'id': winner_id, 'title': winner_title, 'votes': 1})

    return redirect(url_for('compare'))

@app.route('/skip', methods=['POST'])
def skip():
    return redirect(url_for('compare'))

if __name__ == '__main__':
    app.run(debug=True)