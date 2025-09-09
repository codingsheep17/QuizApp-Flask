🧠 Quiz App

A Flask-powered web application where users can sign up, log in, take quizzes by category, track their history, and even submit new questions. The app connects with the Open Trivia Database API for quiz questions and stores user data/history in a MySQL database.

🚀 Features

🔑 User Authentication – Sign up, login, logout (with hashed passwords).

📚 Multiple Categories – Choose from General Knowledge, Sports, Video Games, Films, and Computer Science.

📝 Custom Quiz Settings – Select number of questions.

🏆 Scoring System – Track your progress with scores.

📜 History Page – View your recent quiz attempts (category, score, finished time).

💡 Question Submission – Users can contribute their own questions stored in JSON.

🔒 Session Security – Sessions reset when browser closes or server restarts.

🛠️ Tech Stack

Backend: Flask (Python)

Frontend: HTML, CSS, Jinja2 templating

Database: MySQL

API: Open Trivia Database

Environment Config: python-dotenv

📂 Project Structure
quiz-app/
│── app.py                 # Main Flask app
│── templates/             # Jinja2 HTML templates
│   ├── layout.html
│   ├── login.html
│   ├── signup.html
│   ├── home.html
│   ├── history.html
│   ├── about.html
│   └── submitqa.html
│── static/                # CSS files
│   ├── home.css
│   ├── quiz.css
│   ├── history.css
│   └── ...
│── questions.json         # Stores user-submitted questions
│── .env                   # Environment variables (not tracked in git)
│── requirements.txt       # Python dependencies
└── README.md              # Project documentation

⚙️ Setup Instructions
1. Clone Repo
git clone https://github.com/your-username/quiz-app.git
cd quiz-app

2. Create Virtual Environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

3. Install Requirements
pip install -r requirements.txt

4. Setup .env File

Create a .env file in project root:

SECRET_KEY=your_secret_key
DB_HOST_NAME=localhost
DB_USER_NAME=root
DB_PASSWORD=yourpassword
DB_NAME=quizdb

5. Setup Database

Run these SQL commands:

CREATE DATABASE quizdb;

USE quizdb;

CREATE TABLE users_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE users_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    category VARCHAR(100),
    score INT,
    finished_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users_log(id)
);

6. Run the App
python app.py


App runs on: http://127.0.0.1:5000/

🌟 Future Improvements

Add quiz difficulty levels (easy/medium/hard).

Leaderboard with top scorers.

Email/password reset functionality.

Deploy on cloud (Heroku/Render).

🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you’d like to improve.

📜 License

This project is licensed under the MIT License. 
