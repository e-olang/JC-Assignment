from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from os import environ
import pandas as pd
import numpy as np

import process_csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
db = SQLAlchemy(app)


class MeteorChecklist(db.Model):
    __tablename__ = 'meteor_checklist'

    id = db.Column(db.Integer, primary_key=True)
    cme_completion_date = db.Column(db.Date)
    cme_topic = db.Column(db.Text)
    cme_unique_id = db.Column(db.BigInteger)
    county = db.Column(db.Text)
    date_submitted = db.Column(db.TIMESTAMP)
    drill_topic = db.Column(db.Text)
    drill_unique_id = db.Column(db.Text)
    essential_cme_topic = db.Column(db.Boolean)
    essential_drill_topic = db.Column(db.Boolean)
    facility_code = db.Column(db.Text)
    facility_name = db.Column(db.Text)
    id_number_cme = db.Column(db.Text)
    id_number_drill = db.Column(db.Text)
    mentor_name = db.Column(db.Text)
    submission_id = db.Column(db.BigInteger)
    success_story = db.Column(db.Text)

    def json(self):
        return {
            'id': self.id,
            'cme_completion_date': str(self.cme_completion_date),
            'cme_topic': self.cme_topic,
            'cme_unique_id': self.cme_unique_id,
            'county': self.county,
            'date_submitted': str(self.date_submitted),
            'drill_topic': self.drill_topic,
            'drill_unique_id': self.drill_unique_id,
            'essential_cme_topic': self.essential_cme_topic,
            'essential_drill_topic': self.essential_drill_topic,
            'facility_code': self.facility_code,
            'facility_name': self.facility_name,
            'id_number_cme': self.id_number_cme,
            'id_number_drill': self.id_number_drill,
            'mentor_name': self.mentor_name,
            'submission_id': self.submission_id,
            'success_story': self.success_story
        }

db.create_all()

# POST Endpoint
@app.route('/write', methods=['POST'])
def create_meteor_checklist():
    
    if 'csv' not in request.files:
        return make_response(jsonify({'message': 'No CSV file uploaded'}), 500)
    
    file = request.files['csv']

    try:
        df = pd.read_csv(file)
        cases = process_csv.read_cases(df)
        if not cases:
            return make_response(jsonify({'error': 'No cases seen'}), 500)
        else:
            id = 1
            for i in range(len(cases)):
                rows = process_csv.create_case(cases[i], 8)
                for j in range(len(rows)):
                    data = rows[j]
                    data = {key: int(value) if isinstance(value, np.int64) else value for key, value in data.items()}
                    new_entry = MeteorChecklist(
                        id = id,
                        cme_completion_date = data['cme_completion_date'],
                        cme_topic=data['cme_topic'],
                        cme_unique_id=data['cme_unique_id'],
                        county=data['county'],
                        date_submitted=data['date_submitted'],
                        drill_topic=data['drill_topic'],
                        drill_unique_id=data['drill_unique_id'],
                        essential_cme_topic=data['essential_cme_topic'],
                        essential_drill_topic=data['essential_drill_topic'],
                        facility_code=data['facility_code'],
                        facility_name=data['facility_name'],
                        id_number_cme=data['id_number_cme'],
                        id_number_drill=data['id_number_drill'],
                        mentor_name=data['mentor_name'],
                        submission_id=data['submission_id'],
                        success_story=data['success_story']
                    )
                    db.session.add(new_entry)
                    db.session.commit()
                    id = id + 1

            return make_response(jsonify({'message': 'Data loaded well'}), 201)

    except Exception as e:
        return make_response(jsonify({'error': 'Error reading provided CSV file', 'details': str(e)}), 500)

    


# TEST Endpoint lch/port
@app.route('/test', methods=['GET'])
def test():
    return make_response(jsonify({'message': 'env running well'}), 200)

if __name__ == '__main__':
    app.run(debug=True)