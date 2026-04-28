from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Medecin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    specialite = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telephone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150),unique=True,nullable=False)
    password = db.Column(db.String(255),nullable=False)


class RendezVous(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    groupe_sanguin = db.Column(db.String(10), nullable=False)
    fonction = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    heure = db.Column(db.String(50), nullable=False)
    motif = db.Column(db.String(200), nullable=False)
    statut = db.Column(db.String(20), default='en attente')
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    medecin_id = db.Column(db.Integer, db.ForeignKey('medecin.id'), nullable=True)
    patient = db.relationship('Patient', backref='rendezvous')
    medecin = db.relationship('Medecin', backref='rendezvous')


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    message = db.Column(db.String(255))
    type = db.Column(db.String(50))  # accepte / recu

    lu = db.Column(db.Boolean, default=False)

    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    medecin_id = db.Column(db.Integer, db.ForeignKey('medecin.id'))