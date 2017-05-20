from app import app
import os
from flask_bootstrap import Bootstrap
app.secret_key = os.urandom(12)
bootstrap = Bootstrap(app)
app.run(debug=True)
