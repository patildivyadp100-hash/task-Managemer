import sqlite3

conn = sqlite3.connect("task.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS TASKS")
cursor.execute("DROP TABLE IF EXISTS USERS")

cursor.execute('''
          CREATE TABLE IF NOT EXISTS USERS (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          email TEXT NOT NULL
          )    
        ''')

conn.commit()

cursor.execute('''
          CREATE TABLE IF NOT EXISTS TASKS (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL,
              title TEXT NOT NULL,
              completed INTEGER DEFAULT 0,
              FOREIGN KEY(user_id)
              REFERENCES USERS(id)
          )
        ''')

# Insert users
cursor.execute(
    '''INSERT INTO USERS(id,name,email) VALUES (?,?,?)''',
    (1, 'Sayali', 'sayali@')
)

cursor.execute(
    '''INSERT INTO USERS(id,name,email) VALUES (?,?,?)''',
    (2, 'Rutuja', 'rutuja@')
)

cursor.execute(
    '''INSERT INTO USERS(id,name,email) VALUES (?,?,?)''',
    (3, 'Prachi', 'prachi@')
)

# Insert tasks
cursor.execute(
    '''INSERT INTO TASKS(id,user_id,title,completed) VALUES (?,?,?,?)''',
    (1, 1, 'Complete project', 1)
)

cursor.execute(
    '''INSERT INTO TASKS(id,user_id,title,completed) VALUES (?,?,?,?)''',
    (2, 2, 'Study Python', 0)
)

cursor.execute(
    '''INSERT INTO TASKS(id,user_id,title,completed) VALUES (?,?,?,?)''',
    (3, 3, 'Submit assignment', 0)
)

# Update email of Sayali
cursor.execute(
    '''UPDATE USERS SET email=? WHERE name=?''',
    ("sayali@gmail.com", "Sayali")
)

# Delete Prachi
cursor.execute(
    '''DELETE FROM USERS WHERE name=?''',
    ("Prachi",)
)

conn.commit()

# Display users
cursor.execute('''SELECT * FROM USERS''')
print("USERS:")
print(cursor.fetchall())

# Display tasks
cursor.execute('''SELECT * FROM TASKS''')
print("TASKS:")
print(cursor.fetchall())

conn.close()