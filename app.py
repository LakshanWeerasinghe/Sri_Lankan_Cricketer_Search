from flask import Flask, render_template, request

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


@app.route('/profile/<string:id>', methods=['GET'])
def get_user_profile(id):

    result = search.get_player_by_id(id)
    player = result.get('_source')

    return render_template('profile.html', res=player)


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'mysecret'
    app.run(host='0.0.0.0', port=5000)
