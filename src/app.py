import os
from db import db
from db import Course, Assignment, User
from flask import Flask, request
import json


app = Flask(__name__)
db_filename = "parking.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.session.commit()
    db.create_all()


@app.route("/")
def hello():
    return "succcess"

@app.route("/parks/")
def get_parks():
    """
    Endpoint for getting all parks info
    """  
    pass



# generalized response formats
def success_response(data, code=200):
    return json.dumps(data), code

def failure_response(message, code=404):
    return json.dumps({"error": message}), code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
