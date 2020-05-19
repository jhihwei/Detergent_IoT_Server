import psycopg2

conn = psycopg2.connect(database="detergent", user="detergent", password="pass123", host="139.162.104.10", port="5432")

print("Opened database successfully")