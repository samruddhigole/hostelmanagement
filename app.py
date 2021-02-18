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

#get all urls for all operations
@app.route("/",methods=["GET"])
def get_all_urls():

    result = {
            "post_for_student" : "/students",
            "get_all_students" : "/students",
            "get_student_by_id" : "/students/<id>",
            "update_student_by_id" :"/students/<id>",
            "delete_student_by_id" : "/students/<id>",
            "add_room" : "/rooms",
            "get_all_rooms" : "/rooms",
            "get_room_by_id" : "/rooms/<id>",
            "update_room_by_id" : "/rooms/<id>",
            "delete_room_by_id" : "/rooms/<id>",
            "get_students_by_roomid" : "/roomwisestudent"
            }
    return {"All Requests":result}

#OPERATIONS for ROOMS
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

@app.route("/rooms",methods=["GET"])
def get_all_rooms():
    rooms = Rooms.query.all()
    result = [
            {
                "id":room.id,
                "studentcount":room.studentcount,
                "capacity":room.capacity
                }
            for room in rooms]
    return {"count":len(result),"rooms":result}

@app.route("/rooms/<int:id>",methods=["GET"])
def get_room_by_id(id):
    rooms = Rooms.query.get_or_404(id)

    result ={
                "id":rooms.id,
                "studentcount":rooms.studentcount,
                "capacity":rooms.capacity
                }
    return {"result":result}

@app.route("/rooms/<int:id>",methods=["PUT"])
def update_room_byid(id):

    room = Rooms.query.get_or_404(id)
    rooms = request.get_json()
    if 'capacity' in rooms:
        room.capacity = rooms['capacity']
    db.session.add(room)
    db.session.commit()
    return {"result":"Room is updated"}


@app.route("/rooms/<int:id>",methods=["DELETE"])
def delete_room_by_id(id):

    room = Rooms.query.get_or_404(id)
    db.session.delete(room)
    db.session.commit()
    return {"result":"Record deleted successfully"}


#OPERATIONS for STUDENTS

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

def update_room_data(id,operation):
    room=Rooms.query.get_or_404(id)
    if operation == "add":
        print("B",room.studentcount)
        room.studentcount+=1
        print("A",room.studentcount)

    if operation == "delete":
        print("B",room.studentcount)
        room.studentcount-=1
        print("A",room.studentcount)
    db.session.add(room)
    db.session.commit()

@app.route("/students",methods=["GET"])
def get_all_students():
    students = Students.query.all()

    result = [
            {
                "id":student.id,
                "studname":student.studname,
                "roomid":student.roomid
                }
            for student in students]
    return {"result":result},200


@app.route("/students/id/<int:id>",methods=["GET"])
def get_student_by_id(id):
    student = Students.query.get_or_404(id)

    result = {
            "id":student.id,
            "studname":student.studname,
            "roomid":student.roomid
            }
    return {"result":result},200

@app.route("/students/<int:id>",methods=["PUT"])
def update_student_byid(id):

    student = Students.query.get_or_404(id)
    students = request.get_json()
    student.studname = students["studname"]
    student.roomid = students["roomid"]
    db.session.add(student)
    db.session.commit()
    return {"result":"Student record is updated successfully"}, 200

@app.route("/students/<int:id>",methods=["DELETE"])
def delete_student_by_id(id):

    student = Students.query.get_or_404(id)
    update_room_data(student.roomid,"delete")
    db.session.delete(student)
    db.session.commit()
    return {"result":"Student Deleted successfully"} , 200


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
