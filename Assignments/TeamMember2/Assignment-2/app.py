from crypt import methods
from flask import Flask, render_template, request, redirect, session,url_for
import sqlite3 as sql
import sys
import ibm_db
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b70af05b-76e4-4bca-a1f5-23dbb4c6a74e.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32716;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=tkt02689;PWD=iJblyvngVsuVA5ae;",'','')

app = Flask(__name__)
app.secret_key = 'fasdgfdgdfg'


@app.route('/adduser')
def new_student():
   return render_template('signup.html')

@app.route('/addrec',methods = ['POST', 'GET'])
def addrec():
   print('addrec')
   if request.method == 'POST':
      try:
         name = request.form['name']
         email = request.form['email']
         roll = request.form['roll']
         pw = request.form['pass']
         sql = "INSERT into user values ('{}', '{}','{}', '{}')".format(email, name, roll, pw)
         stmt = ibm_db.exec_immediate(conn, sql)
         with sql.connect("student.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO student (email,username,rollnumber,password) VALUES (?,?,?,?)",(name,email,roll,pw) )
            con.commit()
     
      except:
         con.rollback()
        
      
      finally:
         return redirect (url_for('signin'))
         con.close()

@app.route('/signin')
def signin():
    print("d")
    return render_template ('signin.html')



@app.route('/login',methods=["POST"])
def login():
      if(request.method == "POST"):
        try:
         mail = request.form['email']
         pwd = request.form['pass']
         sql = "SELECT * from user where email = '{}'".format(mail)
        
         stmt = ibm_db.exec_immediate(conn, sql)
         dict = ibm_db.fetch_assoc(stmt)         
         if (mail == dict['EMAIL'].strip() and pwd == dict['PASSWORD'].strip()):
            # print("if clause")
            return render_template("welcome.html", user=dict['USERNAME'])
         else:
            return render_template("signin.html",message = "Not a valid user")
    
             
        except:            
            print (sys.exc_info()[0])
      return render_template("signin.html",message = "Not a valid user")
        
   #  return render_template('signin.html')
     
if __name__ == '__main__':
   app.run(debug = True)