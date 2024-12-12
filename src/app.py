from db import db
from flask import Flask, request
import json
from db import HealthData
from datetime import datetime

app = Flask(__name__)
db_filename = "cms.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

# Generalized response formats
def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code

def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code

# -- ROUTES ------------------------------------------------------------

@app.route("/")
def base():
  return "hello world"

@app.route("/data/", methods=["POST"])
def create_data():
  body = json.loads(request.data)
  heart_rate = body.get("heart_rate", None)
  blood_oxygen = body.get("blood_oxygen", None)
  glucose_level = body.get("glucose_level", None)
  hrv = body.get("hrv", None)
  longitude = body.get("longitude", None)
  latitude = body.get("latitude", None)

  new_data = HealthData(
        heart_rate=heart_rate,
        blood_oxygen=blood_oxygen,
        glucose_level=glucose_level,
        hrv=hrv,
        latitude=latitude,
        longitude=longitude,
        timestamp = datetime.now()
    )
  db.session.add(new_data)
  db.session.commit()
  return success_response(new_data.serialize(), 201)

@app.route("/data/<int:user_id>/")
def get_data(user_id):
  # Check if data exists 
  data = HealthData.query.filter_by(id=user_id).first()
  if data is None:
    return failure_response("Data not found")
  
  return success_response(data.serialize())

@app.route("/data/")
def get_all_data():
  return success_response({"data": [u.serialize() for u in HealthData.query.all()]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
