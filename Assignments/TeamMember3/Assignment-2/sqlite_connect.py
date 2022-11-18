import sqlite3

conn = sqlite3.connect('student.db')
print("Opened database successfully")

# conn.execute('CREATE TABLE student (email TEXT, username TEXT, rollnumber TEXT, password TEXT)')
# conn.execute('delete from student')
res = (conn.execute('SELECT * from student where rollnumber = "91"')).fetchall()
print(res)
print("Table created successfully",len(res))
conn.close()