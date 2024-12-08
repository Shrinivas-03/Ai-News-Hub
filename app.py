from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import requests
from flask_mail import Mail, Message
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from transformers import pipeline
import os
from dotenv import load_dotenv
import random
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# NewsAPI Configuration
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
NEWSAPI_URL = "https://newsapi.org/v2/top-headlines"

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

app.config['MAIL_SERVER'] = 'smtp.gmail.com' 
app.config['MAIL_PORT'] = 587 
app.config['MAIL_USE_TLS'] = True 
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME') 
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
mail = Mail(app)

# SQLite3 Database Path
DATABASE = 'news_app.db'

# Helper function to interact with SQLite
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Fetch news from NewsAPI
def fetch_news(category="general"):
    params = {
        "apiKey": NEWSAPI_KEY,
        "category": category,
        "language": "en",
        "country": "us"
    }
    try:
        response = requests.get(NEWSAPI_URL, params=params)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
        
        # Filter articles with at least 150 characters in their content
        filtered_articles = [article for article in articles if article.get("content") and len(article["content"]) >= 50]
        return filtered_articles
    except requests.exceptions.RequestException as e:
        app.logger.error(f'Error fetching news: {str(e)}')
        return None

# Routes
@app.route('/')
def index():
    if 'loggedin' in session:
        return render_template('index.html', loggedin=True, name=session['name'])
    return redirect(url_for('login'))

@app.route('/latest-news', methods=["GET"])
def get_latest_news():
    category = request.args.get("category", "general")
    news_data = fetch_news(category)
    if news_data:
        return jsonify({"articles": news_data})
    return jsonify({"error": "Unable to fetch news"})

@app.route('/categories')
def categories():
    return render_template('categories.html', loggedin='loggedin' in session, name=session.get('name'))

@app.route('/saved')
def saved():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    user_id = session['id']
    conn = get_db_connection()
    saved_articles = conn.execute('SELECT * FROM saved_articles WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    return render_template('saved.html', articles=saved_articles)


@app.route('/save_article', methods=['POST'])
def save_article():
    if 'loggedin' not in session:
        return jsonify({'error': 'User not logged in'})
    
    user_id = session['id']
    data = request.json
    title = data.get('title')
    url = data.get('url')
    urlToImage = data.get('urlToImage')  # Ensure this line is present
    
    conn = get_db_connection()
    conn.execute('INSERT INTO saved_articles (user_id, title, url, urlToImage) VALUES (?, ?, ?, ?)', 
                 (user_id, title, url, urlToImage))
    conn.commit()
    conn.close()
    return jsonify({'success': 'Article saved'})

@app.route('/summarize_article', methods=['POST'])
def summarize_article():
    data = request.json
    article_content = data.get('content')

    if article_content:
        max_input_length = 10000
        article_content = article_content[:max_input_length]

        try:
            summary = summarizer(article_content, max_length=100, min_length=35, do_sample=False)
            return jsonify({'summary': summary[0]['summary_text']})
        except Exception as e:
            app.logger.error(f'Summarization error: {str(e)}')
            return jsonify({'error': f'Summarization error: {str(e)}'})
    return jsonify({'error': 'No content provided for summarization'})

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        date_of_birth = request.form['date_of_birth']
        otp = random.randint(100000, 999999)

        conn = get_db_connection()
        account = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if account:
            flash('Account already exists!', 'error')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!', 'error')
        elif not name or not password or not email or not date_of_birth:
            flash('Please fill out the form!', 'error')
        else:
            try:
                conn.execute('INSERT INTO users (name, email, password, date_of_birth, otp) VALUES (?, ?, ?, ?, ?)', 
                             (name, email, password, date_of_birth, otp))
                conn.commit()
                conn.close()

                # Send OTP to the user's email
                msg = Message('Your OTP for Registration', sender='noreply@demo.com', recipients=[email])
                msg.body = f'Your OTP is {otp}'
                mail.send(msg)

                session['email'] = email
                flash('OTP has been sent to your email. Please verify.', 'success')
                return redirect(url_for('verify_otp'))
            except Exception as e:
                flash(f'Error during registration: {e}', 'error')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        account = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if account and check_password_hash(account['password'], password):
            session['loggedin'] = True
            session['id'] = account['id']
            session['name'] = account['name']
            return redirect(url_for('index'))
        else:
            flash('Incorrect username/password!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    return redirect(url_for('login'))

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        email = session.get('email')
        input_otp = request.form['otp']

        conn = get_db_connection()
        account = conn.execute('SELECT * FROM users WHERE email = ? AND otp = ?', (email, input_otp)).fetchone()

        if account:
            conn.execute('UPDATE users SET otp = NULL WHERE email = ?', (email,))
            conn.commit()
            conn.close()
            flash('Your account has been verified successfully!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP. Please try again.', 'error')
    return render_template('verify_otp.html')


if __name__ == '__main__':
    # Initialize database if not exists
    with get_db_connection() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                date_of_birth DATE NOT NULL,
                otp TEXT
            );
            CREATE TABLE IF NOT EXISTS saved_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                urlToImage TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        ''')
    app.run(debug=True)
