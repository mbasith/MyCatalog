# Project 1 - Item Catalog
 by (Mohammed Yousuffi)

## Project Description

I've chosen to create a Retro Video Game Catalog that lists popular video game titles from several gaming platforms.  
Games are cataloged by video game genres.  Any user can add a new video game title to an existing video game genre
but only the genre owner can edit or delete the genre. Video games also can only be edited or deleted by the author.

Each video game stored in the database includes the following details.

1. Video game title
2. An Item Number
3. A short description
4. Current selling price
5. Platform the video game supports
5. A rating based on a 5 star rating scale 

## Project Design

The catalog uses a combination of Python3 and the Flask.  Flasks is
a framework for building web applications and is used to host the video game catalog application.
Several other Python modules were used to create the web application including
SQL Alchemy, httplib2, requests, and oauth2client. SQL Alchemy provides the database functionality for storing 
and retrieving user and catalog data. The httplib2, requests, and oauth2client modules are using for 
HTTP requests and authentication. The catalog also supports an API that returns JSON results back to the user.
The application is available to non-authenticated users but does not allow and CRUD actions.  A user can
authenticate using the Google API in order to create, edit, or delete catalog information.

## Prerequisites

To deploy this web application the following prerequisites must be met:

1. A windows or linux host running Python3 or later
2. A google account to perform Create, Read, Update, Delete (CRUD) operations 
3. Th following modules must be installed
* flask - import Flask, render_template, request, redirect, url_for, flash, 
jsonify, make_response, import session as login_session
* sqlalchemy - create_engine, 
* sqlalchemy.orm - sessionmaker
* oauth2client.client - flow_from_clientsecrets, FlowExchangeError
* httplib2
* random 
* string
* json
* requests

Installing prerequisites using PIP installer:

```bash
pip install flask
pip install sqlalchemy
pip install sqlalchemy.orm
pip install oauth2client.client
pip install httplib2
pip install random
pip install string
pip install json
pip install requests
```

4. Catalog application files.  The files are zipped into the "my_project.zip" file.

```bash

│   client_secrets.json
│   database_setup.py
│   myproject.py
│   old_database_setup.py
│   readme.md
│   videogamecatalog.db
│
├───static
│   ├───css
│   │       styles.css
│   │
│   ├───img
│   └───js
│           star_rating.js
│
└───templates
        deletegame.html
        deletegenre.html
        editgame.html
        editgenre.html
        game.html
        genres.html
        header.html
        login.html
        main.html
        newgame.html
        newgenre.html
        publicgame.html
        publicgenres.html
```



## How to Run Python Script

1. Extract the contents of the my_project.zip to the desired directory
2. Launch the myproject.py python script to start the web server on port 5000
3. Navigate to the localhost:5000 URL

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[http://localhost:5000/](http://localhost:5000/)

3. Login using a Google account or browse existing video game genres

## How to use API

Retrieve list of available video game genres:

```bash
URI: /genres/JSON

Example: http://localhost:5000/genres/JSON
{
  "genres": [
    {
      "id": 2, 
      "name": "Adventure", 
      "user_id": 1
    }, 
    {
      "id": 3, 
      "name": "Fighting", 
      "user_id": 2
    }, 
    {
      "id": 6, 
      "name": "Racing", 
      "user_id": 1
    }, 
    {
      "id": 7, 
      "name": "Platforming", 
      "user_id": 1
    }, 
    {
      "id": 10, 
      "name": "Puzzle", 
      "user_id": 1
    }, 
    {
      "id": 15, 
      "name": "Rythm", 
      "user_id": 1
    }, 
    {
      "id": 19, 
      "name": "Role Playing", 
      "user_id": 1
    }, 
    {
      "id": 20, 
      "name": "Action", 
      "user_id": 1
    }, 
    {
      "id": 21, 
      "name": "Sports", 
      "user_id": 1
    }
  ]
}
```

Retrieve list of games under a specified genre ID:

```bash
URI: /genres/<int:genre_id>/catalog/JSON

Example: http://localhost:5000/genres/2/catalog/JSON
{
  "games": [
    {
      "description": "Cute round marshmallow type creature traveling the universe to satisfy his appetite.", 
      "id": 8, 
      "name": "Kirby", 
      "platform": "Super Nintendo", 
      "price": "5.99", 
      "rating": "5.99", 
      "user_id": 1
    }, 
    {
      "description": "An elf hero fighting the forces of evil to save the Kingdom of Highrule", 
      "id": 9, 
      "name": "Legend of Zelda", 
      "platform": "Nintendo 64", 
      "price": "9.99", 
      "rating": "9.99", 
      "user_id": 1
    }
  ]
}

```

Retrieve specified video game based on the game ID and genre ID:

```bash
URI: /genres/<int:genre_id>/catalog/<int:game_id>/JSON

Example: http://localhost:5000/genres/2/catalog/8/JSON
{
  "game": {
    "description": "Cute round marshmallow type creature traveling the universe to satisfy his appetite.", 
    "id": 8, 
    "name": "Kirby", 
    "platform": "Super Nintendo", 
    "price": "5.99", 
    "rating": "5.99", 
    "user_id": 1
  }
}
```
