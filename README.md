# News Summarizer Web App

This project is a **News Summarizer Web Application** built using Flask, SQLite, and NLP-based summarization models. Users can browse the latest news, save articles, and generate AI-based summaries for quick reading. The app includes features like user authentication, email-based OTP verification, and saved article management.

---

## Features

1. **User Authentication**
   - Sign up with email verification via OTP.
   - Secure login with password hashing using `werkzeug.security`.
   - Logout functionality.

2. **News Fetching**
   - Fetch top headlines from NewsAPI based on categories.
   - Filter articles with sufficient content for better summarization.

3. **AI-Powered News Summarization**
   - Use `transformers` pipeline with the `facebook/bart-large-cnn` model.
   - Summarize long news articles into concise and readable summaries.

4. **Article Management**
   - Save articles for future reference.
   - View saved articles on a dedicated page.

5. **Email Integration**
   - Send OTPs to users for email verification.

6. **Database Management**
   - SQLite3 database for user data and saved articles.

---

## Tech Stack

- **Backend:** Flask
- **Database:** SQLite3
- **Email Integration:** Flask-Mail
- **AI Summarization:** Hugging Face Transformers
- **Frontend:** HTML, CSS, Jinja Templates
- **APIs:** NewsAPI

---

## Installation Guide

### Prerequisites

1. Python 3.8+
2. Virtual environment (optional but recommended)

### Steps to Install

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/news-summarizer.git
   cd news-summarizer
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate    # On Linux/Mac
   venv\Scripts\activate       # On Windows
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory:
   ```plaintext
   SECRET_KEY=your_secret_key
   NEWSAPI_KEY=your_newsapi_key
   MAIL_USERNAME=your_email@example.com
   MAIL_PASSWORD=your_email_password
   ```

5. Initialize the SQLite3 database:
   ```bash
   python app.py
   ```

6. Run the application:
   ```bash
   python app.py
   ```

7. Visit the app at `http://127.0.0.1:5000`.

---

## Project Structure

```plaintext
news-summarizer/
├── templates/         # HTML templates
├── static/            # Static files (CSS, JS)
├── app.py             # Main Flask application
├── news_app.db        # SQLite database
├── requirements.txt   # Python dependencies
├── .env               # Environment variables
└── README.md          # Documentation
```

---

## Usage

1. **Sign Up:** Register an account and verify using the OTP sent to your email.
2. **Log In:** Access the app using your email and password.
3. **View News:** Browse top headlines and filter by category.
4. **Save Articles:** Save news articles to your account for later.
5. **Summarize Articles:** Get AI-powered summaries for any news content.

---

## Contributing

Feel free to fork this repository and submit pull requests for improvements. Contributions are welcome!

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Acknowledgments

- **[Hugging Face](https://huggingface.co/)** for the `transformers` library.
- **[NewsAPI](https://newsapi.org/)** for providing access to news articles.
- **[Flask-Mail](https://pythonhosted.org/Flask-Mail/)** for email integration. 

---

## Contact

For questions or suggestions, feel free to contact me at [shrinivasnadager03@gmail.com].
