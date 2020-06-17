import sqlite3

conn=sqlite3.connect('SondaV5.db')

c=conn.cursor()


##Para crear tablas
c.execute("""CREATE TABLE sensores (
            tiempo DATETIME,
            temp TEXT,
            pH TEXT,
            ce TEXT,
            od TEXT,
            opr TEXT,
            color TEXT   
            )""")

conn.commit()

conn.close()