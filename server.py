"""
File: server.py
Author: Metflekx

Desc. :

TODO:
    [*] make a restAPI that takes csv
"""

from flask import Flask, request, jsonify
from flask_restful import Resource, Api

# Init
app = Flask(__name__)
api = Api(app)

class Vehicles(Resource):
    """
    RESTAPI
    """

    def get(self):
        """ READ ALL BOOKS
        """
        return 201

    def post(self):
        """ CREATE A BOOK
            Takes a form and creates
            a book in the database.
        """

        file = request.files["file"]
        return file.read().decode("utf-8")
        return 201

api.add_resource(Vehicles, '/vehicles')# , '/<string:vid>')

if __name__ == '__main__':
    app.run(debug=True)
