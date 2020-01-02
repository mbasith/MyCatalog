#!/usr/bin/python3

# Import Flask and SQL modules and database_setup script
from flask import Flask, render_template, request, redirect, url_for, flash, \
    jsonify, make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Genre, Game, User
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import random
import string
import json
import requests

# Initialize Flask Application
app = Flask(__name__)

# Point SQL engine to genre DB and Bind engine
engine = create_engine('sqlite:///videogamecatalog.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

# Establishes a link of communication between the code and the engine
DBSession = sessionmaker(bind=engine)

# Create an instance of a DB session
session = DBSession()

# Load Client ID
CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Retro Video Games"


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    """Google Sign-In Link """
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits) for x in
        range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Validate users token using Google API"""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code, now compatible with Python3
    request.get_data()
    code = request.data.decode('utf-8')

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # Submit request, parse response - Python3 compatible
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already '
                                            'connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;' \
              'border-radius: 150px;-webkit-border-radius: 150px;' \
              '-moz-border-radius: 150px;"> '
    flash("Logged in as %s" % login_session['username'])
    return output


# User Helper Functions
def createUser(login_session):
    """Creates users in the DB based on info retrieved from the Google API"""
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """Retrieve users info from the Database"""
    user = session.query(User).filter_by(id=user_id).first()
    return user


def getUserID(email):
    """Retrieve users email address from the Database"""
    user = session.query(User).filter_by(email=email).one()
    return user.id


@app.route('/gdisconnect')
def gdisconnect():
    """Function to revoke a current user's token and reset their
    login_session"""
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    print('In gdisconnect access token is %s', access_token)
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'POST')[0]
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully logged out.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# Making an API Endpoint for genre game (Get Request)
@app.route('/genres/JSON')
def genreJSON():
    genres = session.query(Genre).all()
    return jsonify(genres=[i.serialize for i in genres])


# Making an API Endpoint for genre game (Get Request)
@app.route('/genres/<int:genre_id>/catalog/JSON')
def genregameJSON(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    items = session.query(Game).filter_by(genre_id=genre.id).all()
    return jsonify(games=[i.serialize for i in items])


# Making an API Endpoint for genre game Item (Get Request)
@app.route('/genres/<int:genre_id>/catalog/<int:game_id>/JSON')
def genregameItemJSON(genre_id, game_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    gameItem = session.query(Game).filter_by(genre_id=genre.id,
                                             id=game_id).one()
    return jsonify(game=gameItem.serialize)


# URL Routes
# Show all Video Game Genres
@app.route('/')
@app.route('/genres')
def showgenres():
    genres = session.query(Genre).all()
    if 'username' not in login_session:
        return render_template('publicgenres.html', genres=genres)
    else:
        return render_template('genres.html', genres=genres)


# Create a new genre
@app.route('/genre/new', methods=['GET', 'POST'])
def newgenre():
    if request.method == 'POST':
        print(request.form)
        print('REQUEST FORM', request.form['name'], type(request.form['name']))
        newgenreAdd = Genre(name=request.form['name'],
                            user_id=login_session['user_id'])
        session.add(newgenreAdd)
        session.commit()
        flash('New genre {} created.'.format(newgenreAdd.name))
        return redirect(url_for('showgenres'))
    else:
        return render_template('newgenre.html')


# Edit an existing genre
@app.route('/genre/<int:genre_id>/edit', methods=['GET', 'POST'])
def editgenre(genre_id):
    editedgenre = session.query(Genre).filter_by(id=genre_id).one()
    currentgenreName = editedgenre.name

    if 'username' not in login_session:
        return redirect('/login')
    if editedgenre.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not " \
               "authorized to edit this genre. Only content you created " \
               "can be edited.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        editedgenre.name = request.form['name']
        session.add(editedgenre)
        session.commit()
        flash('Genre successfully edited from {} to '
              '{}'.format(currentgenreName, editedgenre.name))
        return redirect(url_for('showgenres'))
    else:
        return render_template('editgenre.html', genre=editedgenre)


# URL to delete a video game genre
@app.route('/genre/<int:genre_id>/delete', methods=['GET', 'POST'])
def deletegenre(genre_id):
    deletedgenre = session.query(Genre).filter_by(id=genre_id).one()
    deletedgenreName = deletedgenre.name

    if 'username' not in login_session:
        return redirect('/login')
    if deletedgenre.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not " \
               "authorized to delete this genre. Only content you " \
               "created can be deleted.');}</script><body " \
               "onload='myFunction()''>"

    if request.method == 'POST':
        session.delete(deletedgenre)
        session.commit()
        flash('Genre {} successfully deleted.'.format(deletedgenreName))
        return redirect(url_for('showgenres'))
    else:
        return render_template('deletegenre.html', genre=deletedgenre)


# URL to show a video game game
@app.route('/genre/<int:genre_id>')
@app.route('/genre/<int:genre_id>/game')
def showgame(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    creator = getUserInfo(genre.user_id)
    items = session.query(Game).filter_by(genre_id=genre.id)

    if not hasattr(creator, 'id'):
        return render_template('publicgame.html', items=items, genre=genre,
                               creator=creator)
    elif hasattr(creator, 'id'):
        if 'username' not in login_session:
            print('User not in login session or creator.id not equal to '
                  'login session user_id')
            return render_template('publicgame.html', items=items,
                                   genre=genre, creator=creator)
        else:
            return render_template('game.html', items=items,
                                   genre=genre, creator=creator)
    else:
        return render_template('game.html', genre=genre,
                               items=items, creator=creator)


# Create/Add a new video game
@app.route('/genre/<int:genre_id>/game/new', methods=['GET', 'POST'])
def newgame(genre_id):
    if request.method == 'POST':
        newItem = Game(name=request.form['name'],
                       description=request.form['description'],
                       price=request.form['price'],
                       rating=request.form['rating'],
                       platform=request.form['platform'],
                       genre_id=genre_id,
                       user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New game {} created!'.format(newItem.name))
        return redirect(url_for('showgame', genre_id=genre_id))
    else:
        return render_template('newgame.html', genre_id=genre_id)


# Edit an existing video game item
@app.route('/genre/<int:genre_id>/<int:game_id>/edit/', methods=['GET',
                                                                 'POST'])
def editgame(genre_id, game_id):
    existinggame = session.query(Game).filter_by(id=game_id).one()
    editedItem = session.query(Game).filter_by(id=game_id).one()

    if 'username' not in login_session:
        return redirect('/login')
    if editedItem.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not " \
               "authorized to edit this game. Please add your own " \
               "game in order to edit.');}</script><body " \
               "onload='myFunction()''>"

    if request.method == 'POST':
        update_list = []
        edited_flag = False
        if existinggame.name != request.form['name']:
            editedItem.name = request.form['name']
            update_list.append('name')
            edited_flag = True

        if existinggame.description != request.form['description']:
            editedItem.description = request.form['description']
            update_list.append('description')
            edited_flag = True

        if existinggame.price != request.form['price']:
            editedItem.price = request.form['price']
            update_list.append('price')
            edited_flag = True

        if 'rating' in request.form:
            if existinggame.rating != request.form['rating']:
                editedItem.rating = request.form['rating']
                update_list.append('rating')
                edited_flag = True

        if existinggame.platform != request.form['platform']:
            editedItem.platform = request.form['platform']
            update_list.append('platform')
            edited_flag = True

        if edited_flag is True:
            session.add(editedItem)
            session.commit()
            tense = 'was'
            if len(update_list) > 1:
                tense = 'were'
            flash('The {} {} successfully updated for game '
                  '{}.'.format(', '.join(update_list), tense,
                               existinggame.name))
        else:
            flash('No changes made for {}.'.format(existinggame.name,
                                                   editedItem.name))
        return redirect(url_for('showgame', genre_id=genre_id))
    else:
        return render_template('editgame.html',
                               genre_id=genre_id,
                               game_id=game_id,
                               game=existinggame,
                               item=editedItem)


# Delete a video game  from a Genre
@app.route('/genre/<int:genre_id>/<int:game_id>/delete/', methods=['GET',
                                                                   'POST'])
def deletegame(genre_id, game_id):
    deletedItem = session.query(Game).filter_by(id=game_id).one()

    if 'username' not in login_session:
        return redirect('/login')
    if deletedItem.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not " \
               "authorized to delete this game. Please add your own game " \
               "in order to delete.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        session.delete(deletedItem)
        session.commit()
        flash('Game successfully {} deleted.'.format(deletedItem.name))
        return redirect(url_for('showgame', genre_id=genre_id))
    else:
        return render_template('deletegame.html', genre_id=genre_id,
                               game_id=game_id, item=deletedItem)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
app.run(host='0.0.0.0', port=5000)
