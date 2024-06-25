from flask import Flask, render_template, request, redirect, url_for
from tmdb import get_random_movies
from database import movie_info as movie_collection
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare')
def compare():
    random_movies = get_random_movies()
    return render_template('comparison.html', movie1=random_movies[0], movie2=random_movies[1])

@app.route('/vote', methods=['POST'])
def vote():
    winner_id = request.form['winner_id']
    
    # Update vote count for the winner in MongoDB
    # Try to find the movie by ID, if not found, create a new document
    movie_collection.update_one({'id': winner_id}, {'$inc': {'votes': 1}}, upsert=True)
    
    return redirect(url_for('compare'))

if __name__ == '__main__':
    app.run(debug=True)
