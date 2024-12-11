from db import db

from flask import Flask, request, jsonify
from analysis import analyze_biometric_data

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

  heart_rate = body.get("heart_rate")
  blood_oxygen = body.get("blood_oxygen")
  glucose_level = body.get("glucose_level")
  hrv = body.get("hrv")
  longitude = body.get("longitude")
  latitude = body.get("latitude")

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

  analysis_results = analyze_biometric_data({
    'heart_rate': heart_rate,
    'blood_oxygen': blood_oxygen,
    'glucose_level': glucose_level,
    'hrv': hrv
  })

  return success_response({
        'data': new_data.serialize(),
        'analysis': analysis_results
        }, 201)

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

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    API endpoint to just analyze the biometric data.
    """
    data = request.json

    analysis_results = analyze_biometric_data({
        'heart_rate': data.get('heart_rate'),
        'blood_oxygen': data.get('blood_oxygen'),
        'glucose_level': data.get('glucose_level'),
        'hrv': data.get('hrv')
    })

    return success_response(analysis_results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
