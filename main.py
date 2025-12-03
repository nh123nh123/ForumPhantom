from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "super_secret_change_me"

# --- ROUTES ---

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pw = request.form["password"]

        # Fake login pour la base ― à remplacer par une vraie DB
        if user == "test" and pw == "1234":
            session["user"] = user
            return redirect(url_for("comments"))

        return "Identifiants incorrects"
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Traitement futur : enregistrer dans une base
        return "Compte créé (placeholder)"
    return render_template("signup.html")

@app.route("/comments")
def comments():
    if "user" not in session:
        return redirect(url_for("login"))
    
    fake_comments = [
        {"author": "Alpha", "text": "Théorie 1"},
        {"author": "Beta", "text": "Théorie 2"}
    ]

    return render_template("comments.html", comments=fake_comments)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)