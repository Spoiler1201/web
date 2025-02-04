from flask import Flask
from config import Config  # Abszolút importálás

app = Flask(__name__)
app.config.from_object(Config)

from app import routes  # Most már abszolút importálunk

if __name__ == '__main__':
    app.run()