# MeteoFlow Flask Application (HF3one.py)

## Overview
This is a Flask web application called Eco Helper that provides features such as educational Q&A, interactive quizzes, environmental issue reporting, eco tips, weather and disaster alerts, and Sustainable Development Goals information.

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Installation

1. Clone or download the project files.

2. Install required Python packages:

```bash
pip install -r requirements.txt
```

### Environment Variables

Set the following environment variables for API keys and email configuration:

- `COHERE_API_KEY`: Your Cohere API key for AI model queries.
- `OPENWEATHER_API_KEY`: Your OpenWeatherMap API key.
- `AGRI_WEATHER_API_KEY`: (Optional) Separate key for agricultural weather forecast.
- `EMAIL_SENDER`: Email address used to send alert emails.
- `EMAIL_PASSWORD`: Password or app password for the sender email.
- `EMAIL_SMTP_SERVER`: SMTP server address (default: smtp.gmail.com).
- `EMAIL_SMTP_PORT`: SMTP server port (default: 587).
- `ALERT_RECIPIENTS`: Comma-separated list of email addresses to receive alerts.
- `FLASK_SECRET_KEY`: Secret key for Flask session management (optional, default provided).

Example (Linux/macOS):

```bash
export COHERE_API_KEY="your_cohere_api_key"
export OPENWEATHER_API_KEY="your_openweather_api_key"
export EMAIL_SENDER="your_email@example.com"
export EMAIL_PASSWORD="your_email_password"
export ALERT_RECIPIENTS="recipient1@example.com,recipient2@example.com"
export FLASK_SECRET_KEY="your_secret_key"
```

### Database Initialization

Before running the app, initialize the SQLite database:

```bash
python
>>> from HF3 import init_db
>>> init_db()
>>> exit()
```

This will create the necessary tables in `app.db`.

### Running the Application

Start the Flask app with:

```bash
python HF3.py
```

The app will be accessible at `http://127.0.0.1:5000/`.

### Usage

- Login with username/password:
  - Admin: `admin` / `adminpass`
  - User: `user` / `userpass`
- Explore features via the navigation menu.

## Notes

- The app uses inline HTML rendering; no separate templates are required.
- Ensure all environment variables are set correctly for full functionality.
- For email alerts, ensure SMTP credentials are valid.

## Dependencies

- Flask
- Cohere
- Requests
- Feedparser

## License

This project is provided as-is without warranty.
