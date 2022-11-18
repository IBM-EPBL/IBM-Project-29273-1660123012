import ibm_db
from flask import Flask, url_for, render_template, request, session, redirect, flash, send_file
import traceback
from datetime import date
from io import BytesIO
 
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

@app.route("/showApplicants", methods=["POST", "GET"])
def viewApplicants():
    try:
        jobid = request.form['jobid']
    except:
        jobid = request.args.get('jobid')

    try:
        conn=connection()
        sql="SELECT * FROM APPLICATIONS WHERE JOBID={}".format(jobid)
        stmt = ibm_db.exec_immediate(conn,sql)
        dictionary = ibm_db.fetch_both(stmt)
        applicantList = []
        while dictionary != False:
                inst={}
                inst['JOBID']=dictionary['JOBID']
                inst['FIRSTNAME']=dictionary['FIRSTNAME']
                inst['LASTNAME']=dictionary['LASTNAME']
                inst['EMAILID']=dictionary['EMAILID']
                inst['PHONENO']=dictionary['PHONENO']
                inst['WORKEXPERIENCE']=dictionary['WORKEXPERIENCE']
                applicantList.append(inst)
                dictionary = ibm_db.fetch_both(stmt)         
    except Exception as e:
        print(e)
    return render_template('applicantDetail.html', applicants=applicantList)

@app.route("/acceptApplication", methods=["POST"])
def acceptApplicant():
    conn=connection()
    try:
        uemail=request.form["uemail"]
        jobid = request.form["jobid"]
        # sql="INSERT INTO SELECTEDAPPLICANTS(JOBID, EMAIL) VALUES({},'{}')".format(jobid, uemail)
        # ibm_db.exec_immediate(conn,sql)

        sql = "INSERT INTO SELECTEDAPPLICANTS(JOBID, EMAILID, FIRSTNAME, LASTNAME, PHONENO, WORKEXPERIENCE, RESUME) SELECT JOBID, EMAILID, FIRSTNAME, LASTNAME, PHONENO, WORKEXPERIENCE, RESUME FROM APPLICATIONS where JOBID={} and EMAILID='{}'".format(jobid, uemail)
        ibm_db.exec_immediate(conn,sql)

        sql = "Delete from APPLICATIONS where JOBID={} and EMAILID='{}'".format(jobid, uemail)
        ibm_db.exec_immediate(conn,sql)

        #REDUCE THE NO OF VACANCIES BY 1
        sql="UPDATE JOBS SET NUMBEROFVACANCIES = NUMBEROFVACANCIES-1 WHERE JOBID='{}'".format(jobid)
        ibm_db.exec_immediate(conn,sql)

        return redirect(url_for('viewApplicants', jobid=jobid))
    except Exception as error:
        print(error)
        return redirect(url_for('viewApplicants', jobid=jobid))

@app.route("/rejectApplication", methods=["POST"])
def rejectApplicant():
    conn=connection()
    try:
        uemail=request.form["uemail"]
        jobid = request.form["jobid"]

        sql = "Delete from APPLICATIONS where JOBID={} and EMAILID='{}'".format(jobid, uemail)
        ibm_db.exec_immediate(conn,sql)

        return redirect(url_for('viewApplicants', jobid=jobid))
    except Exception as error:
        print(error)
        return redirect(url_for('viewApplicants', jobid=jobid))

@app.route("/selectedApplicants", methods=["POST"])
def selectedApplicant():
    jobid = request.form['jobid']

    try:
        conn=connection()
        sql="SELECT * FROM SELECTEDAPPLICANTS WHERE JOBID={}".format(jobid)
        stmt = ibm_db.exec_immediate(conn,sql)
        dictionary = ibm_db.fetch_both(stmt)
        applicantList = []
        while dictionary != False:
                inst={}
                inst['FIRSTNAME']=dictionary['FIRSTNAME']
                inst['LASTNAME']=dictionary['LASTNAME']
                inst['EMAILID']=dictionary['EMAILID']
                inst['PHONENO']=dictionary['PHONENO']
                inst['WORKEXPERIENCE']=dictionary['WORKEXPERIENCE']
                applicantList.append(inst)
                dictionary = ibm_db.fetch_both(stmt)         
    except Exception as e:
        print(e)
    return render_template('selectedApplicants.html', applicants=applicantList)

@app.route("/SelectedResumeDownload", methods=["POST"])
def selectedResumeDownload():
    if request.method=="POST":
        try:
            conn=connection()
            sql="SELECT * FROM SELECTEDAPPLICANTS WHERE EMAILID='{}'".format(request.form["uemail"])
            stmt = ibm_db.exec_immediate(conn,sql)
            dictionary = ibm_db.fetch_both(stmt)
            return send_file(BytesIO(dictionary["RESUME"]),download_name="resume.pdf", as_attachment=True)
        except:
            print("SELECT QUERY FAILED")
            traceback.print_exc()
            return render_template('sample.html')
    else:
        return render_template("sample.html")

#Download Resume
@app.route("/ResumeDownload",methods=["GET","POST"])
def downloadResume():
    if request.method=="POST":
        try:
            conn=connection()
            sql="SELECT * FROM APPLICATIONS WHERE EMAILID='{}'".format(request.form["uemail"])
            stmt = ibm_db.exec_immediate(conn,sql)
            dictionary = ibm_db.fetch_both(stmt)
            return send_file(BytesIO(dictionary["RESUME"]),download_name="resume.pdf", as_attachment=True)
        except:
            print("SELECT QUERY FAILED")
            traceback.print_exc()
            return render_template('sample.html')
    else:
        return render_template("sample.html")

#Recruiter Menu
@app.route('/recruitermenu', methods =["GET","POST"])
def recruitermenu():
    return render_template('recruitermenu.html')

#Post Job       
@app.route('/postjob', methods =["GET","POST"])
def postjob():
    try:
        if request.method=="POST":
            conn=connection()
            
            sql1="SELECT ORGANISATION FROM RECRUITER WHERE EMAIL=?"
            stmt = ibm_db.prepare(conn, sql1)
            ibm_db.bind_param(stmt, 1, session['user'])
            ibm_db.execute(stmt)
            company = ibm_db.fetch_assoc(stmt)
            
            sql = "INSERT INTO JOBS(COMPANY, RECRUITERMAIL, ROLE, DOMAIN, JOBTYPE, JOBDESCRIPTION, EDUCATION, KEYSKILLS, \
                EXPERIENCE, LOCATION, SALARY, BENEFITSANDPERKS, APPLICATIONDEADLINE, NUMBEROFVACANCIES, POSTEDDATE) \
                    values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
            stmt = ibm_db.prepare(conn, sql)
            
            ibm_db.bind_param(stmt, 1, list(company.values())[0])
            ibm_db.bind_param(stmt, 2, session['user'])
            ibm_db.bind_param(stmt, 3, request.form["role"])
            ibm_db.bind_param(stmt, 4, request.form["domain"])
            ibm_db.bind_param(stmt, 5, request.form["jobtype"])
            ibm_db.bind_param(stmt, 6, request.form["jobdes"])
            ibm_db.bind_param(stmt, 7, request.form["education"])
            ibm_db.bind_param(stmt, 8, request.form["skills"])
            ibm_db.bind_param(stmt, 9, request.form["experience"])
            ibm_db.bind_param(stmt, 10, request.form["location"])
            ibm_db.bind_param(stmt, 11, request.form["salary"])
            ibm_db.bind_param(stmt, 12, request.form["benefits"])
            ibm_db.bind_param(stmt, 13, request.form["deadline"])
            # ibm_db.bind_param(stmt, 14, request.files["logo"].read())
            ibm_db.bind_param(stmt, 14, (int)(request.form["vacancies"]))
            ibm_db.bind_param(stmt, 15, date.today())
            ibm_db.execute(stmt)

            flash("Job Successfully Posted!")
            return render_template('recruitermenu.html')
        else:
            return render_template('postjob.html')
    except:
        traceback.print_exc()

if __name__=='__main__':
    # app.config['SECRET_KEY']='super secret key'
    # app.config['SESSION_TYPE']='memcached'
    app.run(debug=True)
