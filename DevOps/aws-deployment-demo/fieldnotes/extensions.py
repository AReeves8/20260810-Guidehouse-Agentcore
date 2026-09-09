"""Shared extension objects, created here and bound to the app in the factory.

Defined in their own module rather than inside app.py so that models.py can
import `db` without importing the application. Doing it the other way round
produces the circular import that every Flask project hits once: app.py needs
models in order to register them, models need db, and db lives in app.py.
"""

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
