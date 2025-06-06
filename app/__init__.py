from flask import Flask
from flask_session import Session
from redis import Redis
from app.config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'flask_session:'
app.config['SESSION_REDIS'] = Redis(host='localhost', port=6379)

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d'):
    """Convert a date string in dd-mmm-yyyy format to yyyy-mm-dd."""
    try:
        # Parse the input date string
        parsed_date = datetime.strptime(value, '%d-%b-%Y')
        # Format it to the desired output format
        return parsed_date.strftime(format)
    except ValueError:
        return value  # Return the original value if parsing fails

Session(app)

from app import routes
