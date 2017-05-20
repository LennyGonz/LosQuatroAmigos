"""
============================
This is the main home page
============================
"""
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension


# Create Instance of Class
app = Flask(__name__)

app.config["DATABASE"] = 'losquatroamigos.db'
app.config['DEBUG'] = True
import os
app.secret_key = os.urandom(12)

app.config['SECRET_KEY'] = app.secret_key
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


toolbar = DebugToolbarExtension(app)

from app import models
from app.models import views
