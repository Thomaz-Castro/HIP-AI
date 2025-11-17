import hashlib
from datetime import datetime, date
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from psycopg2 import pool
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import json
import base64

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
        
        # Chave de criptografia (deve estar no .env em produção)
        encryption_key = os.getenv('ENCRYPTION_KEY')
        if not encryption_key:
            raise Exception("Chave de encriptação nao encontrada no arquivo .env")
            
        
        self.cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
        
        self.connection_pool = None
        self.connect()

    def encrypt_data(self, data):
        """Criptografa dados sensíveis"""
        if data is None:
            return None
        if isinstance(data, dict):
            data = json.dumps(data)
        elif not isinstance(data, str):
            data = str(data)
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data):
        """Descriptografa dados sensíveis"""
        if encrypted_data is None:
            return None
        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode()).decode()
            # Tenta converter para JSON se possível
            try:
                return json.loads(decrypted)
            except:
                return decrypted
        except Exception as e:
            print(f"❌ Erro ao descriptografar: {e}")
            return None

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
        """Cria as tabelas do sistema com campos de segurança"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Tabela de usuários com soft delete e CPF
            cursor.execute(r"""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    user_type VARCHAR(50) NOT NULL CHECK (user_type IN ('admin', 'doctor', 'patient')),
                    cpf VARCHAR(14) UNIQUE,
                    
                    -- Campos específicos de médicos
                    crm VARCHAR(50),
                    specialty VARCHAR(100),
                    
                    -- Campos específicos de pacientes
                    birth_date DATE,
                    phone VARCHAR(20),
                    
                    -- Soft delete
                    is_active BOOLEAN DEFAULT TRUE,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Índices para CPF
                    CONSTRAINT cpf_format CHECK (cpf ~ '^[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}$' OR cpf IS NULL)
                )
            """)
            
            # Tabela de relatórios com dados criptografados
            cursor.execute(r"""
                CREATE TABLE IF NOT EXISTS reports (
                    id SERIAL PRIMARY KEY,
                    doctor_id INTEGER NOT NULL REFERENCES users(id),
                    patient_id INTEGER NOT NULL REFERENCES users(id),
                    
                    -- Dados criptografados
                    report_data_encrypted TEXT NOT NULL,
                    
                                        
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Índices para melhorar performance
            cursor.execute(r"""
                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
                CREATE INDEX IF NOT EXISTS idx_users_type ON users(user_type);
                CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);
                CREATE INDEX IF NOT EXISTS idx_users_cpf ON users(cpf);
                CREATE INDEX IF NOT EXISTS idx_reports_doctor ON reports(doctor_id);
                CREATE INDEX IF NOT EXISTS idx_reports_patient ON reports(patient_id);
                CREATE INDEX IF NOT EXISTS idx_reports_created ON reports(created_at);
            """)
            
            # Trigger para atualizar updated_at automaticamente
            cursor.execute(r"""
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ language 'plpgsql';
            """)
            
            cursor.execute(r"""
                DROP TRIGGER IF EXISTS update_users_updated_at ON users;
                CREATE TRIGGER update_users_updated_at 
                    BEFORE UPDATE ON users 
                    FOR EACH ROW 
                    EXECUTE FUNCTION update_updated_at_column();
            """)
            
            cursor.execute(r"""
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
                    INSERT INTO users (name, email, password, user_type, is_active)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    'Administrador',
                    'admin@sistema.com',
                    self.hash_password('admin123'),
                    'admin',
                    True
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

    def validate_cpf(self, cpf):
        """Valida CPF (formato e dígitos verificadores)"""
        if not cpf:
            return True  # CPF é opcional
        
        # Remove formatação
        cpf_numbers = ''.join(filter(str.isdigit, cpf))
        
        if len(cpf_numbers) != 11:
            return False
        
        # Verifica se todos os dígitos são iguais
        if cpf_numbers == cpf_numbers[0] * 11:
            return False
        
        # Valida primeiro dígito verificador
        sum_1 = sum(int(cpf_numbers[i]) * (10 - i) for i in range(9))
        digit_1 = 11 - (sum_1 % 11)
        digit_1 = 0 if digit_1 >= 10 else digit_1
        
        if int(cpf_numbers[9]) != digit_1:
            return False
        
        # Valida segundo dígito verificador
        sum_2 = sum(int(cpf_numbers[i]) * (11 - i) for i in range(10))
        digit_2 = 11 - (sum_2 % 11)
        digit_2 = 0 if digit_2 >= 10 else digit_2
        
        return int(cpf_numbers[10]) == digit_2

    def authenticate(self, email, password):
        """Autentica um usuário (apenas usuários ativos)"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT * FROM users WHERE email = %s AND password = %s AND is_active = TRUE",
                (email, self.hash_password(password))
            )
            user = cursor.fetchone()
            return dict(user) if user else None
        finally:
            cursor.close()
            self.return_connection(conn)

    def create_user(self, name, email, password, user_type, additional_data=None, created_by=None):
        """Cria um novo usuário"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Valida CPF se fornecido
            cpf = additional_data.get('cpf') if additional_data else None
            if cpf and not self.validate_cpf(cpf):
                return None
            
            # Prepara os dados base
            fields = ['name', 'email', 'password', 'user_type', 'is_active']
            values = [name, email, self.hash_password(password), user_type, True]
            
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
            
        except psycopg2.IntegrityError as e:
            conn.rollback()
            if 'cpf' in str(e):
                print("❌ CPF já cadastrado")
            return None
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao criar usuário: {e}")
            return None
        finally:
            cursor.close()
            self.return_connection(conn)

    def get_users_by_type(self, user_type, include_inactive=False):
        """Retorna todos os usuários de um tipo específico"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            if include_inactive:
                query = "SELECT * FROM users WHERE user_type = %s ORDER BY is_active DESC, created_at DESC"
            else:
                query = "SELECT * FROM users WHERE user_type = %s AND is_active = TRUE ORDER BY created_at DESC"
            
            cursor.execute(query, (user_type,))
            users = cursor.fetchall()
            return [dict(user) for user in users]
        finally:
            cursor.close()
            self.return_connection(conn)

    def update_user(self, user_id, data, updated_by=None):
        """Atualiza um usuário"""
        if not isinstance(data, dict) or not data:
            return False
        
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Valida CPF se fornecido
            if 'cpf' in data and data['cpf'] and not self.validate_cpf(data['cpf']):
                return False
            
            # Busca valores antigos para auditoria
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            old_user = cursor.fetchone()
            
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

    def soft_delete_user(self, user_id, deleted_by):
        """Desativa um usuário (soft delete) - não exclui fisicamente"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET is_active = FALSE
                WHERE id = %s AND user_type IN ('doctor', 'patient')
            """, (user_id,))
            
            rows_affected = cursor.rowcount
            conn.commit()
            
            return rows_affected > 0
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao desativar usuário: {e}")
            return False
        finally:
            cursor.close()
            self.return_connection(conn)

    def reactivate_user(self, user_id, reactivated_by):
        """Reativa um usuário desativado"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET is_active = TRUE
                WHERE id = %s
            """, (user_id,))
            
            rows_affected = cursor.rowcount
            conn.commit()
            
            
            return rows_affected > 0
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao reativar usuário: {e}")
            return False
        finally:
            cursor.close()
            self.return_connection(conn)

    def delete_user(self, user_id):
        """Deleta um usuário PERMANENTEMENTE (apenas para admins)"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s AND user_type = 'admin'", (user_id,))
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

    def create_report(self, doctor_id, patient_id, report_data, created_by=None):
        """Cria um novo relatório com dados criptografados"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Criptografa os dados sensíveis
            encrypted_data = self.encrypt_data(report_data)
            
            cursor.execute("""
                INSERT INTO reports (doctor_id, patient_id, report_data_encrypted)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (doctor_id, patient_id, encrypted_data))
            
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

    def get_patient_reports(self, patient_id, include_inactive=False):
        """Retorna todos os relatórios de um paciente com dados descriptografados"""
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
            
            # Descriptografa os dados
            for report in reports:
                report['report_data'] = self.decrypt_data(report['report_data_encrypted'])
                del report['report_data_encrypted']
            
            return [dict(report) for report in reports]
        finally:
            cursor.close()
            self.return_connection(conn)

    def get_user_by_cpf(self, cpf, user_type='patient'):
        """Busca um usuário ATIVO pelo CPF e tipo."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT * FROM users WHERE cpf = %s AND user_type = %s AND is_active = TRUE",
                (cpf, user_type)
            )
            user = cursor.fetchone()
            return dict(user) if user else None
        except Exception as e:
            print(f"❌ Erro ao buscar usuário por CPF: {e}")
            return None
        finally:
            cursor.close()
            self.return_connection(conn)

    def get_doctor_reports(self, doctor_id, include_inactive=False):
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
            
            # Descriptografa os dados
            for report in reports:
                report['report_data'] = self.decrypt_data(report['report_data_encrypted'])
                del report['report_data_encrypted']
            
            return [dict(report) for report in reports]
        finally:
            cursor.close()
            self.return_connection(conn)

    def get_all_reports(self, include_inactive=False):
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
            
            # Descriptografa os dados
            for report in reports:
                report['report_data'] = self.decrypt_data(report['report_data_encrypted'])
                del report['report_data_encrypted']
            
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
            if report:
                report = dict(report)
                report['report_data'] = self.decrypt_data(report['report_data_encrypted'])
                del report['report_data_encrypted']
                return report
            return None
        finally:
            cursor.close()
            self.return_connection(conn)

    def get_user_by_id(self, user_id):
        """Busca um usuário específico pelo seu ID."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            return user 
        except Exception as e:
            print(f"❌ Erro ao buscar usuário por ID: {e}")
            return None
        finally:
            cursor.close()
            self.return_connection(conn)

    def close(self):
        """Fecha o pool de conexões"""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("✅ Conexões fechadas com sucesso!")