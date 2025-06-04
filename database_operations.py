from datetime import datetime
from database_connection import DatabaseConnection
from config import DB_CONFIG

class DBOperations:
    @staticmethod
    def get_last_status(name):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT status FROM attendance 
                WHERE name = %s 
                ORDER BY timestamp DESC 
                LIMIT 1
            """, (name,))
            result = cursor.fetchone()
            return result[0] if result else None

    @staticmethod
    def insert_attendance(name, status):
        with DatabaseConnection() as conn:
            cursor = conn.cursor()

            # Check last status with transaction
            cursor.execute("""
                SELECT status, timestamp FROM attendance 
                WHERE name = %s 
                ORDER BY timestamp DESC 
                LIMIT 1
                FOR UPDATE
            """, (name,))
            last_record = cursor.fetchone()

            if last_record and last_record[0] == status:
                return False, f"{status} already marked. Please {'Exit' if status == 'Enter' else 'Enter'} first."
            
            now = datetime.now()

            # Insert the new attendance record
            cursor.execute("""
                INSERT INTO attendance (name, status, timestamp) 
                VALUES (%s, %s, %s)
            """, (name, status, now))
            conn.commit()

            # If marking Exit, calculate duration
            if status == 'Exit' and last_record and last_record[0] == 'Enter':
                enter_time = last_record[1]
                duration = now - enter_time
                hours, remainder = divmod(duration.total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)
                return True, f"{status} marked for {name}. Worked for {int(hours)} hour(s) and {int(minutes)} minute(s)."

            return True, f"{status} marked for {name}"
