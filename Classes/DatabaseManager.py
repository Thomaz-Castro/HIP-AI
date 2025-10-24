import hashlib
from datetime import datetime, date
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from psycopg2 import pool
import os
from dotenv import load_dotenv
load_dotenv()


class DatabaseManager:
    def __init__(self):
        # Configuração do PostgreSQL
        self.db_config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'medical_system'),
            'user': os.getenv('POSTGRES_USER', 'medicSys'),
            'password': os.getenv('POSTGRES_PASSWORD', 'Sysmedical')
        }
        
        self.connection_pool = None
        self.connect()

    def connect(self):
        """Conecta ao PostgreSQL e cria as tabelas necessárias"""
        try:
            # Cria um pool de conexões
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 20,  # mínimo e máximo de conexões
                **self.db_config
            )
            
            print("✅ Conectado ao PostgreSQL com sucesso!")
            
            # Cria as tabelas e dados iniciais
            self.create_tables()
            self.create_admin_user()
            
        except Exception as e:
            print(f"❌ Erro ao conectar ao PostgreSQL: {e}")
            return False
        return True

    def get_connection(self):
        """Obtém uma conexão do pool"""
        return self.connection_pool.getconn()

    def return_connection(self, conn):
        """Retorna uma conexão ao pool"""
        self.connection_pool.putconn(conn)

    def create_tables(self):
        """Cria as tabelas do sistema"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Tabela de usuários
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    user_type VARCHAR(50) NOT NULL CHECK (user_type IN ('admin', 'doctor', 'patient')),
                    
                    -- Campos específicos de médicos
                    crm VARCHAR(50),
                    specialty VARCHAR(100),
                    
                    -- Campos específicos de pacientes
                    birth_date DATE,
                    phone VARCHAR(20),
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de relatórios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id SERIAL PRIMARY KEY,
                    doctor_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    patient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    report_data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Índices para melhorar performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
                CREATE INDEX IF NOT EXISTS idx_users_type ON users(user_type);
                CREATE INDEX IF NOT EXISTS idx_reports_doctor ON reports(doctor_id);
                CREATE INDEX IF NOT EXISTS idx_reports_patient ON reports(patient_id);
                CREATE INDEX IF NOT EXISTS idx_reports_created ON reports(created_at);
            """)
            
            # Trigger para atualizar updated_at automaticamente
            cursor.execute("""
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ language 'plpgsql';
            """)
            
            cursor.execute("""
                DROP TRIGGER IF EXISTS update_users_updated_at ON users;
                CREATE TRIGGER update_users_updated_at 
                    BEFORE UPDATE ON users 
                    FOR EACH ROW 
                    EXECUTE FUNCTION update_updated_at_column();
            """)
            
            cursor.execute("""
                DROP TRIGGER IF EXISTS update_reports_updated_at ON reports;
                CREATE TRIGGER update_reports_updated_at 
                    BEFORE UPDATE ON reports 
                    FOR EACH ROW 
                    EXECUTE FUNCTION update_updated_at_column();
            """)
            
            conn.commit()
            print("✅ Tabelas criadas/verificadas com sucesso!")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao criar tabelas: {e}")
        finally:
            cursor.close()
            self.return_connection(conn)

    def create_admin_user(self):
        """Cria usuário administrador padrão se não existir"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Verifica se já existe admin
            cursor.execute("SELECT id FROM users WHERE email = %s", ('admin@sistema.com',))
            if cursor.fetchone() is None:
                cursor.execute("""
                    INSERT INTO users (name, email, password, user_type)
                    VALUES (%s, %s, %s, %s)
                """, (
                    'Administrador',
                    'admin@sistema.com',
                    self.hash_password('admin123'),
                    'admin'
                ))
                conn.commit()
                print("✅ Usuário administrador criado: admin@sistema.com / admin123")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao criar admin: {e}")
        finally:
            cursor.close()
            self.return_connection(conn)

    def hash_password(self, password):
        """Hash de senha usando SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate(self, email, password):
        """Autentica um usuário"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT * FROM users WHERE email = %s AND password = %s",
                (email, self.hash_password(password))
            )
            user = cursor.fetchone()
            return dict(user) if user else None
        finally:
            cursor.close()
            self.return_connection(conn)

    def create_user(self, name, email, password, user_type, additional_data=None):
        """Cria um novo usuário"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Prepara os dados base
            fields = ['name', 'email', 'password', 'user_type']
            values = [name, email, self.hash_password(password), user_type]
            
            # Adiciona campos adicionais se fornecidos
            if additional_data:
                for key, value in additional_data.items():
                    fields.append(key)
                    values.append(value)
            
            # Monta a query dinamicamente
            placeholders = ', '.join(['%s'] * len(fields))
            fields_str = ', '.join(fields)
            
            query = f"INSERT INTO users ({fields_str}) VALUES ({placeholders}) RETURNING id"
            cursor.execute(query, values)
            
            user_id = cursor.fetchone()[0]
            conn.commit()
            return user_id
            
        except psycopg2.IntegrityError:
            conn.rollback()
            return None
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao criar usuário: {e}")
            return None
        finally:
            cursor.close()
            self.return_connection(conn)

    def get_users_by_type(self, user_type):
        """Retorna todos os usuários de um tipo específico"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT * FROM users WHERE user_type = %s ORDER BY created_at DESC",
                (user_type,)
            )
            users = cursor.fetchall()
            return [dict(user) for user in users]
        finally:
            cursor.close()
            self.return_connection(conn)

    def update_user(self, user_id, data):
        """Atualiza um usuário"""
        if not isinstance(data, dict) or not data:
            return False
        
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Monta a query dinamicamente
            set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
            values = list(data.values())
            values.append(user_id)
            
            query = f"UPDATE users SET {set_clause} WHERE id = %s"
            cursor.execute(query, values)
            
            rows_affected = cursor.rowcount
            conn.commit()
            return rows_affected > 0
            
        except psycopg2.IntegrityError:
            conn.rollback()
            return False
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao atualizar usuário: {e}")
            return False
        finally:
            cursor.close()
            self.return_connection(conn)

    def delete_user(self, user_id):
        """Deleta um usuário"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            rows_affected = cursor.rowcount
            conn.commit()
            return rows_affected > 0
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao deletar usuário: {e}")
            return False
        finally:
            cursor.close()
            self.return_connection(conn)

    def create_report(self, doctor_id, patient_id, report_data):
        """Cria um novo relatório"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # report_data será armazenado como JSONB
            import json
            cursor.execute("""
                INSERT INTO reports (doctor_id, patient_id, report_data)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (doctor_id, patient_id, json.dumps(report_data)))
            
            report_id = cursor.fetchone()[0]
            conn.commit()
            return report_id
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao criar relatório: {e}")
            return None
        finally:
            cursor.close()
            self.return_connection(conn)

    def get_patient_reports(self, patient_id):
        """Retorna todos os relatórios de um paciente"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT r.*, 
                       row_to_json(d.*) as doctor,
                       row_to_json(p.*) as patient
                FROM reports r
                LEFT JOIN users d ON r.doctor_id = d.id
                LEFT JOIN users p ON r.patient_id = p.id
                WHERE r.patient_id = %s
                ORDER BY r.created_at DESC
            """, (patient_id,))
            
            reports = cursor.fetchall()
            return [dict(report) for report in reports]
        finally:
            cursor.close()
            self.return_connection(conn)

    def get_doctor_reports(self, doctor_id):
        """Retorna todos os relatórios criados por um médico"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT r.*,
                       row_to_json(d.*) as doctor,
                       row_to_json(p.*) as patient
                FROM reports r
                LEFT JOIN users d ON r.doctor_id = d.id
                LEFT JOIN users p ON r.patient_id = p.id
                WHERE r.doctor_id = %s
                ORDER BY r.created_at DESC
            """, (doctor_id,))
            
            reports = cursor.fetchall()
            return [dict(report) for report in reports]
        finally:
            cursor.close()
            self.return_connection(conn)

    def get_all_reports(self):
        """Retorna todos os relatórios com dados de médico e paciente"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT r.*,
                       COALESCE(row_to_json(d.*), '{"name": "Médico não encontrado"}'::json) as doctor,
                       COALESCE(row_to_json(p.*), '{"name": "Paciente não encontrado"}'::json) as patient
                FROM reports r
                LEFT JOIN users d ON r.doctor_id = d.id
                LEFT JOIN users p ON r.patient_id = p.id
                ORDER BY r.created_at DESC
            """)
            
            reports = cursor.fetchall()
            return [dict(report) for report in reports]
        finally:
            cursor.close()
            self.return_connection(conn)

    def get_latest_patient_report(self, patient_id):
        """Retorna o último relatório de um paciente"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM reports 
                WHERE patient_id = %s 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (patient_id,))
            
            report = cursor.fetchone()
            return dict(report) if report else None
        finally:
            cursor.close()
            self.return_connection(conn)

    def close(self):
        """Fecha o pool de conexões"""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("✅ Conexões fechadas com sucesso!")