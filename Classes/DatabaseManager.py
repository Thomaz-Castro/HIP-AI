import hashlib
from datetime import datetime, date
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId
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
                # Converte date para datetime se necessário
                for key, value in additional_data.items():
                    if isinstance(value, date) and not isinstance(value, datetime):
                        additional_data[key] = datetime.combine(value, datetime.min.time())
                user_data.update(additional_data)

            result = self.db.users.insert_one(user_data)
            return result.inserted_id
        except pymongo.errors.DuplicateKeyError:
            return None

    def get_users_by_type(self, user_type):
        return list(self.db.users.find({"user_type": user_type}))

    def update_user(self, user_id, data):
        try:
            # Validação básica para evitar erros comuns
            if not isinstance(data, dict) or not data:
                return False

            # Converte date para datetime se necessário
            for key, value in data.items():
                if isinstance(value, date) and not isinstance(value, datetime):
                    data[key] = datetime.combine(value, datetime.min.time())
                    print(f"DEBUG: Convertido '{key}' de date para datetime")

            result = self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": data}
            )
            
            return result.matched_count > 0

        except InvalidId:
            return False
        except Exception as e:
            import traceback
            traceback.print_exc()
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
        """Busca todos os relatórios, populando os dados do médico e do paciente.
        
        Mantém os relatórios mesmo que o médico ou paciente associado não seja encontrado,
        fornecendo um valor padrão nesses casos.
        """
        pipeline = [
            # 1. Busca o documento do médico correspondente
            {
                "$lookup": {
                    "from": "users",
                    "localField": "doctor_id",
                    "foreignField": "_id",
                    "as": "doctor_info" # Usar um nome diferente para evitar conflito
                }
            },
            # 2. Busca o documento do paciente correspondente
            {
                "$lookup": {
                    "from": "users",
                    "localField": "patient_id",
                    "foreignField": "_id",
                    "as": "patient_info" # Usar um nome diferente para evitar conflito
                }
            },
            # 3. Substitui o array do médico pelo primeiro objeto ou um valor padrão
            {
                "$addFields": {
                    "doctor": {
                        "$ifNull": [
                            { "$arrayElemAt": ["$doctor_info", 0] },
                            { "name": "Médico não encontrado" } # Objeto padrão
                        ]
                    }
                }
            },
            # 4. Substitui o array do paciente pelo primeiro objeto ou um valor padrão
            {
                "$addFields": {
                    "patient": {
                        "$ifNull": [
                            { "$arrayElemAt": ["$patient_info", 0] },
                            { "name": "Paciente não encontrado" } # Objeto padrão
                        ]
                    }
                }
            },
            # 5. Remove os campos temporários que usamos no lookup
            {
                "$project": {
                    "doctor_info": 0,
                    "patient_info": 0
                }
            }
        ]
        return list(self.db.reports.aggregate(pipeline))

    def get_doctor_reports(self, doctor_id):
        """Busca todos os relatórios criados por um médico específico."""
        reports_cursor = self.db.reports.find({"doctor_id": doctor_id})
        reports_list = []
        
        # É importante popular os dados do paciente e do médico para a tabela funcionar
        for report in reports_cursor:
            patient = self.db.users.find_one({"_id": report["patient_id"]})
            doctor = self.db.users.find_one({"_id": report["doctor_id"]}) # O próprio médico
            
            report["patient"] = patient if patient else {"name": "Paciente não encontrado"}
            report["doctor"] = doctor if doctor else {"name": "Médico não encontrado"}
            reports_list.append(report)
            
        return reports_list