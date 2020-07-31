import psycopg2
from psycopg2 import Error

def sql_connection():
    try:
        conn = psycopg2.connect('Test.db')  # Nombre de la Base de datos 
        return conn
    except Error:
        print(Error)

def sql_table(conn):
    cur =conn.cursor()
    cur.execute("CREATE TABLE (name text)")
    conn.commit()
    
def sql_insert(conn,lecturas):
    cur=conn.cursor()
    #Se crea la table lecturas
    cur.execute("INSERT INTO values(lecturas)")
    conn.commit()

conn= sql_connection()
sql_table(conn)
c = conn.cursor()

# conn = psycopg2.connect('dbname=test')
# cur = conn.cursor()
# 
# cur.execute('select * from people')
# 
# results = cur.fetchall()
# 
# for result in results:
#     print(result)