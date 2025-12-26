from pymongo import MongoClient
from datetime import datetime
import os

class DatabaseService:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
        self.db = self.client[os.getenv('DB_NAME', 'myapp')]
        self.users = self.db['users']

    def find_user_by_google_id(self, google_id: str):
        """Trova utente tramite Google ID"""
        return self.users.find_one({'google_id': google_id})

    def find_user_by_email(self, email: str):
        """Trova utente tramite email"""
        return self.users.find_one({'email': email})

    def create_user(self, user_data: dict):
        """Crea nuovo utente"""
        user_data['created_at'] = datetime.now()
        result = self.users.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return user_data

    def update_user(self, user_id, update_data: dict):
        """Aggiorna utente esistente"""
        update_data['updated_at'] = datetime.now()
        self.users.update_one(
            {'_id': user_id},
            {'$set': update_data}
        )
        return self.users.find_one({'_id': user_id})

database_service = DatabaseService()