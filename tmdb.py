import os
import requests
import random

TMDB_API_KEY = os.getenv('TMDB_API_KEY')
BASE_URL = 'https://api.themoviedb.org/3'

# Genre list from TMDB API
GENRES = [
    {'id': 28, 'name': 'Action'}, 
    {'id': 12, 'name': 'Adventure'}, 
    {'id': 16, 'name': 'Animation'}, 
    {'id': 35, 'name': 'Comedy'}, 
    {'id': 80, 'name': 'Crime'}, 
    {'id': 99, 'name': 'Documentary'}, 
    {'id': 18, 'name': 'Drama'}, 
    {'id': 10751, 'name': 'Family'}, 
    {'id': 14, 'name': 'Fantasy'}, 
    {'id': 36, 'name': 'History'}, 
    {'id': 27, 'name': 'Horror'}, 
    {'id': 10402, 'name': 'Music'}, 
    {'id': 9648, 'name': 'Mystery'}, 
    {'id': 10749, 'name': 'Romance'}, 
    {'id': 878, 'name': 'Science Fiction'}, 
    {'id': 10770, 'name': 'TV Movie'}, 
    {'id': 53, 'name': 'Thriller'}, 
    {'id': 10752, 'name': 'War'}, 
    {'id': 37, 'name': 'Western'}
]


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

def get_popular_movies():
    page = random.randint(1, 100)
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
    poster_size = 'w500'

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

def discover_movies_by_genre(genre_id, page=1):
    url = f'{BASE_URL}/discover/movie'
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US',
        'sort_by': 'popularity.desc',
        'include_adult': 'true',
        'with_genres': genre_id,
        'page': page
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def get_random_movies(num_movies=2):
    random_genre = random.choice(GENRES)
    genre_id = random_genre['id']
    
    all_movies = []
    movies = discover_movies_by_genre(genre_id, random.randint(1,10))
    all_movies.extend(movies['results'])
    print(len(all_movies))
    
    random_movies = random.sample(all_movies, num_movies)
    return [get_movie_info(movie['id']) for movie in random_movies]