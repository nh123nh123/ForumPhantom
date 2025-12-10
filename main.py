from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "mongo_KEY")

from pymongo import MongoClient
# client = MongoClient("")
# db = client["p345theories"]
# users_collection = db["users"]
# comments_collection = db["comments"]

def get_user_by_username(username):
    """
    
    return users_collection.find_one({"username": username})
    """
    # Base de données temporaire en mémoire
    fake_users = {
        "test": {"username": "test", "password": "1234"}
    }
    return fake_users.get(username)

def create_user(username, password):
    """
    À remplacer par une insertion MongoDB
    Exemple futur: users_collection.insert_one({"username": username, "password": hashed_pw})
    """
    return {"username": username, "password": password}

def get_all_comments():
    """
    À remplacer par une requête MongoDB
    Exemple futur: return list(comments_collection.find().sort("created_at", -1))
    """
    return [
        {"author": "Alpha", "text": "Théorie intéressante sur Persona 3/4/5 !"},
        {"author": "Beta", "text": "J'ai une nouvelle théorie à partager..."},
        {"author": "Gamma", "text": "Discussion sur les social links"}
    ]

def add_comment(author, text):
    """
    À remplacer par une insertion MongoDB
    Exemple futur: comments_collection.insert_one({"author": author, "text": text, "created_at": datetime.now()})
    """
    pass

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

        # Vérification utilisateur (à remplacer par MongoDB + hash)
        user = get_user_by_username(username)
        if user and user["password"] == password:
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
        confirm_password = request.form.get("confirm_password", "")

        if not username or not password:
            flash("Veuillez remplir tous les champs", "error")
            return render_template("signup.html")
        
        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas", "error")
            return render_template("signup.html")
        
        if len(password) < 4:
            flash("Le mot de passe doit contenir au moins 4 caractères", "error")
            return render_template("signup.html")

        # Vérifier si l'utilisateur existe (futur: MongoDB)
        if get_user_by_username(username):
            flash("Ce nom d'utilisateur existe déjà", "error")
            return render_template("signup.html")

        # Créer l'utilisateur (futur: MongoDB avec hash)
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
    """Ajouter un commentaire - Route pour plus tard"""
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
#LANCEMENT DE L'APPLICATION#
############################

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8888)