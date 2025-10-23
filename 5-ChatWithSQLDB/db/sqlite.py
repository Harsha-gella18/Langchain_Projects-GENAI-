import sqlite3

#Connect to sqllite
connection = sqlite3.connect('student.db')

#Create a cursor
cursor = connection.cursor()

#Create a table
cursor.execute('''CREATE TABLE IF NOT EXISTS students
                  (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, grade TEXT)''')

#Insert sample data
cursor.execute("INSERT INTO students (name, age, grade) VALUES ('Alice', 20, 'A')")
cursor.execute("INSERT INTO students (name, age, grade) VALUES ('Bob', 22, 'B')")
cursor.execute("INSERT INTO students (name, age, grade) VALUES ('Charlie', 23   , 'C')")
cursor.execute("INSERT INTO students (name, age, grade) VALUES ('Diana', 21, 'A')")
cursor.execute("INSERT INTO students (name, age, grade) VALUES ('Ethan', 24, 'B')")

print("Sample data inserted successfully.")
print("Fetching data from the database:")
print("-----------------------------------")
#Query the data
data = cursor.execute("SELECT * FROM students")
connection.commit()

for i in data:
    print(i)
connection.close()