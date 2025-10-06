import mysql.connector
from configparser import ConfigParser

# Load config
config = ConfigParser()
config.read("../config/config.ini")
db = config["mysql"]

try:
    connection = mysql.connector.connect(
        host=db["host"],
        port=int(db["port"]),
        user=db["user"],
        password=db["password"],
        database=db["database"]
    )

    if connection.is_connected():
        print("✅ Connected to MySQL")
        cursor = connection.cursor()

        # Run your query BEFORE closing
        cursor.execute("SELECT * FROM users LIMIT 5;")
        rows = cursor.fetchall()
        for row in rows:
            print("👤", row)

        cursor.close()
        connection.close()
        print("🔒 Connection closed")

except mysql.connector.Error as err:
    print("❌ MySQL error:", err)
