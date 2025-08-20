from flask import Flask, request, redirect, url_for
from flask_restful import Api, Resource
from models import db, Student

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///students.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
api = Api(app)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    # Redirect to /students
    return redirect(url_for("students"))

# ------------------ Validation Helper ------------------
VALID_GRADES = {"A", "B", "C", "D"}

def validate_grade(grade):
    return grade in VALID_GRADES

# ------------------ Resources ------------------

class StudentListResource(Resource):
    def get(self):
        students = Student.query.all()
        return [student.to_dict() for student in students], 200

    def post(self):
        data = request.get_json()
        if not data:
            return {"status": "error", "message": "Missing JSON body"}, 400

        name = data.get("name")
        roll = data.get("roll")
        grade = data.get("grade")

        if not name or not roll or not grade:
            return {"status": "error", "message": "Name, Roll, and Grade are required"}, 400

        if not validate_grade(grade):
            return {"status": "error", "message": "Grade must be A, B, C, or D"}, 400

        # Prevent duplicate roll numbers
        if Student.query.filter_by(roll=roll).first():
            return {"status": "error", "message": "Roll number already exists"}, 400

        new_student = Student(name=name, roll=roll, grade=grade)
        db.session.add(new_student)
        db.session.commit()

        return {"status": "success", "student": new_student.to_dict()}, 201


class StudentResource(Resource):
    def get(self, id):
        student = Student.query.get_or_404(id)
        return {"status": "success", "student": student.to_dict()}, 200

    def put(self, id):
        student = Student.query.get_or_404(id)
        data = request.get_json()

        if "name" in data:
            student.name = data["name"]
        if "roll" in data:
            # prevent duplicate roll if changed
            if Student.query.filter(Student.roll == data["roll"], Student.id != id).first():
                return {"status": "error", "message": "Roll number already taken"}, 400
            student.roll = data["roll"]
        if "grade" in data:
            if not validate_grade(data["grade"]):
                return {"status": "error", "message": "Grade must be A, B, C, or D"}, 400
            student.grade = data["grade"]

        db.session.commit()
        return {"status": "success", "student": student.to_dict()}, 200

    def delete(self, id):
        student = Student.query.get_or_404(id)
        db.session.delete(student)
        db.session.commit()
        return {"status": "success", "message": "Student deleted"}, 200

# Register resources
api.add_resource(StudentListResource, "/students", endpoint="students")
api.add_resource(StudentResource, "/students/<int:id>", endpoint="student")

if __name__ == "__main__":
    app.run(debug=True)
