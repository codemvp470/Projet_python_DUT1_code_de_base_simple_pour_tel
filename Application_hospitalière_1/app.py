# =====================================================
from flask import Flask, render_template, request, redirect, url_for, session
from config import Config
from models import db, Patient, Admin, Medecin, RendezVous

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# =====================================================
# ROUTES PRINCIPALES
# =====================================================

@app.route('/')
def accueil():
    return render_template('accueil.html')


@app.route('/choix')
def choix():
    return render_template('choix_utilisateur.html')


@app.route('/patient')
def patient_menu():
    return render_template('patient/menu_patient.html')


@app.route('/admin')
def admin_root():
    return redirect(url_for('admin_login'))


@app.route('/medecin')
def medecin_root():
    return redirect(url_for('login_medecin'))


# =====================================================
# INSCRIPTION PATIENT
# =====================================================
@app.route('/patient/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        nom = request.form.get('nom', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not nom or not email or not password or not confirm_password:
            return "❌ Tous les champs sont obligatoires"

        if password != confirm_password:
            return "❌ Les mots de passe ne correspondent pas"

        patient_exist = Patient.query.filter_by(email=email).first()
        if patient_exist:
            return "❌ Email déjà utilisé"

        patient = Patient(
            nom=nom,
            email=email,
            password=password
        )

        db.session.add(patient)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('patient/register.html')


# =====================================================
# CONNEXION PATIENT
# =====================================================
@app.route('/patient/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        patient = Patient.query.filter_by(email=email).first()

        if patient and patient.password == password:
            session['patient_connecte'] = patient.id
            return redirect(url_for('dashboard_patient'))

        return "❌ Email ou mot de passe incorrect"

    return render_template('patient/login.html')


# =====================================================
# DASHBOARD PATIENT
# =====================================================
@app.route('/patient/dashboard')
def dashboard_patient():

    patient_id = session.get('patient_connecte')

    if not patient_id:
        return redirect(url_for('login'))

    rendezvous = RendezVous.query.filter_by(patient_id=patient_id).all()

    return render_template(
        'patient/dashboard_patient.html',
        rendezvous=rendezvous
    )


# =====================================================
# PRISE DE RENDEZ-VOUS
# =====================================================
@app.route('/patient/rendez-vous', methods=['GET', 'POST'])
def prise_rdv():

    if 'patient_connecte' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        patient_id = session['patient_connecte']

        rdv = RendezVous(
            nom=request.form['nom'],
            prenom=request.form['prenom'],
            age=request.form['age'],
            groupe_sanguin=request.form['groupe_sanguin'],
            fonction=request.form['fonction'],
            date=request.form['date'],
            heure=request.form['heure'],
            motif=request.form['motif'],
            medecin_id=int(request.form.get('medecin_id')) if request.form.get('medecin_id') else None,
            patient_id=patient_id,
            statut="en_attente"
        )

        db.session.add(rdv)
        db.session.commit()

        return redirect(url_for('dashboard_patient'))

    medecins = Medecin.query.all()

    return render_template('patient/prise_rdv.html', medecins=medecins)


# =====================================================
# MODIFICATION RENDEZ-VOUS
# =====================================================
@app.route('/patient/modifier-rdv/<int:id>', methods=['GET', 'POST'])
def modifier_rdv(id):

    if 'patient_connecte' not in session:
        return redirect(url_for('login'))

    rdv = RendezVous.query.filter_by(
        id=id,
        patient_id=session['patient_connecte']
    ).first_or_404()

    if request.method == 'POST':

        rdv.nom = request.form['nom']
        rdv.prenom = request.form['prenom']
        rdv.age = request.form['age']
        rdv.groupe_sanguin = request.form['groupe_sanguin']
        rdv.fonction = request.form['fonction']
        rdv.date = request.form['date']
        rdv.heure = request.form['heure']
        rdv.motif = request.form['motif']

        db.session.commit()

        return redirect(url_for('dashboard_patient'))

    return render_template('patient/modifier_rdv.html', rdv=rdv)


# =====================================================
# HISTORIQUE RENDEZ-VOUS
# =====================================================
@app.route('/patient/historique')
def historique():

    if 'patient_connecte' not in session:
        return redirect(url_for('login'))

    patient_id = session['patient_connecte']

    rendezvous = RendezVous.query.filter_by(patient_id=patient_id).all()

    if not rendezvous:
        return """
            <h2>⚠️ Vous n'avez pas encore d'historique de rendez-vous.</h2>
            <br>
            <a href="/patient/dashboard">⬅️ Retour au dashboard</a>
        """

    return render_template('patient/historique.html', rendezvous=rendezvous)


# =====================================================
# LOGOUT PATIENT
# =====================================================
@app.route('/patient/logout')
def patient_logout():
    session.pop('patient_connecte', None)
    return redirect(url_for('login'))


# =====================================================
# LOGIN ADMIN
# =====================================================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        admin = Admin.query.filter_by(email=email, password=password).first()

        if admin:
            session['admin_connecte'] = admin.email
            return redirect(url_for('admin_dashboard'))

        return "❌ Admin incorrect"

    return render_template('admin/login_admin.html')


# =====================================================
# DASHBOARD ADMIN
# =====================================================
@app.route('/admin/dashboard')
def admin_dashboard():

    if 'admin_connecte' not in session:
        return redirect(url_for('admin_login'))

    return render_template('admin/admin_dashboard.html')


# =====================================================
# BEFORE REQUEST
# =====================================================
@app.before_request
def verifier_acces_admin():

    if not request.endpoint:
        return

    routes_admin_protegees = [
        'admin_dashboard',
        'ajouter_medecin',
        'liste_medecins',
        'supprimer_medecin',
        'voir_patients',
        'statistiques'
    ]

    if request.endpoint in routes_admin_protegees:
        if 'admin_connecte' not in session:
            return redirect(url_for('admin_login'))


# =====================================================
# LISTE MEDECINS
# =====================================================
@app.route('/admin/medecins', methods=['GET', 'POST'])
def liste_medecins():

    if 'admin_connecte' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':

        nom_complet = request.form.get('nom_complet', '').strip()
        email = request.form.get('email', '').strip()
        specialite = request.form.get('specialite', '').strip()
        telephone = request.form.get('telephone', '').strip()
        password = request.form.get('password', '').strip()

        if not telephone.startswith("+241"):
            telephone = "+241" + telephone.lstrip("0")

        if Medecin.query.filter_by(email=email).first():
            return "❌ Email déjà utilisé"

        if Medecin.query.filter_by(telephone=telephone).first():
            return "❌ Téléphone déjà utilisé"

        medecin = Medecin(
            nom=nom_complet,
            email=email,
            specialite=specialite,
            telephone=telephone,
            password=password
        )

        try:
            db.session.add(medecin)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return f"❌ Erreur: {str(e)}"

        return redirect(url_for('liste_medecins'))

    medecins = Medecin.query.all()
    return render_template('admin/liste_medecins.html', medecins=medecins)


# =====================================================
# SUPPRIMER MEDECIN
# =====================================================
@app.route('/admin/supprimer-medecin/<int:id>')
def supprimer_medecin(id):

    if 'admin_connecte' not in session:
        return redirect(url_for('admin_login'))

    medecin = Medecin.query.get_or_404(id)
    db.session.delete(medecin)
    db.session.commit()

    return redirect(url_for('liste_medecins'))


# =====================================================
# VOIR PATIENTS
# =====================================================
@app.route('/admin/patients')
def voir_patients():

    if 'admin_connecte' not in session:
        return redirect(url_for('admin_login'))

    patients = Patient.query.all()
    return render_template('admin/patients.html', patients=patients)


# =====================================================
# MODIFIER PATIENT
# =====================================================
@app.route('/admin/modifier-patient/<int:id>', methods=['GET', 'POST'])
def modifier_patient(id):

    patient = Patient.query.get_or_404(id)

    if request.method == 'POST':
        patient.nom = request.form['nom']
        patient.email = request.form['email']
        patient.password = request.form['password']

        db.session.commit()
        return redirect(url_for('voir_patients'))

    return render_template('admin/modifier_patient.html', patient=patient)


# =====================================================
# STATISTIQUES
# =====================================================
@app.route('/admin/statistiques')
def statistiques():

    if 'admin_connecte' not in session:
        return redirect(url_for('admin_login'))

    nb_patients = Patient.query.count()
    nb_medecins = Medecin.query.count()
    nb_rdvs = RendezVous.query.count()

    return render_template(
        'admin/statistiques.html',
        patients=nb_patients,
        medecins=nb_medecins,
        rdvs=nb_rdvs
    )


# =====================================================
# LOGOUT ADMIN
# =====================================================
@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))


# =====================================================
# LOGIN MEDECIN
# =====================================================
@app.route('/medecin/login', methods=['GET', 'POST'])
def login_medecin():

    if request.method == 'POST':

        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        medecin = Medecin.query.filter_by(email=email, password=password).first()

        if medecin:
            session['medecin_connecte'] = medecin.id
            return redirect(url_for('dashboard_medecin'))

        return "❌ Email ou mot de passe incorrect"

    return render_template('medecin/login_medecin.html')


# =====================================================
# DASHBOARD MEDECIN
# =====================================================
@app.route('/medecin/dashboard')
def dashboard_medecin():

    if 'medecin_connecte' not in session:
        return redirect(url_for('login_medecin'))

    medecin_id = session['medecin_connecte']
    medecin = Medecin.query.get_or_404(medecin_id)

    return render_template('medecin/dashboard_medecin.html', medecin=medecin)


# =====================================================
# PATIENTS DU MEDECIN
# =====================================================
@app.route('/medecin/mes-patients')
def mes_patients():

    if 'medecin_connecte' not in session:
        return redirect(url_for('login_medecin'))

    medecin_id = session['medecin_connecte']

    rendezvous = RendezVous.query.filter_by(medecin_id=medecin_id).all()

    return render_template('medecin/mes_patients.html', rendezvous=rendezvous)


# =====================================================
# MARQUER PATIENT COMME REÇU
# =====================================================
@app.route('/medecin/recu/<int:id>')
def marquer_recu(id):

    if 'medecin_connecte' not in session:
        return redirect(url_for('login_medecin'))

    rdv = RendezVous.query.get_or_404(id)
    rdv.statut = "reçu"
    db.session.commit()

    return redirect(url_for('mes_patients'))


# =====================================================
# MARQUER PATIENT COMME ACCEPTÉ
# =====================================================
@app.route('/medecin/accepter/<int:id>')
def accepter_rdv(id):

    if 'medecin_connecte' not in session:
        return redirect(url_for('login_medecin'))

    rdv = RendezVous.query.get_or_404(id)
    rdv.statut = "accepté"
    db.session.commit()

    return redirect(url_for('mes_patients'))


# =====================================================
# LOGOUT MEDECIN
# =====================================================
@app.route('/medecin/logout')
def medecin_logout():
    session.pop('medecin_connecte', None)
    return redirect(url_for('login_medecin'))


# =====================================================
# LANCEMENT DE L'APPLICATION
# =====================================================
if __name__ == "__main__":

    with app.app_context():
        db.create_all()

        admin = Admin.query.filter_by(email="admin@hopital.com").first()

        if not admin:
            admin = Admin(email="admin@hopital.com", password="admin123")
            db.session.add(admin)
            db.session.commit()

    app.run(host="0.0.0.0", port=5000)