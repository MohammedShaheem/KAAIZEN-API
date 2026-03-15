from firebase_admin import credentials
import firebase_admin
from firebase.firebase_config import firebase_config

cred = credentials.Certificate(firebase_config)

firebase_admin.initialize_app(cred)