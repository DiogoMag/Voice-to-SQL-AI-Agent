# 3. Database Query (MySQL)
# Task: Execute the SQL query and return results.
# Tech: Use mysql-connector-python or SQLAlchemy.


import mysql.connector

sql_query = 'this is a placeholder'

conn = mysql.connector.connect(user='root', password='...', database='your_db')
cursor = conn.cursor()
cursor.execute(sql_query)
results = cursor.fetchall()
