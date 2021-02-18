
from flask import Flask, render_template, request, jsonify, json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_serialize import FlaskSerializeMixin
from sqlalchemy.orm import backref

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="postgresql://hosteluser:admin123@localhost:5432/hostelmanagement"

db = SQLAlchemy(app)
migrate = Migrate(app,db)

FlaskSerializeMixin.db = db

@app.route("/rooms",methods=["POST"])
def create_room():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            new_room = Rooms(studentcount=data['studentcount'],capacity=data['capacity'])
            db.session.add(new_room)
            db.session.commit()
            return {"result":"Record is created successfully"}, 201
        else:
            return {"result":"not updated"}


@app.route("/students",methods=["POST"])
def add_student():
    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
            roomData = get_room_free_allocation()
            print(roomData)
            roomfound=0
            for room in roomData['freeallocation']:
                if (room['freeallocation']>0):
                    roomfound=1
                    roomid = room['id']
                    break
            if roomfound == 1:
                update_room_data(roomid,"add")
                new_student = Students(studname=data['studname'],roomid=roomid)
                db.session.add(new_student)
                db.session.commit()
                return {"result":"Successfully added new student"}, 201
            else:
                return {"result":"Free rooms are not found"}, 404


class Rooms(FlaskSerializeMixin,db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True)
    studentcount = db.Column(db.Integer)
    capacity = db.Column(db.Integer)

    serialize_only=('studentcount','capacity')

    create_fields = update_fields = ['studentcount','capacity']

    def __init__(self,studentcount,capacity):
        self.studentcount = studentcount
        self.capacity = capacity


class Students(FlaskSerializeMixin,db.Model):
    __tablename__ = 'student'

    id=db.Column(db.Integer,primary_key=True)
    studname = db.Column(db.String())
    roomid = db.Column(db.Integer, db.ForeignKey('room.id'))
    room = db.relationship("Rooms",backref=backref("room"))

    serialize_only=('studname','roomid')

    create_fields = update_fields = ['studname','roomid']

    def __init__(self,studname,roomid):
        self.studname = studname
        self.roomid = roomid



db.create_all()
db.session.commit()


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=8080)
