import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',  # e.g., 'localhost'
        user='root',
        password='mysql',
        database='streamlit_app'
    )
    return connection

def add_user(username, password):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user:
            return False

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        connection.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def authenticate(username, password):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        if user:
            return True
        return False
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
