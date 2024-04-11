from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
app.permanent_session_lifetime = timedelta(days=5)

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    
    def __init__(self, name, email):
        self.name = name
        self.email = email

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/view")
def view():
    return render_template("view.html",values=users.query.all())



@app.route("/test", methods=["POST", "GET"])
def test():
    if request.method == "POST":
        session.permanent = True
        user_name = request.form.get("nm")
        session["custom_user_key"] = user_name
        
        found_user = users.query.filter_by(name=user_name).first()
        if not found_user:
            usr = users(name=user_name, email="")
            db.session.add(usr)
            db.session.commit()
            flash("New user created!", "info")
        else:
            session["email"] = found_user.email
            flash("Login successful", "info")
        
        return redirect(url_for("user"))
    elif "custom_user_key" in session:
        return redirect(url_for("user"))
    else:
        return render_template("login.html")

@app.route("/user", methods=["POST", "GET"])
def user():
    email = None
    if "custom_user_key" in session:
        user_name = session["custom_user_key"]
        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_user = users.query.filter_by(name=user_name).first()
            if found_user:
                found_user.email = email
                db.session.commit()
                flash("Email was saved!")
            else:
                flash("User not found!")
        else:
            if "email" in session:
                email = session["email"]
        return render_template("user.html", email=email)
    else:
        flash("You are not logged in")
        return redirect(url_for("test"))

@app.route("/logout")
def logout():
    session.pop("custom_user_key", None)
    session.pop("email", None)
    flash("You are logged out", "info")
    return redirect(url_for("test"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
