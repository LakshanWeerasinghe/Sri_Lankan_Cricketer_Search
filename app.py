from flask import Flask, render_template, request
from elasticsearch import Elasticsearch

import search

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('search.html')


@app.route('/search/results', methods=['GET', 'POST'])
def search_request():
    search_term = request.form["input"]

    res = search.search(search_term)

    return render_template('results.html', res=res )


@app.route('/profile', methods=['GET'])
def get_user_profile():

    return render_template('profile.html')

if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'mysecret'
    app.run(host='0.0.0.0', port=5000)
