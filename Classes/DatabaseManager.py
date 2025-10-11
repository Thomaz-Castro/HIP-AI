import hashlib
from datetime import datetime, date
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

class DatabaseManager:
    def __init__(self):
        # Configure sua string de conexão do MongoDB Atlas aqui
        # Formato: mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>?retryWrites=true&w=majority
        self.connection_string = os.getenv(
            "MONGODB_URI", "mongodb+srv://usuario:senha@cluster.mongodb.net/medical_system?retryWrites=true&w=majority")
        self.client = None
        self.db = None
        self.connect()

    def connect(self):
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client.medical_system
            # Testa a conexão
            self.client.admin.command('ismaster')
            print("Conectado ao MongoDB Atlas com sucesso!")
            self.create_indexes()
            self.create_admin_user()
        except Exception as e:
            print(f"Erro ao conectar ao MongoDB: {e}")
            return False
        return True
    
    def get_latest_patient_report(self, patient_id):
        """Retorna o último relatório de um paciente"""
        try:
            report = self.db.reports.find_one(
                {"patient_id": ObjectId(patient_id)},
                sort=[("created_at", pymongo.DESCENDING)]
            )
            return report
        except:
            return None

    def create_indexes(self):
        """Cria índices únicos para email"""
        try:
            self.db.users.create_index("email", unique=True)
        except:
            pass

    def create_admin_user(self):
        """Cria usuário administrador padrão se não existir"""
        admin_exists = self.db.users.find_one({"email": "admin@sistema.com"})
        if not admin_exists:
            admin_user = {
                "name": "Administrador",
                "email": "admin@sistema.com",
                "password": self.hash_password("admin123"),
                "user_type": "admin",
                "created_at": datetime.now()
            }
            self.db.users.insert_one(admin_user)
            print("Usuário administrador criado: admin@sistema.com / admin123")

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate(self, email, password):
        user = self.db.users.find_one({"email": email})
        if user and user["password"] == self.hash_password(password):
            return user
        return None

    def create_user(self, name, email, password, user_type, additional_data=None):
        try:
            user_data = {
                "name": name,
                "email": email,
                "password": self.hash_password(password),
                "user_type": user_type,
                "created_at": datetime.now()
            }
            if additional_data:
                for key, value in additional_data.items():
                    if isinstance(value, date) and not isinstance(value, datetime):
                        additional_data[key] = datetime.combine(
                            value, datetime.min.time())
                user_data.update(additional_data)

            result = self.db.users.insert_one(user_data)
            return result.inserted_id
        except pymongo.errors.DuplicateKeyError:
            return None

    def get_users_by_type(self, user_type):
        return list(self.db.users.find({"user_type": user_type}))

    def update_user(self, user_id, data):
        try:
            result = self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": data}
            )
            return result.modified_count > 0
        except:
            return False

    def delete_user(self, user_id):
        try:
            result = self.db.users.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
        except:
            return False

    def create_report(self, doctor_id, patient_id, report_data):
        try:
            report = {
                "doctor_id": ObjectId(doctor_id),
                "patient_id": ObjectId(patient_id),
                "report_data": report_data,
                "created_at": datetime.now()
            }
            result = self.db.reports.insert_one(report)
            return result.inserted_id
        except:
            return None

    def get_patient_reports(self, patient_id):
        return list(self.db.reports.find({"patient_id": ObjectId(patient_id)}))

    def get_all_reports(self):
        pipeline = [
            {
                "$lookup": {
                    "from": "users",
                    "localField": "doctor_id",
                    "foreignField": "_id",
                    "as": "doctor"
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "patient_id",
                    "foreignField": "_id",
                    "as": "patient"
                }
            },
            {
                "$unwind": "$doctor"
            },
            {
                "$unwind": "$patient"
            }
        ]
        return list(self.db.reports.aggregate(pipeline))
