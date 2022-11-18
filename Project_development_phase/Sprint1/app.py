import ibm_db
from flask import Flask, url_for, render_template, request, session, redirect, flash, send_file
 
app = Flask(__name__)
app.config['SECRET_KEY'] = 'e5ac358c-f0bf-11e5-9e39-d3b532c10a28'
arr2=[]

def connection():
    try:
        #db2 credential
        conn=ibm_db.connect('DATABASE=bludb;HOSTNAME=125f9f61-9715-46f9-9399-c8177b21803b.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30426;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=fyq84028;PWD=Cxm5IBvcj9oboXaE', '', '')
        print("CONNECTED TO DATABASE")
        return conn
    except:
        print(ibm_db.conn_errormsg())
        print("CONNECTION FAILED")

#Home Page
@app.route("/")
def home():
    return render_template('index.html')

#Logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return render_template("index.html")

#Register
@app.route("/register",methods=["GET","POST"])
def registerPage():
    if request.method=="POST":
        conn=connection()
        try:
            role=request.form["urole"]
            if role=="seeker":
                sql="INSERT INTO SEEKER VALUES('{}','{}','{}','{}','{}')".format(request.form["uemail"],request.form["upass"],request.form["uname"],request.form["umobileno"],request.form["uworkstatus"])
            else:
                sql="INSERT INTO RECRUITER VALUES('{}','{}','{}','{}','{}')".format(request.form["uemail"],request.form["upass"],request.form["uname"],request.form["umobileno"],request.form["uorganisation"])
            ibm_db.exec_immediate(conn,sql)
            return render_template('index.html')
        except Exception as error:
            print(error)
            return render_template('register.html')
    else:
        return render_template('register.html')

@app.route("/seekerHome", methods=["GET"])
def seekerHome():
    return render_template('SeekerMenu.html')

#Seeker Login
@app.route("/login_seeker",methods=["GET","POST"])
def loginPageSeeker():
    if request.method=="POST":
        conn=connection()
        useremail=request.form["lemail"]
        password=request.form["lpass"]
        sql="SELECT COUNT(*) FROM SEEKER WHERE EMAIL=? AND PASSWORD=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,useremail)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        res=ibm_db.fetch_assoc(stmt)
        if res['1']==1:
            session['loggedin']= True
            session['user'] = useremail
            return redirect(url_for('seekerHome'))
        else:
            print("Wrong Username or Password")
            return render_template('loginseeker.html')
    else:
        return render_template('loginseeker.html')

#Recruiter Login
@app.route("/login_recruiter",methods=["GET","POST"])
def loginPageRecruiter():
    if request.method=="POST":
        conn=connection()
        useremail=request.form["lemail"]
        password=request.form["lpass"]
        sql="SELECT COUNT(*) FROM RECRUITER WHERE EMAIL=? AND PASSWORD=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,useremail)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        res=ibm_db.fetch_assoc(stmt)
        if res['1']==1:
            session['loggedin']= True
            session['user'] = useremail
            return redirect(url_for('recruitermenu'))
        else:
            print("Wrong Username or Password")
            return render_template('loginrecruiter.html')
    else:
        return render_template('loginrecruiter.html')


#Recruiter Menu
@app.route('/recruitermenu', methods =["GET","POST"])
def recruitermenu():
    return render_template('recruitermenu.html')

if __name__=='__main__':
    # app.config['SECRET_KEY']='super secret key'
    # app.config['SESSION_TYPE']='memcached'
    app.run(debug=True)
