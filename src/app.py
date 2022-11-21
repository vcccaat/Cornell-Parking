import os
from db import db
from db import Asset, Park, Comment
from flask import Flask, request
import json


app = Flask(__name__)
db_filename = "parking.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    # db.session.query(Comment).delete()
    db.session.commit()
    db.create_all()


@app.route("/")
def hello():
    return "succcess"



@app.route("/upload/", methods=["POST"])
def upload():
    """
    endpoint for uploading image to AWS given its base64, then store returning URL
    """
    body = json.loads(request.data)
    image_data = body.get("image_data")
    if image_data is None:
        return failure_response("no base64 image passed in!")
    
    asset = Asset(image_data=image_data)
    db.session.add(asset)
    db.session.commit()
    return success_response(asset.serialize(), 201)



@app.route("/parks/")
def get_parks():
    """
    Endpoint for getting all parks info
    """  
    return success_response({"parks": [t.serialize() for t in Park.query.all()]})



@app.route("/parks/", methods=["POST"])
def create_park():
    """
    Endpoint for creating a new parking
    """
    body = json.loads(request.data)
    if not body.get("name") or not body.get("address"):
        return failure_response("didn't provide name or address", 400)

    if Park.query.filter_by(name=body.get("name")).first():
        return failure_response("This parking already exist", 400)

    new_park = Park(address=body.get("address"), 
                      name=body.get("name"),
                      latitude=body.get("latitude",""),
                      longitude=body.get("longitude",""),
                      hourlyRate=body.get("hourlyRate",""),
                      dailyRate=body.get("dailyRate",""),
                      rateDays=body.get("rateDays",""),
                      openHours=body.get("openHours",""),
                      note=body.get("note",""))
    db.session.add(new_park)
    db.session.commit()
    return success_response(new_park.serialize(), 201)



@app.route("/parks/<int:park_id>/")
def get_park(park_id):
    """
    Endpoint for getting a park by id
    """
    park = Park.query.filter_by(id=park_id).first()
    if not park:
        return failure_response("park not found")
    return success_response(park.serialize())



@app.route("/parks/<int:park_id>/", methods=["DELETE"])
def delete_park(park_id):
    """
    Endpoint for deleting a park by id
    """
    park = Park.query.filter_by(id=park_id).first()
    if not park:
        return failure_response("park not found")
    db.session.delete(park)
    db.session.commit()
    return success_response(park.serialize())



# @app.route("/parks/<int:park_id>/", methods=["POST"])
# def edit_park(park_id):
#     """
#     Endpoint for editing a park attribute
#     """
#     park = Park.query.filter_by(id=park_id).first()
#     if not park:
#         return failure_response("park not found")

#     body = json.loads(request.data)

#     new_park = Park(
#         netid=body.get("netid"),
#         park=body.get("park"),
#         park_id=park_id
#     )
#     db.session.add(new_park)
#     db.session.commit()
#     return success_response(new_park.serialize(),201)



@app.route("/parks/<int:park_id>/comment/", methods=["POST"])
def create_comment(park_id):
    """
    Endpoint for creating a comment for a park by id
    """
    park = Park.query.filter_by(id=park_id).first()
    if not park:
        return failure_response("park not found")

    body = json.loads(request.data)
    if not body.get("netid") or not body.get("comment"):
        return failure_response("didn't provide info", 400)

    image_data = body.get("image_data")
    img_url = ""
    if image_data:
        # upload image 
        asset = Asset(image_data=image_data)
        db.session.add(asset)
        db.session.commit()
        img_url = asset.get_img_url()

        new_comment = Comment(
            netid=body.get("netid"),
            comment=body.get("comment"),
            park_id=park_id,
            img_url=img_url,
        )
        db.session.add(new_comment)
        db.session.commit()
        return success_response(new_comment.serialize(),201)
    else:
        new_comment = Comment(
        netid=body.get("netid"),
        comment=body.get("comment"),
        park_id=park_id,
        )
        db.session.add(new_comment)
        db.session.commit()
        return success_response(new_comment.serialize(),201)


@app.route("/parks/<int:park_id>/comment/", methods=["GET"])
def get_comment(park_id):
    """
    Endpoint for getting all comments for a park by id
    """
    park = Park.query.filter_by(id=park_id).first()
    if not park:
        return failure_response("park not found")

    return success_response({"comments": [s.serialize() for s in park.comments]},201)



@app.route("/comments/<int:comment_id>/", methods=["DELETE"])
def delete_comment(comment_id):
    """
    Endpoint for deleting a comment by id
    """
    comment = Comment.query.filter_by(id=comment_id).first()
    if not comment:
        return failure_response("comment not found")
    db.session.delete(comment)
    db.session.commit()
    return success_response(comment.serialize())



# generalized response formats
def success_response(data, code=200):
    return json.dumps(data), code

def failure_response(message, code=404):
    return json.dumps({"error": message}), code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
