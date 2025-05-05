import os
from flask import Flask, request, redirect, g
import cohere  # Install with: pip install cohere
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
from flask import session, url_for

# Initialize Cohere client with API key from environment variable for security
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "z6NGR7BJwHtNMm2GKMA1OPt65K1VaXN58HTETYeV")
co = cohere.Client(COHERE_API_KEY)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")  # Needed for session management

DATABASE = 'app.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                options TEXT NOT NULL,
                answer TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                activity_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                issue TEXT NOT NULL,
                location TEXT NOT NULL,
                report_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()

init_db()

import feedparser

@app.route('/toggle_dark_mode')
def toggle_dark_mode():
    current_mode = session.get('dark_mode', False)
    session['dark_mode'] = not current_mode
    return redirect(request.referrer or url_for('home'))

def page(title, body):
    dark_mode = session.get('dark_mode', False)
    bg_color = "#121212" if dark_mode else "#e9f5f2"
    text_color = "#e9f5f2" if dark_mode else "#2c6e49"
    nav_bg = "#1f1f1f" if dark_mode else "#2c6e49"
    nav_link_color = "#d4f1e4" if dark_mode else "#d4f1e4"
    nav_link_hover = "#a1c9b9" if dark_mode else "#a1c9b9"
    card_bg = "#1e1e1e" if dark_mode else "white"
    card_shadow = "0 4px 12px rgba(255, 255, 255, 0.15)" if dark_mode else "0 4px 12px rgba(44, 110, 73, 0.15)"
    card_shadow_hover = "0 8px 20px rgba(255, 255, 255, 0.3)" if dark_mode else "0 8px 20px rgba(44, 110, 73, 0.3)"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
    <style>
        body {{
            background: {bg_color};
            color: {text_color};
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
        }}
        .navbar {{
            background-color: {nav_bg};
        }}
        .navbar-brand, .nav-link {{
            color: {nav_link_color} !important;
            font-weight: 600;
        }}
        .nav-link:hover {{
            color: {nav_link_hover} !important;
        }}
        .container {{
            max-width: 1200px;
            margin-top: 2rem;
        }}
        .dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
        }}
        .card {{
            background: {card_bg};
            border-radius: 10px;
            box-shadow: {card_shadow};
            padding: 1.5rem;
            transition: transform 0.2s ease-in-out;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: {card_shadow_hover};
        }}
        h1 {{
            color: {text_color};
            margin-bottom: 1.5rem;
        }}
        footer {{
            margin-top: 3rem;
            text-align: center;
            color: {text_color};
            font-size: 0.9rem;
            padding: 1rem 0;
            border-top: 1px solid #ccc;
        }}
        button, input, textarea {{
            border-radius: 5px;
            border: 1px solid #ccc;
            padding: 10px;
            font-size: 1rem;
            width: 100%;
            max-width: 600px;
            margin: 0.5rem 0;
        }}
        textarea {{
            height: 80px;
            resize: vertical;
        }}
        .dark-mode-toggle {{
            position: fixed;
            top: 1rem;
            right: 1rem;
            z-index: 1050;
        }}
    </style>
</head>
<body>
<nav class="navbar navbar-expand-lg">
  <div class="container">
    <a class="navbar-brand" href="/">MeteoFlow 🌿</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
      aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav ms-auto">
        <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
        <li class="nav-item"><a class="nav-link" href="/educational">Q&A</a></li>
        <li class="nav-item"><a class="nav-link" href="/quiz">Quiz</a></li>
        <li class="nav-item"><a class="nav-link" href="/report">Report</a></li>
        <li class="nav-item"><a class="nav-link" href="/assistant">Tips</a></li>
        <li class="nav-item"><a class="nav-link btn btn-sm btn-outline-light ms-2" href="/weather">Weather</a></li>
        <li class="nav-item"><a class="nav-link btn btn-sm btn-outline-light ms-2" href="/news">News</a></li>
      </ul>
    </div>
  </div>
</nav>
<a href="/toggle_dark_mode" class="btn btn-secondary dark-mode-toggle">{'Light Mode' if dark_mode else 'Dark Mode'}</a>
<div class="container">
<h1>{title}</h1>
<div class="dashboard">
{body}
</div>
</div>
<footer>
    <p>© 2025 MeteoFlow. All rights reserved.</p>
</footer>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""

@app.route('/news')
def news():
    if 'username' not in session:
        return redirect(url_for('login'))

    # List of trusted RSS feed URLs for weather and disaster news
    feed_urls = [
        "https://indianexpress.com/section/weather/",
        "https://timesofindia.indiatimes.com/city/delhi/breaking-news-today-04-may-2025-live-updates-weather-rain-temperature-delhi-gujarat-imd-badrinath-dham/liveblog/120865779.cms",
        "https://www.bbc.com/weather",
        "https://zeenews.india.com/india"
    ]

    news_items = []
    for url in feed_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:  # Limit to 5 entries per feed
            news_items.append({
                'title': entry.title,
                'link': entry.link,
                'published': entry.published if 'published' in entry else '',
                'summary': entry.summary if 'summary' in entry else ''
            })

    # Sort news items by published date descending if possible
    try:
        news_items.sort(key=lambda x: x['published'], reverse=True)
    except Exception:
        pass

    # Fetch reported incidents from database
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM reports ORDER BY report_time DESC LIMIT 10')
    reports = cursor.fetchall()

    news_html = '<h2>Live Weather and Disaster News</h2><ul class="list-group mb-4">'
    for item in news_items[:20]:  # Show top 20 news items
        news_html += f'<li class="list-group-item"><a href="{item["link"]}" target="_blank">{item["title"]}</a><br><small>{item["published"]}</small><p>{item["summary"]}</p></li>'
    news_html += '</ul>'

    # Embed live video content (YouTube live streams for weather/disaster news)
    live_video_html = """
    <h2>Live Weather and Disaster Video</h2>
    <div class="ratio ratio-16x9 mb-4">
        <iframe src="https://www.youtube.com/embed/De5KQEDX41g?si=C4iXoGD15DWQBHJd" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen" title="Live Weather News" allowfullscreen></iframe>
    </div>
    """

    reports_html = '<h2>Reported Incidents</h2>'
    if reports:
        reports_html += '<ul class="list-group">'
        for r in reports:
            reports_html += f'<li class="list-group-item">{r["issue"]} at <strong>{r["location"]}</strong> on {r["report_time"]}</li>'
        reports_html += '</ul>'
    else:
        reports_html += '<p>No reported incidents yet.</p>'

    return page("News and Reports", news_html + live_video_html + reports_html)

# Remove in-memory lists
# user_quiz_questions = []
# reports = []

# Simple user store for demonstration (username: password, role)
users = {
    "admin": {"password": "adminpass", "role": "admin"},
    "user": {"password": "userpass", "role": "user"}
}

# Configuration for OpenWeatherMap API and email alerts from environment variables
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "7457ef10ed4f085cfa1d50715b07d2ac")
AGRI_WEATHER_API_KEY = os.getenv("AGRI_WEATHER_API_KEY", WEATHER_API_KEY)  # Separate key for agriculture forecast, fallback to WEATHER_API_KEY
OPEN_METEO_API_BASE = "https://api.open-meteo.com/v1/forecast"  # Free agricultural weather API base URL
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "akitmescrop@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "MescropG@12")
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp@mailtrap.io")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", 587))
ALERT_RECIPIENTS = os.getenv("ALERT_RECIPIENTS", "surajgoswamiv1@gmail.com").split(",")

def log_user_activity(username, activity_type):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO user_activity (username, activity_type) VALUES (?, ?)', (username, activity_type))
    db.commit()


# Instructions:
# 1. Set environment variables before running the app:
#    - COHERE_API_KEY: Your Cohere API key
#    - OPENWEATHER_API_KEY: Your OpenWeatherMap API key
#    - AGRI_WEATHER_API_KEY: Your agricultural weather API key (optional)
#    - EMAIL_SENDER: Your email address for sending alerts
#    - EMAIL_PASSWORD: Your email password or app password
#    - EMAIL_SMTP_SERVER: SMTP server address (default: smtp.gmail.com)
#    - EMAIL_SMTP_PORT: SMTP server port (default: 587)
#    - ALERT_RECIPIENTS: Comma-separated list of email addresses to receive alerts
# 2. Install required packages: flask, cohere, requests
# 3. Run the app: python HF3.py

def send_email_alert(subject, message, recipients=ALERT_RECIPIENTS):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, recipients, msg.as_string())
        server.quit()
        print("Alert email sent successfully.")
    except Exception as e:
        print(f"Failed to send alert email: {e}")


def page(title, body):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
    <style>
        body {{
            background: #e9f5f2;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
        }}
        .navbar {{
            background-color: #2c6e49;
        }}
        .navbar-brand, .nav-link {{
            color: #d4f1e4 !important;
            font-weight: 600;
        }}
        .nav-link:hover {{
            color: #a1c9b9 !important;
        }}
        .container {{
            max-width: 1200px;
            margin-top: 2rem;
        }}
        .dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
        }}
        .card {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(44, 110, 73, 0.15);
            padding: 1.5rem;
            transition: transform 0.2s ease-in-out;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(44, 110, 73, 0.3);
        }}
        h1 {{
            color: #2c6e49;
            margin-bottom: 1.5rem;
        }}
        footer {{
            margin-top: 3rem;
            text-align: center;
            color: #666;
            font-size: 0.9rem;
            padding: 1rem 0;
            border-top: 1px solid #ccc;
        }}
        button, input, textarea {{
            border-radius: 5px;
            border: 1px solid #ccc;
            padding: 10px;
            font-size: 1rem;
            width: 100%;
            max-width: 600px;
            margin: 0.5rem 0;
        }}
        textarea {{
            height: 80px;
            resize: vertical;
        }}
    </style>
</head>
<body>
<nav class="navbar navbar-expand-lg">
  <div class="container">
    <a class="navbar-brand" href="/">MeteoFlow 🌿</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
      aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav ms-auto">
        <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
        <li class="nav-item"><a class="nav-link" href="/educational">Q&A</a></li>
        <li class="nav-item"><a class="nav-link" href="/quiz">Quiz</a></li>
        <li class="nav-item"><a class="nav-link" href="/report">Report</a></li>
        <li class="nav-item"><a class="nav-link" href="/assistant">Tips</a></li>
        <li class="nav-item"><a class="nav-link btn btn-sm btn-outline-light ms-2" href="/weather">Weather</a></li>
        <li class="nav-item"><a class="nav-link btn btn-sm btn-outline-light ms-2" href="/news">News</a></li>
      </ul>
    </div>
  </div>
</nav>
<div class="container">
<h1>{title}</h1>
<div class="dashboard">
{body}
</div>
</div>
<footer>
    <p>© 2025 MeteoFlow. All rights reserved.</p>
</footer>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""


def query_model(prompt, max_tokens=512):
    try:
        response = co.generate(
            model="command-xlarge",
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.generations[0].text.strip()
    except Exception as e:
        return f"Error: {e}"


@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    cards = [
        {
            "title": "Educational Q&A",
            "description": "Ask questions about climate and sustainability.",
            "link": "/educational",
            "btn_text": "Go to Q&A"
        },
        {
            "title": "Interactive Quiz",
            "description": "Test your knowledge with quizzes.",
            "link": "/quiz",
            "btn_text": "Take Quiz"
        },
        {
            "title": "Report Issues",
            "description": "Report environmental issues in your area.",
            "link": "/report",
            "btn_text": "Report Now"
        },
        {
            "title": "Eco Tips",
            "description": "Get daily tips to help the environment.",
            "link": "/assistant",
            "btn_text": "View Tips"
        },
        {
            "title": "Weather Alerts",
            "description": "Check weather and disaster alerts.",
            "link": "/weather",
            "btn_text": "Check Weather"
        },
        {
            "title": "Sustainable Development Goals",
            "description": "Explore the UN Sustainable Development Goals and related resources.",
            "link": "/sdgs",
            "btn_text": "Explore SDGs"
        }
    ]
    banner_html = '<div class="alert alert-info text-center mb-4"><strong>New:</strong> Sustainable Development Goals Section Added!</div>'
    card_html = ""
    for card in cards:
        card_html += f'''
        <div class="card">
            <h3>{card["title"]}</h3>
            <p>{card["description"]}</p>
            <a href="{card["link"]}" class="btn btn-success">{card["btn_text"]}</a>
        </div>
        '''
    return page("MeteoFlow Helper Dashboard", banner_html + card_html)


@app.route('/educational', methods=['GET', 'POST'])
def educational():
    response = ""
    if request.method == 'POST':
        user_question = request.form['question']
        try:
            max_tokens = int(request.form.get('max_tokens') or 512)
            max_tokens = max(50, min(max_tokens, 2048))
            prompt = f"Answer this question concisely: {user_question}"
            response = query_model(prompt, max_tokens)
        except Exception as e:
            response = f"Error: {e}"

    form = f"""
    <form method="post" class="mb-3">
        <input name="question" placeholder="Ask about climate, sustainability..." required class="form-control mb-2" />
        <input name="max_tokens" type="number" placeholder="Max tokens (50-2048)" value="512" min="50" max="2048" class="form-control mb-2" />
        <button type="submit" class="btn btn-success">Ask</button>
    </form>
    """
    response_html = f'<div class="alert alert-info mt-3">{response}</div>' if response else ""
    return page("Educational Q&A", form + response_html)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']
            log_user_activity(username, 'login')
            return redirect(url_for('home'))
        else:
            error = "Invalid username or password"
            return page("Login", f"<p style='color:red;'>{error}</p>" + login_form())
    return login_form()

def login_form():
    return """
    <div class="d-flex justify-content-center align-items-center" style="height: 80vh; background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);">
      <form method="post" class="p-5 border rounded shadow" style="min-width: 320px; max-width: 400px; width: 100%; background-color: white;">
        <h2 class="mb-4 text-center" style="color: #2c6e49; font-weight: 700; letter-spacing: 1px;">MeteoFlow Login</h2>
        <div class="mb-3">
          <label for="username" class="form-label" style="font-weight: 600;">Username</label>
          <input id="username" name="username" placeholder="Enter username" required class="form-control" />
        </div>
        <div class="mb-3">
          <label for="password" class="form-label" style="font-weight: 600;">Password</label>
          <input id="password" name="password" type="password" placeholder="Enter password" required class="form-control" />
        </div>
        <button type="submit" class="btn btn-success w-100 fw-bold">Login</button>
      </form>
    </div>
    """

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'username' not in session:
        return redirect(url_for('login'))

    role = session.get('role', 'user')
    username = session.get('username')

    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        if 'add_question' in request.form:
            if role != 'admin':
                return page("Unauthorized", "<p>You do not have permission to add questions.</p>")
            question = request.form['question']
            correct_answer = request.form['correct_answer'].strip()
            options = [opt.strip() for opt in request.form['options'].split(",")]
            options_str = ", ".join(options)
            cursor.execute('INSERT INTO quiz_questions (question, options, answer) VALUES (?, ?, ?)', (question, options_str, correct_answer))
            db.commit()
            return redirect('/quiz')
        elif 'delete_question' in request.form:
            if role != 'admin':
                return page("Unauthorized", "<p>You do not have permission to delete questions.</p>")
            try:
                index = int(request.form['delete_question'])
                cursor.execute('SELECT id FROM quiz_questions ORDER BY id')
                rows = cursor.fetchall()
                if 0 <= index < len(rows):
                    question_id = rows[index]['id']
                    cursor.execute('DELETE FROM quiz_questions WHERE id = ?', (question_id,))
                    db.commit()
            except (ValueError, IndexError):
                pass
            return redirect('/quiz')
        elif 'edit_question' in request.form:
            if role != 'admin':
                return page("Unauthorized", "<p>You do not have permission to edit questions.</p>")
            try:
                question_id = int(request.form['edit_question'])
                question = request.form['question']
                correct_answer = request.form['correct_answer']
                options = [opt.strip() for opt in request.form['options'].split(",")]
                options_str = ",".join(options)
                cursor.execute('UPDATE quiz_questions SET question = ?, options = ?, answer = ? WHERE id = ?', (question, options_str, correct_answer, question_id))
                db.commit()
            except (ValueError, KeyError):
                pass
            return redirect('/quiz')
        else:
            score = 0
            cursor.execute('SELECT * FROM quiz_questions ORDER BY id')
            questions = cursor.fetchall()
            for i, q in enumerate(questions):
                submitted_answer = request.form.get(f'q{i}', '').strip()
                correct_answer = q['answer'].strip()
                if submitted_answer == correct_answer:
                    score += 1
            log_user_activity(username, 'quiz_attempt')
            result_html = f'<div class="alert alert-success">Your score: {score}/{len(questions)}</div>'
            retry_link = '<a href="/quiz" class="btn btn-outline-primary mt-3">Try again</a>'
            return page("Quiz Result", result_html + retry_link)

    form = ""
    edit_id = request.args.get('edit_id', type=int)
    if role == 'admin':
        form += f"""
        <h3>Manage Quiz Questions (Admin View)</h3>
        <p><em>Logged in as admin: {username}</em></p>
        <ul class="list-group mb-4">
        """
        cursor.execute('SELECT * FROM quiz_questions ORDER BY id')
        questions = cursor.fetchall()
        for i, q in enumerate(questions):
            options = q['options'].split(",")
            if edit_id == q['id']:
                # Show edit form for this question
                form += f'''
                <li class="list-group-item">
                    <form method="post" class="mb-3">
                        <input type="hidden" name="edit_question" value="{q['id']}" />
                        <input name="question" value="{q['question']}" required class="form-control mb-2" />
                        <input name="options" value="{q['options']}" required class="form-control mb-2" />
                        <input name="correct_answer" value="{q['answer']}" required class="form-control mb-2" />
                        <button type="submit" class="btn btn-primary btn-sm me-2">Save</button>
                        <a href="/quiz" class="btn btn-secondary btn-sm">Cancel</a>
                    </form>
                </li>
                '''
            else:
                form += f'''
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <strong>{q["question"]}</strong><br>
                        Options: {", ".join(options)}<br>
                        Correct Answer: {q["answer"]}
                    </div>
                    <div>
                        <form method="post" style="display:inline;">
                            <input type="hidden" name="delete_question" value="{i}" />
                            <button type="submit" class="btn btn-danger btn-sm me-2" style="min-width: 80px;">Delete</button>
                        </form>
                        <a href="/quiz?edit_id={q['id']}" class="btn btn-warning btn-sm" style="min-width: 80px;">Edit</a>
                    </div>
                </li>
                '''
        form += "</ul>"

        form += """
        <h3>Add a New Quiz Question</h3>
        <form method="post" class="mb-4">
            <input type="hidden" name="add_question" value="1" />
            <input name="question" placeholder="Enter question" required class="form-control mb-2" />
            <input name="options" placeholder="Enter options (comma-separated)" required class="form-control mb-2" />
            <input name="correct_answer" placeholder="Correct answer" required class="form-control mb-2" />
            <button type="submit" class="btn btn-success">Add Question</button>
        </form>
        <hr />
        """

    cursor.execute('SELECT * FROM quiz_questions ORDER BY id')
    questions = cursor.fetchall()
    if questions:
        form += '<h3>Take the Quiz</h3><form method="post">'
        for i, q in enumerate(questions):
            options = q['options'].split(",")
            form += f'<p><b>{q["question"]}</b><br>'
            for opt in options:
                form += f'<div class="form-check"><input class="form-check-input" type="radio" name="q{i}" value="{opt}" id="q{i}_{opt}" required><label class="form-check-label" for="q{i}_{opt}">{opt}</label></div>'
            form += '</p>'
        form += '<button type="submit" class="btn btn-primary">Submit Quiz</button></form>'
    else:
        form += '<p>No quiz questions added yet.</p>'

    return page("Interactive Quiz", form)


@app.route('/report', methods=['GET', 'POST'])
def report():
    if 'username' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        issue = request.form['issue']
        location = request.form['location']
        cursor.execute('INSERT INTO reports (issue, location) VALUES (?, ?)', (issue, location))
        db.commit()
        return redirect('/report')

    cursor.execute('SELECT * FROM reports ORDER BY report_time DESC')
    reports = cursor.fetchall()

    report_list = ""
    if reports:
        report_list = '<ul class="list-group mb-3">'
        for i, r in enumerate(reports, 1):
            report_list += f'<li class="list-group-item">#{i}: {r["issue"]} at <strong>{r["location"]}</strong></li>'
        report_list += '</ul>'
    else:
        report_list = '<p>No reports yet.</p>'

    form = """
    <form method="post" class="mb-4">
        <textarea name="issue" placeholder="Describe the issue" required class="form-control mb-2"></textarea>
        <input name="location" placeholder="Location" required class="form-control mb-2" />
        <button type="submit" class="btn btn-success">Report</button>
    </form>
    """
    return page("Report Environmental Issue", form + report_list)


@app.route('/assistant')
def assistant():
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        tip = query_model("Give me one random environmental tip.", max_tokens=80)
    except Exception as e:
        tip = f"Error getting tip: {e}"
    return page("Eco Tip", f'<div class="alert alert-success p-3">🌿 {tip}</div>')


# New route for weather and disaster alerts
@app.route('/weather', methods=['GET', 'POST'])
def weather():
    if 'username' not in session:
        return redirect(url_for('login'))

    weather_info = None
    alert_message = None
    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
            try:
                response = requests.get(url)
                data = response.json()
                if data.get('cod') != 200:
                    alert_message = f"City not found: {city}"
                else:
                    weather_info = {
                        'city': data['name'],
                        'temperature': data['main']['temp'],
                        'description': data['weather'][0]['description'],
                        'rain': any(w['main'].lower() == 'rain' for w in data['weather']),
                        'alerts': []
                    }
                    # Check for rain or severe weather to send alert
                    if weather_info['rain']:
                        alert_message = f"Rain alert for {weather_info['city']}! Stay safe."
                        send_email_alert(f"Rain Alert for {weather_info['city']}", alert_message)
                    # Additional disaster alerts can be added here based on weather data
            except Exception as e:
                alert_message = f"Error fetching weather data: {e}"

    form = """
    <form method="post" class="mb-3">
        <input name="city" placeholder="Enter city name" required class="form-control mb-2" />
        <button type="submit" class="btn btn-primary">Get Weather</button>
    </form>
    """

    weather_html = ""
    if weather_info:
        weather_html = f"""
        <div class="alert alert-info">
            🌍 <strong>{weather_info['city']}</strong><br>
            🌡 Temperature: {weather_info['temperature']}°C<br>
            ☁️ Condition: {weather_info['description'].capitalize()}<br>
            💧 Humidity: {data['main']['humidity']}%<br>
            🌬 Wind Speed: {data['wind']['speed']} m/s
        </div>
        """

    alert_html = f'<div class="alert alert-warning">{alert_message}</div>' if alert_message else ""

    extra_links = '''
    <div class="mt-4">
        <a href="/weather/live_map" class="btn btn-info me-2">Live Weather Map</a>
        <a href="/weather/forecast" class="btn btn-info me-2">Weather Forecast</a>
        <a href="/weather/history" class="btn btn-info me-2">Weather History</a>
        <a href="/weather/agriculture" class="btn btn-info">Agricultural Weather</a>
    </div>
    '''

    return page("Weather and Disaster Alerts", form + alert_html + weather_html + extra_links)

@app.route('/weather/live_map')
def weather_live_map():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Embed OpenWeatherMap's live weather map iframe
    iframe_html = """
    <h2>Live Weather Map</h2>
    <iframe src="https://openweathermap.org/weathermap?basemap=map&cities=true&layer=temperature&lat=20&lon=0&zoom=2" 
    width="1000" height="700" style="border:none;"></iframe>
    <div class="mt-3">
        <a href="/weather" class="btn btn-secondary">Back to Weather</a>
    </div>
    """
    return page("Live Weather Map", iframe_html)

@app.route('/weather/forecast', methods=['GET', 'POST'])
def weather_forecast():
    if 'username' not in session:
        return redirect(url_for('login'))

    forecast_data = None
    alert_message = None
    city = None
    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric"
            try:
                response = requests.get(url)
                data = response.json()
                if data.get('cod') != "200":
                    alert_message = f"City not found or error: {city}"
                else:
                    forecast_data = data['list']  # List of forecast entries
            except Exception as e:
                alert_message = f"Error fetching forecast data: {e}"

    form = """
    <form method="post" class="mb-3">
        <input name="city" placeholder="Enter city name" value="{city}" required class="form-control mb-2" />
        <button type="submit" class="btn btn-primary">Get Forecast</button>
    </form>
    """.format(city=city or "")

    forecast_html = ""
    if forecast_data:
        forecast_html += '<h3>5-Day / 3-Hour Forecast</h3><div class="list-group">'
        for entry in forecast_data[:16]:  # Show next 2 days approx
            dt_txt = entry['dt_txt']
            temp = entry['main']['temp']
            desc = entry['weather'][0]['description'].capitalize()
            forecast_html += f'<div class="list-group-item">{dt_txt}: {temp}°C, {desc}</div>'
        forecast_html += '</div>'

    alert_html = f'<div class="alert alert-warning">{alert_message}</div>' if alert_message else ""

    back_link = '<a href="/weather" class="btn btn-secondary mt-3">Back to Weather</a>'

    return page("Weather Forecast", form + alert_html + forecast_html + back_link)

@app.route('/weather/history', methods=['GET', 'POST'])
def weather_history():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Note: OpenWeatherMap historical data requires paid plan.
    # Here we simulate by showing recent weather data for past 5 days using current weather API for demo.

    history_data = []
    alert_message = None
    city = None
    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            try:
                # For demo, get current weather multiple times with delay or simulate
                # Here we just call current weather once and replicate for demo
                url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
                response = requests.get(url)
                data = response.json()
                if data.get('cod') != 200:
                    alert_message = f"City not found: {city}"
                else:
                    for i in range(5):
                        history_data.append({
                            'date': f"Day -{i+1}",
                            'temp': data['main']['temp'],
                            'desc': data['weather'][0]['description'].capitalize()
                        })
            except Exception as e:
                alert_message = f"Error fetching history data: {e}"

    form = """
    <form method="post" class="mb-3">
        <input name="city" placeholder="Enter city name" value="{city}" required class="form-control mb-2" />
        <button type="submit" class="btn btn-primary">Get History</button>
    </form>
    """.format(city=city or "")

    history_html = ""
    if history_data:
        history_html += '<h3>Recent Weather History (Simulated)</h3><ul class="list-group">'
        for entry in history_data:
            history_html += f'<li class="list-group-item">{entry["date"]}: {entry["temp"]}°C, {entry["desc"]}</li>'
        history_html += '</ul>'

    alert_html = f'<div class="alert alert-warning">{alert_message}</div>' if alert_message else ""

    back_link = '<a href="/weather" class="btn btn-secondary mt-3">Back to Weather</a>'

    return page("Weather History", form + alert_html + history_html + back_link)

@app.route('/weather/agriculture', methods=['GET', 'POST'])
def weather_agriculture():
    if 'username' not in session:
        return redirect(url_for('login'))

    alert_message = None
    city = None
    agri_alerts = []
    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            try:
                url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
                response = requests.get(url)
                data = response.json()
                if data.get('cod') != 200:
                    alert_message = f"City not found: {city}"
                else:
                    temp = data['main']['temp']
                    weather_desc = data['weather'][0]['description'].lower()
                    wind_speed = data['wind']['speed']
                    humidity = data['main']['humidity']

                    # Simple agricultural alerts logic
                    if temp < 0:
                        agri_alerts.append("Frost alert: Temperature below freezing. Protect your crops!")
                    if 'rain' in weather_desc:
                        agri_alerts.append("Rain alert: Expect rain. Prepare for wet conditions.")
                    if wind_speed > 10:
                        agri_alerts.append("High wind alert: Strong winds expected. Secure loose items.")
                    if humidity < 30:
                        agri_alerts.append("Low humidity alert: Dry conditions. Consider irrigation.")

                    if not agri_alerts:
                        agri_alerts.append("No significant agricultural alerts at this time.")

                    # Send email alert to farmers if any alerts
                    if agri_alerts:
                        alert_text = "\\n".join(agri_alerts)
                        send_email_alert(f"Agricultural Weather Alerts for {city}", alert_text)

            except Exception as e:
                alert_message = f"Error fetching agricultural weather data: {e}"

    form = """
    <form method="post" class="mb-3">
        <input name="city" placeholder="Enter city name" value="{city}" required class="form-control mb-2" />
        <button type="submit" class="btn btn-primary">Get Agricultural Weather</button>
    </form>
    """.format(city=city or "")

    alerts_html = ""
    if agri_alerts:
        alerts_html += '<h3>Agricultural Weather Alerts</h3><ul class="list-group">'
        for alert in agri_alerts:
            alerts_html += f'<li class="list-group-item">{alert}</li>'
        alerts_html += '</ul>'

    alert_html = f'<div class="alert alert-warning">{alert_message}</div>' if alert_message else ""

    back_link = '<a href="/weather" class="btn btn-secondary mt-3">Back to Weather</a>'

    return page("Agricultural Weather Forecast", form + alert_html + alerts_html + back_link)


@app.route('/sdgs')
def sdgs():
    sdg_list = [
        "No Poverty",
        "Zero Hunger",
        "Good Health & well-Being",
        "Quality Education",
        "Gender Equality",
        "Clean Water & Sanitation",
        "Affordable & Clean Energy",
        "Decent Work & Economic Growth",
        "Industry, Innovation & Infrastructure",
        "Reduced Inequalities",
        "Responsible Consumption & Production",
        "Sustainable Cities and Communities",
        "Climate Action",
        "Life Below Water",
        "Life on Land",
        "Peace, Justice and Strong Institutions"
    ]
    sdg_cards = ""
    for sdg in sdg_list:
        sdg_cards += f'''
        <div class="card">
            <h3>{sdg}</h3>
            <p>Learn about {sdg} and explore related resources and tools.</p>
            <a href="/sdgs/{sdg.replace(' ', '_').replace('&', 'and').replace(',', '')}" class="btn btn-primary">Explore</a>
        </div>
        '''
    return page("UN Sustainable Development Goals", sdg_cards)

@app.route('/sdgs/<sdg_name>')
def sdg_detail(sdg_name):
    sdg_display_name = sdg_name.replace('_', ' ').replace('and', '&')

    sdg_details = {
        "No Poverty": {
            "description": "End poverty in all its forms everywhere.",
            "resources": [
                {"name": "UN SDG No Poverty", "url": "https://sdgs.un.org/goals/goal1"},
                {"name": "World Bank Poverty Overview", "url": "https://www.worldbank.org/en/topic/poverty/overview"}
            ]
        },
        "Zero Hunger": {
            "description": "End hunger, achieve food security and improved nutrition, and promote sustainable agriculture.",
            "resources": [
                {"name": "UN SDG Zero Hunger", "url": "https://sdgs.un.org/goals/goal2"},
                {"name": "FAO Food Security", "url": "https://www.fao.org/food-security/en/"}
            ]
        },
        "Good Health & well-Being": {
            "description": "Ensure healthy lives and promote well-being for all at all ages.",
            "resources": [
                {"name": "UN SDG Good Health", "url": "https://sdgs.un.org/goals/goal3"},
                {"name": "WHO Health Topics", "url": "https://www.who.int/health-topics"}
            ]
        },
        "Quality Education": {
            "description": "Ensure inclusive and equitable quality education and promote lifelong learning opportunities for all.",
            "resources": [
                {"name": "UN SDG Quality Education", "url": "https://sdgs.un.org/goals/goal4"},
                {"name": "UNESCO Education", "url": "https://en.unesco.org/themes/education"}
            ]
        },
        "Gender Equality": {
            "description": "Achieve gender equality and empower all women and girls.",
            "resources": [
                {"name": "UN SDG Gender Equality", "url": "https://sdgs.un.org/goals/goal5"},
                {"name": "UN Women", "url": "https://www.unwomen.org/en"}
            ]
        },
        "Clean Water & Sanitation": {
            "description": "Ensure availability and sustainable management of water and sanitation for all.",
            "resources": [
                {"name": "UN SDG Clean Water", "url": "https://sdgs.un.org/goals/goal6"},
                {"name": "UN Water", "url": "https://www.unwater.org/"}
            ]
        },
        "Affordable & Clean Energy": {
            "description": "Ensure access to affordable, reliable, sustainable and modern energy for all.",
            "resources": [
                {"name": "UN SDG Clean Energy", "url": "https://sdgs.un.org/goals/goal7"},
                {"name": "IRENA", "url": "https://www.irena.org/"}
            ]
        },
        "Decent Work & Economic Growth": {
            "description": "Promote sustained, inclusive and sustainable economic growth, full and productive employment and decent work for all.",
            "resources": [
                {"name": "UN SDG Decent Work", "url": "https://sdgs.un.org/goals/goal8"},
                {"name": "ILO", "url": "https://www.ilo.org/global/lang--en/index.htm"}
            ]
        },
        "Industry, Innovation & Infrastructure": {
            "description": "Build resilient infrastructure, promote inclusive and sustainable industrialization and foster innovation.",
            "resources": [
                {"name": "UN SDG Industry", "url": "https://sdgs.un.org/goals/goal9"},
                {"name": "UNIDO", "url": "https://www.unido.org/"}
            ]
        },
        "Reduced Inequalities": {
            "description": "Reduce inequality within and among countries.",
            "resources": [
                {"name": "UN SDG Reduced Inequalities", "url": "https://sdgs.un.org/goals/goal10"},
                {"name": "UN DESA", "url": "https://www.un.org/development/desa/en/"}
            ]
        },
        "Responsible Consumption & Production": {
            "description": "Ensure sustainable consumption and production patterns.",
            "resources": [
                {"name": "UN SDG Responsible Consumption", "url": "https://sdgs.un.org/goals/goal12"},
                {"name": "UNEP", "url": "https://www.unep.org/"}
            ]
        },
        "Sustainable Cities and Communities": {
            "description": "Make cities and human settlements inclusive, safe, resilient and sustainable.",
            "resources": [
                {"name": "UN SDG Sustainable Cities", "url": "https://sdgs.un.org/goals/goal11"},
                {"name": "UN Habitat", "url": "https://unhabitat.org/"}
            ]
        },
        "Climate Action": {
            "description": "Take urgent action to combat climate change and its impacts.",
            "resources": [
                {"name": "UN SDG Climate Action", "url": "https://sdgs.un.org/goals/goal13"},
                {"name": "UNFCCC", "url": "https://unfccc.int/"}
            ]
        },
        "Life Below Water": {
            "description": "Conserve and sustainably use the oceans, seas and marine resources for sustainable development.",
            "resources": [
                {"name": "UN SDG Life Below Water", "url": "https://sdgs.un.org/goals/goal14"},
                {"name": "UN Ocean", "url": "https://www.un.org/en/our-work/oceans"}
            ]
        },
        "Life on Land": {
            "description": "Protect, restore and promote sustainable use of terrestrial ecosystems, sustainably manage forests, combat desertification, and halt and reverse land degradation and halt biodiversity loss.",
            "resources": [
                {"name": "UN SDG Life on Land", "url": "https://sdgs.un.org/goals/goal15"},
                {"name": "UNEP Biodiversity", "url": "https://www.unep.org/explore-topics/biodiversity"}
            ]
        },
        "Peace, Justice and Strong Institutions": {
            "description": "Promote peaceful and inclusive societies for sustainable development, provide access to justice for all and build effective, accountable and inclusive institutions at all levels.",
            "resources": [
                {"name": "UN SDG Peace and Justice", "url": "https://sdgs.un.org/goals/goal16"},
                {"name": "UNODC", "url": "https://www.unodc.org/"}
            ]
        }
    }

    sdg_info = sdg_details.get(sdg_display_name, None)
    if sdg_info:
        resources_html = "<ul>"
        for res in sdg_info["resources"]:
            resources_html += f'<li><a href="{res["url"]}" target="_blank" rel="noopener">{res["name"]}</a></li>'
        resources_html += "</ul>"

        content = f"""
        <h2>{sdg_display_name}</h2>
        <p>{sdg_info['description']}</p>
        <h3>Resources</h3>
        {resources_html}
        <a href="/sdgs" class="btn btn-secondary mt-3">Back to SDGs</a>
        """
    else:
        content = f"""
        <h2>{sdg_display_name}</h2>
        <p>Information about this SDG is not available yet.</p>
        <a href="/sdgs" class="btn btn-secondary mt-3">Back to SDGs</a>
        """

    return page(f"SDG: {sdg_display_name}", content)

@app.route('/farmers', methods=['GET', 'POST'])
def farmers():
    # Ensure user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))

    alert_message = None
    city_name = None
    agricultural_alerts = []

    # Fun and easy tips for farmers to tackle weather and disasters
    farmer_tips = [
        "🌞 Keep an eye on the weather forecast – it's like your crop's daily horoscope!",
        "❄️ Use covers or sprinklers to keep your plants cozy during frosty nights.",
        "💧 Make sure water drains well to avoid soggy roots after heavy rains.",
        "🌳 Plant some trees as windbreakers – your crops will thank you!",
        "🌾 Store your seeds and fertilizers in a safe, dry spot.",
        "📞 Stay connected with local farm experts for handy advice.",
        "🌈 Try growing different crops to keep your farm happy and healthy.",
        "🌱 Take care of your soil – it's the secret to great harvests!",
        "🚿 Water your plants smartly during dry spells.",
        "⚡ Have a quick plan ready for any weather surprises!"
    ]

    if request.method == 'POST':
        city_name = request.form.get('city')
        if city_name:
            try:
                # Call OpenWeatherMap API to get current weather data for the city
                weather_api_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={WEATHER_API_KEY}&units=metric"
                response = requests.get(weather_api_url)
                weather_data = response.json()

                if weather_data.get('cod') != 200:
                    alert_message = f"Oops! City '{city_name}' not found. Double-check the name and try again."
                else:
                    temp_celsius = weather_data['main']['temp']
                    weather_description = weather_data['weather'][0]['description'].lower()
                    wind_speed_mps = weather_data['wind']['speed']
                    humidity_percent = weather_data['main']['humidity']

                    # Generate simple agricultural alerts based on weather conditions
                    if temp_celsius < 0:
                        agricultural_alerts.append("🥶 Frost alert! Time to protect your crops from the chill.")
                    if 'rain' in weather_description:
                        agricultural_alerts.append("🌧 Rain alert! Get ready for some wet weather.")
                    if wind_speed_mps > 10:
                        agricultural_alerts.append("💨 Wind alert! Secure anything that might blow away.")
                    if humidity_percent < 30:
                        agricultural_alerts.append("🌵 Dry air alert! Your plants might need a drink.")

                    if not agricultural_alerts:
                        agricultural_alerts.append("🌟 All clear! No major weather worries for now.")

            except Exception as error:
                alert_message = f"Uh-oh! Couldn't fetch weather info: {error}"

    # HTML form for city input
    form_html = f"""
    <form method="post" class="mb-3">
        <input name="city" placeholder="Enter city name" value="{city_name or ''}" required class="form-control mb-2" />
        <button type="submit" class="btn btn-primary">Get Agricultural Alerts</button>
    </form>
    """

    # Display agricultural alerts if any
    alerts_html = ""
    if agricultural_alerts:
        alerts_html += '<h3>Agricultural Weather Alerts</h3><ul class="list-group mb-4">'
        for alert in agricultural_alerts:
            alerts_html += f'<li class="list-group-item">{alert}</li>'
        alerts_html += '</ul>'

    # Display tips for farmers
    tips_html = '<h3>Easy & Fun Tips to Tackle Weather & Disasters</h3><ul class="list-group mb-4">'
    for tip in farmer_tips:
        tips_html += f'<li class="list-group-item">{tip}</li>'
    tips_html += '</ul>'

    # Benefits information for farmers
    benefits_html = """
    <h3>Why Farmers Love This</h3>
    <ul class="list-group">
        <li class="list-group-item">Get timely weather alerts to keep your crops safe and sound.</li>
        <li class="list-group-item">Handy tips that make farming easier and more fun.</li>
        <li class="list-group-item">Email alerts so you never miss important updates.</li>
        <li class="list-group-item">Support from local farm experts and community resources.</li>
    </ul>
    """

    # Display any alert messages
    alert_html = f'<div class="alert alert-warning">{alert_message}</div>' if alert_message else ""

    # Link to go back to the main dashboard
    back_link_html = '<a href="/" class="btn btn-secondary mt-3">Back to Dashboard</a>'

    # Combine all parts into the page content
    full_content = form_html + alert_html + alerts_html + tips_html + benefits_html + back_link_html

    return page("Farmers' Disaster and Weather Alerts", full_content)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=5001)
