import os
import requests
import random

TMDB_API_KEY = os.getenv('TMDB_API_KEY')
BASE_URL = 'https://api.themoviedb.org/3'

def get_configuration():
    url = f'{BASE_URL}/configuration'
    params = {
        'api_key': TMDB_API_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def get_movie_details(movie_id):
    url = f'{BASE_URL}/movie/{movie_id}'
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US'
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def get_popular_movies(page=1):
    url = f'{BASE_URL}/movie/popular'
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US',
        'page': page
    }
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an error for bad status codes
    return response.json()

def get_movie_info(movie_id):
    config = get_configuration()
    image_base_url = config['images']['secure_base_url']
    poster_size = 'original'

    movie_details = get_movie_details(movie_id)
    movie_info = {
        'id': movie_details['id'],
        'title': movie_details['title'],
        'overview': movie_details['overview'],
        'popularity': movie_details['popularity'],
        'vote_average': movie_details['vote_average'],
        'genres': [genre['name'] for genre in movie_details['genres']],
        'imdb_id': movie_details['imdb_id'],
        'poster_path': f"{image_base_url}{poster_size}{movie_details['poster_path']}",
        'backdrop_path': f"{image_base_url}original{movie_details['backdrop_path']}",
        'tagline': movie_details['tagline']
    }
    return movie_info

def get_random_movies(num_movies=2):
    popular_movies = get_popular_movies()
    movies = popular_movies['results']
    random_movies = random.sample(movies, num_movies)
    return [get_movie_info(movie['id']) for movie in random_movies]
