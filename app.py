from flask import Flask, render_template, request

import search

app = Flask(__name__)

global_scope = {
    'search_terms': None,
    'roles': [],
    'bowling_styles': []
}


@app.route('/')
def home():
    return render_template('search.html')


@app.route('/search/results', methods=['GET', 'POST'])
def search_request():
    search_term = request.form["input"]

    res, roles, bowling_styles = search.search(search_term)

    global_scope['search_terms'] = search_term
    global_scope['roles'] = roles
    global_scope['bowling_styles'] = bowling_styles

    res['search_term'] = global_scope.get('search_terms')
    print(global_scope.get('search_terms'))
    return render_template('results.html', res=res, roles=roles, bowling_styles=bowling_styles)


@app.route('/search/results/filter', methods=['GET', 'POST'])
def faceted_search_request():

    role_filter = []
    bowling_style_filter = []

    for role in global_scope.get('roles'):
        if request.form.get(role["id"]):
            role_filter.append(role)

    for bowling_style in global_scope.get('bowling_styles'):
        if request.form.get(bowling_style["id"]):
            bowling_style_filter.append(bowling_style)

    search_term = global_scope.get('search_terms')

    res, roles, bowling_styles = search.search(search_term, role_filter, bowling_style_filter)

    print(role_filter, bowling_style_filter)
    res['search_term'] = global_scope.get('search_terms')
    print(global_scope.get('search_terms'))
    return render_template('results.html', res=res, roles=roles, bowling_styles=bowling_styles)


@app.route('/profile/<string:id>', methods=['GET'])
def get_user_profile(id):
    player = search.get_player_by_id(id)

    return render_template('profile.html', res=player)


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'mysecret'
    app.run(host='0.0.0.0', port=5000)
