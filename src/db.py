from unicodedata import category
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()



class Park(db.Model): 
    """
    parks model
    has a one-to-many relationship with the comment model
    """   
    __tablename__ = "parks"    
    id = db.Column(db.Integer, primary_key=True)    
    name = db.Column(db.String, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.String, nullable=False)
    hourlyRate = db.Column(db.String, nullable=False)
    dailyRate = db.Column(db.String, nullable=False)
    rateDays = db.Column(db.String, nullable=False)
    openHours = db.Column(db.String, nullable=False)
    note = db.Column(db.String, nullable=False)
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



class Comment(db.Model):
  """
  comment model
  """
  __tablename__ = "comments"    
  id = db.Column(db.Integer, primary_key=True)    
  netid = db.Column(db.String, nullable=False)
  comment = db.Column(db.String, nullable=False)

  def __init__(self, **kwargs):
    """
    init comment object
    """
    self.netid = kwargs.get("netid", "")
    self.comment = kwargs.get("comment", "")

