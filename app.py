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
            "get_students_by_roomid" : "/roomwisestudent",
            "get_rooms_free_allocation":"/rooms/freeallocation"
            }
    return {"All Requests":result}

@app.errorhandler(404)
def resource_not_found(e):
        return jsonify(error=str(e)), 404


@app.route('/home')
def home1():
       return render_template('home.html')

#ROOM OPERATIONS
@app.route('/addroom')
def home():
       return render_template('rooms.html')

@app.route("/room",methods=["POST"])
def add_room():
    if request.method == 'POST':
        studentcount=0
        #capacity = request.form['capacity']
        room = request.get_json()
        capacity = room["capacity"]
        if capacity == "":
            return jsonify({"error":"Capacity cannot be empty"}),400
        else:
            record = Rooms(studentcount,capacity)
            db.session.add(record)
            db.session.commit()
            rooms = Rooms.query.all()
            result = [
            {
                "id":room.id,
                "studentcount":room.studentcount,
                "capacity":room.capacity
                }
            for room in rooms]
        return render_template("allroom.html",result=result)

@app.route("/rooms",methods=["GET"])
#def get_all_rooms_handler():
#result=get_all_rooms()
def get_all_rooms():
    rooms = Rooms.query.all()
    result = [
            {
                "id":room.id,
                "studentcount":room.studentcount,
                "capacity":room.capacity
                }
            for room in rooms]
    #return {"result":result}
    return render_template('allroom.html',result=result)

@app.route("/rooms/<int:id>",methods=["GET"])
def get_room_by_id(id):
    rooms = Rooms.query.get_or_404(id)
    result ={
                "id":rooms.id,
                "studentcount":rooms.studentcount,
                "capacity":rooms.capacity
                }
    return render_template('editroom.html',result=result)

@app.route("/rooms/<int:id>",methods=["PUT"])
def update_room_byid(id):
    room = Rooms.query.get_or_404(id)
    rooms = request.get_json()
    if 'capacity' in rooms:
        if int(rooms['capacity']) < room.studentcount:
            return jsonify({"error":"Capacity should not be less than student count in given room"}),400
        else:
            room.capacity = rooms['capacity']
    db.session.add(room)
    db.session.commit()
    return {"result":"room is updated"}

@app.route("/rooms/<int:id>",methods=["DELETE"])
def delete_room_by_id(id):
    roomData = get_room_free_allocation_byid(id)
    studcount = roomData["freeallocation"]["capacity"]-roomData["freeallocation"]["freeallocation"]
    if studcount > 0:
        return jsonify({"error":"Room contains students. You are not athorised to delete room!"}),400

    room = Rooms.query.get_or_404(id)
    db.session.delete(room)
    db.session.commit()
    return {"result":"Record deleted successfully"}

@app.route("/rooms/freeallocation",methods=["GET"])
def get_room_free_allocation_handler():
    result = get_room_free_allocation()
    return render_template('free_allocation.html',result=result)

def get_room_free_allocation():
    rooms = Rooms.query.all()
    result=[]
    for room in rooms:
        ca = room.capacity
        sc = room.studentcount
        freeallocation = ca - sc
        result.append(
                {
            "id":room.id,
            "capacity":room.capacity,
            "freeallocation":freeallocation
            })
    return {'freeallocation':result}

@app.route("/rooms/freeallocation/<int:id>",methods=["GET"])
def get_room_free_allocation_byid_handler():
    result = get_room_free_allocation_byid()
    return render_template("free_allocation_byid.html",result=result),200


def get_room_free_allocation_byid(id):
    try:
        rooms = Rooms.query.get_or_404(id)
        result=[]
        capacity = rooms.capacity
        studcount = rooms.studentcount
        freeallocation = capacity - studcount
        result={
            "id":rooms.id,
            "capacity":rooms.capacity,
            "freeallocation":freeallocation
            }
        return {"freeallocation":result}
    except Exception as e:
        return resource_not_found(e)


#STUDENT OPERATIONS
@app.route("/addstudent",methods=["GET"])
def create_student():
    freerooms = get_room_free_allocation()
    roomslist=[]
    for rooms in freerooms['freeallocation']:
        print(rooms)
        if rooms['freeallocation']>0:
            print(rooms['freeallocation'])
            roomslist.append(rooms)
    return render_template("create_student.html",roomslist=roomslist)

@app.route("/student",methods=["POST"])
def add_student():
    if request.method == "POST":
        student = request.get_json()
        studentname = student['studname']
        roomid = student['roomid']
        if studentname == "":
            return jsonify({"error":"Student Name should not be empty!!"}),400  #bad request
        if roomid == "":
            roomData = get_room_free_allocation()
            roomfound=False
            for room in roomData:
                if (room['freeallocation']>0):
                    roomfound=True
                    roomid = room['id']
                    break
            if not roomfound:
                return jsonify({"error":"Room is not available!!"}),400  #bad request

            if roomfound == True:
                update_room_data(roomid,"add")
                new_student = Students(studname=studentname,roomid=roomid)
                db.session.add(new_student)
                db.session.commit()
        else:
            roomData = get_room_free_allocation_byid(roomid)
            print(roomData,roomid)
            if len(roomData) == 2 and roomData[1] == 404:
                print(roomData)
                return jsonify({"error":"Please select the Room Id"}),400  #bad request

            roomfound=False
            print(roomData)
            if (roomData['freeallocation']['freeallocation']>0):
                print("You can add student")
                roomfound=True
                roomid = roomData['freeallocation']['id']
            if roomfound == False:
                return jsonify({"error":"Given room is full. Please select another room"}),400  #bad request

            if roomfound == 1:
                update_room_data(roomid,"add")
                new_student = Students(studname=studentname,roomid=roomid)
                db.session.add(new_student)
                db.session.commit()

        students = Students.query.all()
        result = [
            {
                "id":student.id,
                "studname":student.studname,
                "roomid":student.roomid
                }
            for student in students]
        return render_template("allstudent.html",result=result), 201


def update_room_data(id,operation):
    room=Rooms.query.get_or_404(id)

    if operation == "add":
        if room.capacity > room.studentcount:
            room.studentcount+=1
        else:
            return jsonify({"error":"Rooms are full"}),400  #bad request
    if room.studentcount > 0:
        if operation == "delete":
            room.studentcount-=1
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
    return render_template('allstudent.html',result=result)

@app.route("/students/<int:id>",methods=["GET"])
def get_student_by_id(id):
    student = Students.query.get_or_404(id)
    result = {
            "id":student.id,
            "studname":student.studname,
            "roomid":student.roomid
            }
    rooms = Rooms.query.all()
    allrooms = [
            {
                "id":room.id,
                "studentcount":room.studentcount,
                "capacity":room.capacity
                }
            for room in rooms]
    freerooms = get_room_free_allocation()
    roomslist=[]
    for rooms in freerooms['freeallocation']:
        if rooms['freeallocation']>0 and rooms['id']!=result["roomid"]:
            roomslist.append(rooms)
            print(roomslist)
    return render_template('editstudent.html',result=result, allrooms=allrooms, roomslist=roomslist)

@app.route("/students/<int:id>",methods=["PUT"])
def update_student_byid(id):
    result1=[]
    student = Students.query.get_or_404(id)
    students = request.get_json()

    if students["studname"] == "" or students["roomid"] == None:
        return jsonify({"error":"Student name or Roomid cannot be empty while updation"}),400  #bad request

    if student.studname != students["studname"]:
        student.studname = students["studname"]

    if student.roomid == students["roomid"] or students["roomid"]== "0":
        result = {
            "id":student.id,
            "studname":student.studname,
            "roomid":student.roomid
            }
        db.session.add(student)
        db.session.commit()
        return render_template('editstudent.html',result=result)

    if student.roomid != students["roomid"]:
        roomid = students["roomid"]

        roomdata = get_room_free_allocation_byid(roomid)
        if len(roomdata) == 2 and roomdata[1] == 404:
            return jsonify({"error":"Room is not available"}),400  #bad request

        if roomdata['freeallocation']['freeallocation'] <= 0:
            return jsonify({"error":"Room capacity full"}),400  #bad request

        update_room_data(roomid,"add")#updating the student count in NEW room

        if student.roomid !=None:
            update_room_data(student.roomid,"delete") #updating the student count in OLD room

        student.roomid = roomid
    result = {
            "id":student.id,
            "studname":student.studname,
            "roomid":student.roomid
            }
    db.session.add(student)
    db.session.commit()
    return render_template('editstudent.html',result=result)

@app.route("/students/<int:id>",methods=["DELETE"])
def delete_student_by_id(id):
    student = Students.query.get_or_404(id)
    print(student.roomid)
    if student.roomid:
        update_room_data(student.roomid,"delete")
    db.session.delete(student)
    db.session.commit()
    return {"result":"Student Deleted successfully"} , 200

#get students detail using room id
@app.route("/roomwisestudent/<int:id>")
def get_student_byroom_id(id):
    room = Rooms.query.get_or_404(id)
    students = Students.query.all()
    result=[]
    for student in students:
        if room.id == student.roomid:
            result.append(
                    {
                    "id":student.id,
                    "studentname":student.studname,
                    "roomid":student.roomid
                    })
    return render_template('result.html',result=result)

#get all urls for all operations
@app.route("/",methods=["GET"])
def get_all_urls():
    result = {
            "add_student" : "/addstudent",
            "get_all_students" : "/students",
            "get_student_by_id" : "/students/<id>",
            "update_student_by_id" :"/students/<id>",
            "delete_student_by_id" : "/students/<id>",
            "add_room" : "/addroom",
            "get_all_rooms" : "/rooms",
            "get_room_by_id" : "/rooms/<id>",
            "update_room_by_id" : "/rooms/<id>",
            "delete_room_by_id" : "/rooms/<id>",
            "get_students_by_roomid" : "/roomwisestudent",
            "get_rooms_free_allocation":"/rooms/freeallocation"
            }
    return {"All Requests":result}

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
