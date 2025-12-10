from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "mongo_KEY")

from pymongo import MongoClient

# CONFIGURATION MONGODB
# Nom du projet : P345THEORIES
# Nom du cluster : p345user
# Username : noahhuai333333_db_user
# Password : mgh9In1rcNZnT43E

# ✅ Chaîne de connexion MongoDB Atlas
MONGO_URI = "mongodb+srv://noahhuai333333_db_user:mgh9In1rcNZnT43E@p345user.mulf4h8.mongodb.net/?retryWrites=true&w=majority&appName=p345user"

# CONNEXION À MONGODB
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Test immédiat de la connexion
    client.server_info()
    print("✅ Connexion à MongoDB réussie !")
except Exception as e:
    print(f"❌ Erreur de connexion MongoDB : {e}")
    print("🔍 Vérifiez :")
    print("   1) Vous avez copié la VRAIE chaîne depuis MongoDB Atlas")
    print("   2) Votre IP est autorisée dans Network Access")
    print("   3) Le mot de passe est correct : mgh9In1rcNZnT43E")
    # On crée quand même un client pour éviter les erreurs, mais il ne fonctionnera pas
    client = MongoClient()

# COLLECTIONS
db = client["p345theories"]
users_collection = db["users"]
comments_collection = db["comments"]

# FONCTIONS BASE DE DONNÉES

def get_user_by_username(username):
    """Récupère un utilisateur par son nom d'utilisateur"""
    return users_collection.find_one({"username": username})

def create_user(username, password):
    """Crée un nouvel utilisateur avec mot de passe hashé"""
    hashed_password = generate_password_hash(password)
    user_data = {
        "username": username,
        "password": hashed_password,
        "created_at": datetime.now()
    }
    users_collection.insert_one(user_data)
    return user_data

def get_all_comments():
    """Récupère tous les commentaires triés par date décroissante"""
    return list(comments_collection.find().sort("created_at", -1))

def add_comment(author, text):
    """Ajoute un nouveau commentaire"""
    comment_data = {
        "author": author,
        "text": text,
        "created_at": datetime.now()
    }
    comments_collection.insert_one(comment_data)

##########
# ROUTES #
##########

@app.route("/")
def index():
    """Page d'accueil"""
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Page de connexion"""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Veuillez remplir tous les champs", "error")
            return render_template("login.html")

        # Vérification utilisateur avec MongoDB
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
    """Page d'inscription"""
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

        # Vérifier si l'utilisateur existe déjà
        if get_user_by_username(username):
            flash("Ce nom d'utilisateur existe déjà", "error")
            return render_template("signup.html")

        # Créer l'utilisateur dans MongoDB
        create_user(username, password)
        flash("Compte créé avec succès ! Connectez-vous maintenant.", "success")
        return redirect(url_for("login"))
    
    return render_template("signup.html")

@app.route("/comments")
def comments():
    """Page des commentaires - nécessite d'être connecté"""
    if "user" not in session:
        flash("Vous devez être connecté pour accéder aux commentaires", "warning")
        return redirect(url_for("login"))
    
    all_comments = get_all_comments()
    return render_template("comments.html", comments=all_comments)

@app.route("/add_comment", methods=["POST"])
def add_comment_route():
    """Route pour ajouter un commentaire"""
    if "user" not in session:
        return redirect(url_for("login"))
    
    text = request.form.get("comment_text", "").strip()
    if text:
        add_comment(session["user"], text)
        flash("Commentaire ajouté !", "success")
    
    return redirect(url_for("comments"))

@app.route("/logout")
def logout():
    """Déconnexion"""
    username = session.get("user")
    session.clear()
    flash(f"À bientôt {username} !", "info")
    return redirect(url_for("index"))

@app.route("/contact")
def contact():
    """Page de contact"""
    return render_template("contact.html")


############################
# LANCEMENT DE L'APPLICATION
############################

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8888)