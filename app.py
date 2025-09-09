from flask import Flask, render_template, url_for, session, redirect, request
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import mysql.connector
import os
import json
import requests
import random

#load env during filling database values
load_dotenv()

#important app things to include
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=False,   # True only with HTTPS
    SESSION_PERMANENT = False      # makes session temporary
)

#db parameters
db_host = os.getenv("DB_HOST_NAME")
db_user_name = os.getenv("DB_USER_NAME")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

#all endpoints ("route")
@app.route("/", methods=["GET","POST"])
def login():
    session.permanent = False
    if request.method == "POST":
        email_login = request.form["email"]
        password_login = str(request.form["password"])
        #database stuff
        connection = mysql.connector.connect(
            host= db_host,
            user= db_user_name,
            password= db_password,
            database= db_name
        )
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users_log WHERE email = %s", (email_login,))
        user = cursor.fetchone()
        if not user:
            cursor.close()
            connection.close()
            return render_template("login.html", error="No User Found, SignUp")
        elif not check_password_hash(user[3], password_login):
            cursor.close()
            connection.close()
            return render_template("login.html", error="Wrong Password")
        else:
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            cursor.close()
            connection.close()
            return redirect(url_for("home"))
        
    return render_template("login.html")

# theres bug in signup form (returning back to the signup again after creating account)
@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        signup_name = request.form["username"]
        signup_email = request.form["email"]
        signup_password = request.form["password"]
        #hash the password
        hashed_password = generate_password_hash(signup_password, method='pbkdf2:sha256', salt_length=10)
        #db user_addition
        connection = mysql.connector.connect(
            host= os.getenv("DB_HOST_NAME"),
            user= os.getenv("DB_USER_NAME"),    
            password= os.getenv("DB_PASSWORD"),
            database= os.getenv("DB_NAME")
        )
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users_log WHERE email = %s", (signup_email,))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return render_template("signup.html", error_signup="User is already registered, Login")
        cursor.execute(
            "INSERT INTO users_log(user_name, email, password) VALUES (%s, %s, %s)",
            (signup_name, signup_email, hashed_password)
        )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/logout")
def logout():
    if "user_id" not in session:   # check session
        return redirect(url_for("login"))
    else:
        session.clear()   # clears all session data
        return redirect(url_for('login'))

@app.route("/home", methods=["POST","GET"])
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("home.html")

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    # Start a new quiz
    if "questions" not in session:
        if request.method == "POST":
            category = request.form.get("category_menu")  # form input
            num_qs = int(request.form.get("num_questions", 10))

            # store category in session
            session["category"] = category

            categories_dic = {
                "general": 9,
                "games": 15,
                "films": 11,
                "computer": 18, 
                "sports": 21
            }

            if category not in categories_dic:
                return redirect(url_for("home"))  # invalid category

            category_key = categories_dic[category]
            api_url = f"https://opentdb.com/api.php?amount={num_qs}&category={category_key}&difficulty=easy&type=multiple"
            data = requests.get(api_url).json()["results"]

            # Save in session
            session["questions"] = data
            session["current_index"] = 0
            session["score"] = 0

        else:
            return redirect(url_for("home"))

    else:
        # Answering a question
        q_index = session["current_index"]
        answer = request.form.get("answer")
        correct = session["questions"][q_index]["correct_answer"]

        if answer == correct:
            session["score"] += 1
        session["current_index"] += 1

    # Quiz finished?
    if session["current_index"] >= len(session["questions"]):
        score = session["score"]
        user_id = session.get("user_id")
        category_db = session["category"]  # ✅ always from session

        # Save history
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user_name,
            password=db_password,
            database=db_name
        )
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users_history (user_id, category, score) VALUES (%s, %s, %s)",
            (user_id, category_db, str(score))
        )
        connection.commit()
        cursor.close()
        connection.close()

        # cleanup
        session.pop("questions", None)
        session.pop("category", None)

        return render_template("home.html", message=f"Quiz finished! Your score: {score}", question=None)

    # Otherwise → show next question
    q = session["questions"][session["current_index"]]
    options = q["incorrect_answers"] + [q["correct_answer"]]
    random.shuffle(options)

    return render_template("home.html",
                           question=q["question"],
                           options=options,
                           current_index=session["current_index"],
                           score=session["score"])


@app.route("/about")
def about():
    if "user_id" not in session:   # check session
        return redirect(url_for("login"))
    return render_template("about.html")

@app.route("/history", methods=["GET"])
def history():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    connection = mysql.connector.connect(
        host=db_host,
        user=db_user_name,
        password=db_password,
        database=db_name
    )
    cursor = connection.cursor()
    cursor.execute(
        "SELECT category, score, finished_at FROM users_history WHERE user_id = %s ORDER BY finished_at DESC LIMIT 10",
        (user_id,)
    )
    history_fetched = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("history.html", history=history_fetched)

@app.route("/submitqa", methods=["POST","GET"])
def submitqa():
    if "user_id" not in session:   # check session
        return redirect(url_for("login"))
    if request.method == "POST":
        submitter_name = request.form["submitter_name"]
        submitter_question = request.form["submitted_question"]
        submitter_options = request.form["submitted_options"]
        
        #adding to json file
        new_entry = {
            "name": submitter_name,
            "questions": submitter_question,
            "options": submitter_options
        }
        
        file_path = "questions.json"
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
        else:
            data = []
            
        data.append(new_entry)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        return render_template("submitqa.html", message="Question has been submitted!!")
    return render_template("submitqa.html")

if __name__ == "__main__":
    app.run(debug=True)