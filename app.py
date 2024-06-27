from flask import Flask, render_template, request, redirect, url_for, jsonify
from tmdb import get_random_movies, get_movie_info
from database import movie_info as movie_collection
import os
import random 

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
    total_movies = movie_collection.count_documents({})
    
    return render_template('index.html', movies=movies, total_votes=total_votes, total_movies=total_movies)


@app.route('/compare')
def compare():
    if random.randint(1, 6) == 1:
        # Fetch a random movie with genres from the database
        local_movie = list(movie_collection.aggregate([
            { '$match': { 'genres': { '$exists': True, '$ne': [] } } },
            { '$sample': { 'size': 1 } }
        ]))

        if local_movie:
            local_movie = local_movie[0]
            genres = local_movie['genres']

            # Fetch another movie with at least one matching genre
            matching_genre_movies = list(movie_collection.aggregate([
                { '$match': { 'genres': { '$in': genres }, 'id': { '$ne': local_movie['id'] } } },
                { '$sample': { 'size': 1 } }
            ]))

            if matching_genre_movies:
                movie1 = get_movie_info(local_movie['id'])
                movie2 = get_movie_info(matching_genre_movies[0]['id'])

                return render_template('comparison.html', movie1=movie1, movie2=movie2)
    elif random.randint(1,5) == 2:
        local_movies = list(movie_collection.aggregate([{ '$sample': { 'size': 2 } }]))
        movie1 = get_movie_info(local_movies[0]['id'])
        movie2 = get_movie_info(local_movies[1]['id'])
        
    else:
        # Fallback to fetching random movies if genre-based selection fails
        random_movies = get_random_movies()
        movie1 = random_movies[0]
        movie2 = random_movies[1]
    
    if movie1 == movie2:
        return redirect(url_for('compare'))
    return render_template('comparison.html', movie1=movie1, movie2=movie2)


@app.route('/vote', methods=['POST'])
def vote():
    winner_id = request.form['winner_id']
    winner_title = request.form['winner_title']
    non_winner_id = request.form['non_winner_id']

    # Update vote count for the winner in MongoDB
    movie = movie_collection.find_one({'id': winner_id})
    non_winner = movie_collection.find_one({'id': non_winner_id})

    movie_info = get_movie_info(winner_id)
    if non_winner:
        non_winner_votes = non_winner.get('votes')
        add_votes = non_winner_votes//2
        if add_votes == 0:
            add_votes = 2


        if movie:
            if 'genres' not in movie:
                movie_collection.update_one(
                    {'id': winner_id},
                    {
                        '$inc': {'votes': add_votes},
                        '$set': {
                            'popularity': movie_info.get('popularity'),
                            'vote_average': movie_info.get('vote_average'),
                            'genres': movie_info.get('genres'),
                            'tagline': movie_info.get('tagline'),
                            'imdb_id': movie_info.get('imdb_id')
                        }
                    }
                )
            else:
                movie_collection.update_one(
                    {'id': winner_id},
                    {'$inc': {'votes': add_votes}}
                )
        else:
            movie_collection.insert_one({
                'id': winner_id,
                'title': winner_title,
                'votes': add_votes,
                'popularity': movie_info.get('popularity'),
                'vote_average': movie_info.get('vote_average'),
                'genres': movie_info.get('genres'),
                'tagline': movie_info.get('tagline'),
                'imdb_id':movie_info.get('imdb_id')
            })
    else:
        movie_collection.insert_one({
            'id': winner_id,
            'title': winner_title,
            'votes': 1,
            'popularity': movie_info.get('popularity'),
            'vote_average': movie_info.get('vote_average'),
            'genres': movie_info.get('genres'),
            'tagline': movie_info.get('tagline'),
            'imdb_id':movie_info.get('imdb_id')
        })

    return redirect(url_for('compare'))

@app.route('/skip', methods=['POST'])
def skip():
    data = request.get_json()
    movie_id_to_replace = data['movie_id']

    # Get the current movies being compared
    movie1 = get_movie_info(movie_id_to_replace)
    movie2 = None
    if 'movie2_id' in data:
        movie2 = get_movie_info(data['movie2_id'])

    # Get a new random movie to replace the one the user hasn't watched
    new_movie = None
    while new_movie is None or new_movie['id'] == movie_id_to_replace:
        new_movie = get_random_movies(1)[0]

    # Prepare response data
    response_data = {
        'success': True,
        'movie': new_movie,
        'other_movie_id': movie2['id'] if movie2 else None
    }

    return jsonify(response_data)


@app.route('/duplicates')
def cleanup_duplicates():
    # Aggregate movies by id and title to find duplicates
    pipeline = [
        {
            '$group': {
                '_id': {
                    'id': '$id',
                    'title': '$title'
                },
                'count': {'$sum': 1},
                'docs': {'$push': '$$ROOT'}
            }
        },
        {
            '$match': {
                'count': {'$gt': 1}
            }
        }
    ]
    
    duplicates = list(movie_collection.aggregate(pipeline))
    
    for duplicate in duplicates:
        movies = duplicate['docs']
        # Sort movies by votes in descending order
        movies.sort(key=lambda x: x['votes'], reverse=True)
        # Keep the movie with the highest votes
        movie_to_keep = movies[0]
        # Remove all other duplicates
        for movie in movies[1:]:
            movie_collection.delete_one({'_id': movie['_id']})
    
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
