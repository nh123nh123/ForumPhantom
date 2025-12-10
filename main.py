from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "mongo_KEY")

from pymongo import MongoClient

MONGO_URI = "mongodb+srv://noahhuai333333_db_user:mgh9In1rcNZnT43E@p345user.mulf4h8.mongodb.net/?retryWrites=true&w=majority&appName=p345user"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()
    print(" Connexion à MongoDB réussie !")
except Exception as e:
    print(f" Erreur : {e}")
    client = MongoClient()

db = client["p345theories"]
users_collection = db["users"]
comments_collection = db["comments"]

def get_user_by_username(username):
    return users_collection.find_one({"username": username})

def create_user(username, password):
    hashed_password = generate_password_hash(password)
    user_data = {
        "username": username,
        "password": hashed_password,
        "created_at": datetime.now()
    }
    users_collection.insert_one(user_data)
    return user_data

def get_all_comments():
    return list(comments_collection.find().sort("created_at", -1))

def add_comment(author, text):
    comment_data = {
        "author": author,
        "text": text,
        "created_at": datetime.now()
    }
    comments_collection.insert_one(comment_data)

def delete_comment(comment_id):
    comments_collection.delete_one({"_id": ObjectId(comment_id)})

@app.route("/")
def index():
    recent_comments = list(comments_collection.find().sort("created_at", -1).limit(5))
    return render_template("index.html", recent_comments=recent_comments)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Veuillez remplir tous les champs", "error")
            return render_template("login.html")

        user = get_user_by_username(username)
        if user and check_password_hash(user["password"], password):
            session["user"] = username
            flash(f"Bienvenue {username} !", "success")
            return redirect(url_for("comments"))
        
        flash("Identifiants incorrects", "error")
        return render_template("login.html")
    
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("password2", "")

        if not username or not password:
            flash("Veuillez remplir tous les champs", "error")
            return render_template("signup.html")
        
        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas", "error")
            return render_template("signup.html")
        
        if len(password) < 4:
            flash("Le mot de passe doit contenir au moins 4 caractères", "error")
            return render_template("signup.html")

        if get_user_by_username(username):
            flash("Ce nom d'utilisateur existe déjà", "error")
            return render_template("signup.html")

        create_user(username, password)
        flash("Compte créé avec succès ! Connectez-vous maintenant.", "success")
        return redirect(url_for("login"))
    
    return render_template("signup.html")

@app.route("/comments")
def comments():
    if "user" not in session:
        flash("Vous devez être connecté pour accéder aux commentaires", "warning")
        return redirect(url_for("login"))
    
    all_comments = get_all_comments()
    return render_template("comments.html", comments=all_comments)

@app.route("/add_comment", methods=["POST"])
def add_comment_route():
    if "user" not in session:
        return redirect(url_for("login"))
    
    text = request.form.get("comment_text", "").strip()
    if text:
        add_comment(session["user"], text)
        flash("Commentaire ajouté !", "success")
    
    return redirect(url_for("comments"))

@app.route("/delete_comment/<comment_id>", methods=["POST"])
def delete_comment_route(comment_id):
    if "user" not in session:
        return redirect(url_for("login"))
    
    delete_comment(comment_id)
    flash("Commentaire supprimé !", "success")
    return redirect(url_for("comments"))

@app.route("/logout")
def logout():
    username = session.get("user")
    session.clear()
    flash(f"À bientôt {username} !", "info")
    return redirect(url_for("index"))

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8888)