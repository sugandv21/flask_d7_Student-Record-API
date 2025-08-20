from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    roll = db.Column(db.String(50), unique=True, nullable=False)
    grade = db.Column(db.String(2), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "roll": self.roll,
            "grade": self.grade
        }
