import os
import redis
from flask import Flask, jsonify, request
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

cache = redis.StrictRedis(host="english_redis", port=6379, decode_responses=True)

API_KEY = os.getenv("API_KEY")  
CACHE_TIMEOUT = int(os.getenv("CACHE_TIMEOUT", 300))  


@app.route('/define/<word>', methods=['GET'])
def get_definition(word):
    cache_key = f"definition:{word}"
    cached_def = cache.get(cache_key)
    
    if cached_def:
        return jsonify({"source": "redis", "word": word, "definition": cached_def})

    url = f"https://api.api-ninjas.com/v1/dictionary?word={word}"
    headers = {"X-Api-Key": API_KEY}  
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        definition = response.json().get("definition", "No definition found.")
        cache.setex(cache_key, CACHE_TIMEOUT, definition) 
        return jsonify({"source": "api", "word": word, "definition": definition})
    else:
        return jsonify({"error": "Unable to fetch definition."}), 500

@app.route('/random_word', methods=['GET'])
def get_random_word():
    url = "https://api.api-ninjas.com/v1/randomword"
    headers = {"X-Api-Key": API_KEY}  

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        word_data = response.json()
        return jsonify(word_data)
    else:
        return jsonify({"error": "Unable to fetch random word."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("FLASK_PORT", 5000))) 
