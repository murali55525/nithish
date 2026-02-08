import psycopg2

def get_db():
    return psycopg2.connect(
        host="database-service",
        database="healthcare",
        user="admin",
        password="admin"
    )
