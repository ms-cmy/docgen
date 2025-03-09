import psycopg2
from psycopg2 import sql

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="vectordb",  # ← Changed from mydb
        user="admin",
        password="secret",
        port=5432
    )

def get_users():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM documents")
            return cur.fetchall()

def insert_document(data: dict):
    """Insert a document with embedding"""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("""
                    INSERT INTO documents (function_name, embedding, original_text)
                    VALUES (%s, %s, %s)
                """),
                (
                    data['function_name'],
                    data['embed'],
                    data['text_that_got_embed']
                )
            )
        conn.commit()

# insert_document(data={"function_name": "teste", "embed": [float(i) for i in range(0, 384)], "text_that_got_embed": "meu texto"})
print(get_users())