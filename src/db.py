from unicodedata import category
from flask_sqlalchemy import SQLAlchemy
import base64
import boto3
import datetime
import io
from io import BytesIO
from mimetypes import guess_extension, guess_type
import os
from PIL import Image
import random
import re
import string

db = SQLAlchemy()

EXTENSIONS = ["png", "gif", "jpg","jpeg"]
BASE_DIR = os.getcwd()
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_BASE_URL = f"https://{S3_BUCKET_NAME}.s3.us-east-1.amazonaws.com"


####################
# Image Class
####################
class Asset(db.Model):
  """
  Asset model
  """
  __tablename__ = "asset"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  base_url = db.Column(db.String, nullable=True)
  salt = db.Column(db.String, nullable=False)
  extension = db.Column(db.Integer, nullable=False)
  width = db.Column(db.Integer, nullable=False)
  height = db.Column(db.Integer, nullable=False)
  created_at = db.Column(db.DateTime, nullable=False)

  def __init__(self, **kwargs):
    """
    Intialize an Asset object
    """
    self.create(kwargs.get("image_data"))

  def serialize(self):
    """
    serialize an asset object
    """
    return {
      "url": f"{self.base_url}/{self.salt}.{self.extension}",
      "created_at": str(self.created_at)
    }

  def get_img_url(self):
    """
    return img url
    """
    return f"{self.base_url}/{self.salt}.{self.extension}"

  def create(self, image_data):
    """
    given image in base64 form, check filetype, generate random string for image filename, decode image and upload it to AWS
    """
    try:
      ext = guess_extension(guess_type(image_data)[0])[1:]
      if ext not in EXTENSIONS:
        raise Exception(f"unsupported file type: {ext}")

      salt = "".join(
        random.SystemRandom().choice(
          string.ascii_uppercase + string.digits
        )
        for _ in range(16)
      )

      img_str = re.sub("^data:image/.+;base64,", "", image_data)
      image_data = base64.b64decode(img_str)
      img = Image.open(BytesIO(image_data))  #convert binary image data from base64 to Image object

      self.base_url = S3_BASE_URL
      self.salt = salt
      self.extension = ext
      self.width = img.width
      self.height = img.height
      self.created_at = datetime.datetime.now()

      img_filename = f"{salt}.{ext}"
      self.upload(img, img_filename)


    except Exception as e:
      print(f"errror when creating image: {e}")

      
  def upload(self, img, img_filename):
    """
    upload image to specified s3 bucket
    """
    try:
      # save image temp on server
      img_temploc = f"{BASE_DIR}/{img_filename}"
      img.save(img_temploc)

      # upload the image to S3
      s3_client = boto3.client("s3")
      s3_client.upload_file(img_temploc, S3_BUCKET_NAME, img_filename)

      # make S3 image url public
      s3_resource = boto3.resource("s3")
      object_acl = s3_resource.ObjectAcl(S3_BUCKET_NAME, img_filename)
      object_acl.put(ACL="public-read")

      # remove imge from server
      os.remove(img_temploc)

    except Exception as e:
      print(f"error when upolading image: {e}")


####################
# Park Class
####################
class Park(db.Model): 
    """
    parks model
    has a one-to-many relationship with the comment model
    """   
    __tablename__ = "parks"    
    id = db.Column(db.Integer, primary_key=True)    
    name = db.Column(db.String, nullable=False)
    latitude = db.Column(db.String, nullable=True)
    longitude = db.Column(db.String, nullable=True)
    address = db.Column(db.String, nullable=False)
    hourlyRate = db.Column(db.String, nullable=True)
    dailyRate = db.Column(db.String, nullable=True)
    rateDays = db.Column(db.String, nullable=True)
    openHours = db.Column(db.String, nullable=True)
    note = db.Column(db.String, nullable=True)
    comments = db.relationship("Comment", cascade="delete")


    def __init__(self, **kwargs):
      """
      init park object
      """
      self.name = kwargs.get("name", "")
      self.latitude = kwargs.get("latitude", "")
      self.longitude = kwargs.get("longitude", "")
      self.address = kwargs.get("address", "")
      self.hourlyRate = kwargs.get("hourlyRate", "")
      self.dailyRate = kwargs.get("dailyRate", "")
      self.rateDays = kwargs.get("rateDays", "")
      self.openHours = kwargs.get("openHours", "")
      self.note = kwargs.get("note", "")
      self.comments = []


    def serialize(self):  
      """
      convert object into json format
      """
      return {        
          "id": self.id,  
          "name": self.name,      
          "latitude": self.latitude,        
          "longitude": self.longitude,   
          "address": self.address,   
          "hourlyRate": self.hourlyRate,   
          "dailyRate": self.dailyRate,   
          "rateDays": self.rateDays,   
          "openHours": self.openHours,   
          "note": self.note,           
          "comments":[s.serialize() for s in self.comments]
          }

    def simple_serialize(self):  
      """
      only provide minimal info about a park
      """
      return {        
          "id": self.id,  
          "name": self.name,
          "address": self.address
      } 

####################
# Comment Class
####################
class Comment(db.Model):
  """
  comment model
  """
  __tablename__ = "comments"    
  id = db.Column(db.Integer, primary_key=True)    
  netid = db.Column(db.String, nullable=False)
  comment = db.Column(db.String, nullable=False)
  img_url = db.Column(db.String, nullable=True)
  park_id = db.Column(db.Integer, db.ForeignKey("parks.id"), nullable=False)


  def __init__(self, **kwargs):
    """
    init comment object
    """
    self.netid = kwargs.get("netid", "")
    self.comment = kwargs.get("comment", "")
    self.park_id = kwargs.get("park_id")
    self.img_url = kwargs.get("img_url","")
    

  def serialize(self):  
    """
    convert object into json format
    """
    return {        
        "id": self.id,        
        "netid": self.netid,     
        "comment": self.comment,   
        "img": self.img_url
    }