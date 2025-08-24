from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'voting.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'change-me'  # for flash messages
ADMIN_KEY = 'letmein'  # simple admin key for adding candidates

db = SQLAlchemy(app)

# --- Database tables ---
class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    manifesto = db.Column(db.Text, default='')

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll = db.Column(db.String(50), unique=True, nullable=False)  # one vote per roll
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    candidate = db.relationship('Candidate')

# --- Pages ---
@app.route('/', methods=['GET', 'POST'])
def home():
    candidates = Candidate.query.order_by(Candidate.name).all()
    if request.method == 'POST':
        roll = request.form.get('roll', '').strip().upper()
        cand_id = request.form.get('candidate')
        if not roll or not cand_id:
            flash('Please enter roll number and select a candidate.')
            return redirect(url_for('home'))
        try:
            db.session.add(Vote(roll=roll, candidate_id=int(cand_id)))
            db.session.commit()
            flash('Vote saved! Thank you.')
            return redirect(url_for('results'))
        except IntegrityError:
            db.session.rollback()
            flash('This roll number has already voted.')
            return redirect(url_for('results'))
    return render_template('index.html', candidates=candidates)

@app.route('/results')
def results():
    candidates = Candidate.query.order_by(Candidate.name).all()
    totals = []
    total_votes = Vote.query.count()
    for c in candidates:
        count = Vote.query.filter_by(candidate_id=c.id).count()
        totals.append({'candidate': c, 'count': count})
    totals.sort(key=lambda x: (-x['count'], x['candidate'].name))
    winner = totals[0] if totals else None
    return render_template('results.html', totals=totals, total_votes=total_votes, winner=winner)

@app.route('/admin/add', methods=['GET', 'POST'])
def add_candidate():
    key = request.values.get('key', '')
    if request.method == 'POST':
        if key != ADMIN_KEY:
            flash('Wrong admin key.')
            return redirect(url_for('add_candidate') + f'?key={key}')
        name = request.form.get('name', '').strip()
        manifesto = request.form.get('manifesto', '').strip()
        if not name:
            flash('Name is required.')
            return redirect(url_for('add_candidate') + f'?key={key}')
        if Candidate.query.filter_by(name=name).first():
            flash('Candidate already exists.')
            return redirect(url_for('add_candidate') + f'?key={key}')
        db.session.add(Candidate(name=name, manifesto=manifesto))
        db.session.commit()
        flash('Candidate added.')
        return redirect(url_for('add_candidate') + f'?key={key}')
    return render_template('admin_add.html', key=key, admin_key=ADMIN_KEY)

# --- First run: make DB and sample candidates ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if Candidate.query.count() == 0:
            for nm in ['Alice', 'Bob', 'Charlie']:
                db.session.add(Candidate(name=nm, manifesto=''))
            db.session.commit()
    app.run(debug=True)
