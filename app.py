

from flask import Flask,jsonify,render_template,request,redirect,flash,url_for,session,Response
from email.message import EmailMessage
import os,random,time,smtplib
import mysql.connector
import base64
import re
import math
from decimal import Decimal


app = Flask(__name__)
app.secret_key ="mykey123@"

@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] ="no-store"
    return response    

@app.context_processor
def user_detect():
    con = mysql.connector.connect(
                                   host ='localhost',
                                   user='root',
                                   password ='password',
                                   database ='doctorapplication'
                            )
    cursor = con.cursor()
    username = session.get("username")
    admin = session.get("admin")
    try:
        cursor.execute("select * from useraccount where username =%s",(username,))
        data = cursor.fetchone()
    finally:
        cursor.close()
        con.close()
    if data is None:
        return {"current_user":"none"}
    return {"current_user":data[1],"username":username,"current_admin":admin}

# this is relate to the none user page 
# front Home 
@app.route("/")
def fhome():
    return render_template("fhome.html")

@app.route("/ffinddoctr",methods = ["GET","POST"])
def f_finddoctor():
    con = mysql.connector.connect(
               host ='localhost',
               user='root',
               password ='password',
               database ='doctorapplication'
        )
    cursor = con.cursor()
    cursor.execute("select * from doctorlist;")
    data = cursor.fetchall()
    
    doctorlist =[]
    for i in data:
        img = base64.b64encode(i[1]).decode('utf-8') if i[1] else ''
        doctorlist.append({
            'id':i[0],
            'image':img,
            'imagetype':i[2],
            'name':i[3],
            'specalist':i[4],
            'year':i[5],
            'rating':i[6],
            'fees':i[7],
            'status':i[8]
        })
        
    try:
        if request.method =="POST":
            input_data = request.form.get("input")
            pattern = "%"+input_data+"%"
            
            con = get_connection()
            cursor = con.cursor()
            cursor.execute("SELECT * FROM doctorlist WHERE name like %s OR specailist LIKE %s ",(pattern,pattern))
            data = cursor.fetchall()
            cursor.close()
            con.close()
            
            doctor=[]
            for i in data:
                img = base64.b64encode(i[1]).decode('utf-8') if i[1] else ''
                doctor.append(
                    {
                        'id':i[0],
                        'image':img,
                        'imagetype':i[2],
                        'name':i[3],
                        'specalist':i[4],
                        'year':i[5],
                        'rating':i[6],
                        'fees':i[7],
                        'status':i[8]
                    }
                )
            
            return render_template('ffindoctor.html',results=doctor)
    
    except mysql.connector.Error as e:
        flash("data base connection error ","error")
        return redirect(url_for('f_finddoctor'))
    finally:
        cursor.close()
        con.close()
         
    return render_template('ffindoctor.html',results=doctorlist)

@app.route("/fmyappoint",methods =["GET","POST"])
def f_myappointment():
    return render_template("fmyappoint.html")

@app.route("/abouts")
def f_about():
    return render_template("fabout.html")    

@app.route("/gotologin")
def gotologin():
    return render_template("notallowed.html")

# admin relate worked
@app.route("/adminHome")
def admin_home():
    if 'admin' not in session:
        return redirect(url_for('login'))
    return render_template("ahome.html")


@app.route("/admin/adddoctor",methods =["GET","POST"])
def add_doctor():
    if 'admin' not in session:
        return redirect(url_for('login'))
    con = mysql.connector.connect(
               host ='localhost',
               user='root',
               password ='password',
               database ='doctorapplication'
        )
    cursor = con.cursor()
    try:
        cursor.execute("select * from doctorlist;")
        data = cursor.fetchall()
        
        doctorlist =[]
        for i in data:
            img = base64.b64encode(i[1]).decode('utf-8') if i[1] else ''
            doctorlist.append({
                'id':i[0],
                'image':img,
                'imagetype':i[2] ,
                'name':i[3],
                'specalist':i[4],
                'year':i[5],
                'rating':i[6],
                'fees':i[7],
                'status':i[8]
            }) 
            
        if request.method == "POST":
            input_data = request.form.get("input")
            pattern = "%"+input_data+"%"
            
            con = get_connection()
            cursor = con.cursor()
            cursor.execute("SELECT * FROM doctorlist WHERE name like %s OR specailist LIKE %s ",(pattern,pattern))
            data = cursor.fetchall()
            
            doctor=[]
            for i in data:
                img = base64.b64encode(i[1]).decode('utf-8') if i[1] else ''
                doctor.append(
                    {
                        'id':i[0],
                        'image':img,
                        'imagetype':i[2],
                        'name':i[3],
                        'specalist':i[4],
                        'year':i[5],
                        'rating':i[6],
                        'fees':i[7],
                        'status':i[8]
                    }
                )
            return render_template("afinddoctor.html",results = doctor)
                      
    finally:
        cursor.close()
        con.close()
        
    
    return render_template("afinddoctor.html",results = doctorlist)

@app.route("/status",methods=["GET","POST"])
def status():
    con = mysql.connector.connect(
                   host ='localhost',
                   user='root',
                   password ='password',
                   database ='doctorapplication'
            )
    cursor = con.cursor()
    try:
        if request.method =="POST":
            select_status = request.form.get("selectstatus","").strip()
            doctor_id = request.form.get("doctor_id","")
            cursor.execute("update doctorlist set status =%s where doctor_id =%s",(select_status,doctor_id))
            con.commit()
            
            return redirect(url_for('add_doctor'))
    finally:
        cursor.close()
        con.close()        
    
    return render_template("afinddoctor.html")


@app.route("/admin/adding",methods=["GET","POST"])
def adding_doctor():
    if 'admin' not in session:
        return redirect(url_for('login'))
    con = mysql.connector.connect(
                       host ='localhost',
                       user='root',
                       password ='password',
                       database ='doctorapplication'
                )
    cursor = con.cursor()
    try:
        if request.method =="POST":
            
            doctor_name = request.form.get("doctor_name","").strip()
            doctor_sp = request.form.get("doctor_sp","").strip()
            years = Decimal(request.form.get("years","").strip())
            rating = request.form.get("rating","")
            fees = Decimal(request.form.get("fees","").strip())
            f = request.files['image']
            image_data = f.read()
            image_type = f.mimetype
            
            months =request.form.get("month","")
            day_one =request.form.get("day_one","").strip()
            day_two =request.form.get("day_two","").strip()
            day_three =request.form.get("day_three","").strip()
            from_time =request.form.get("time_from","")
            to_time =request.form.get("time_to","")
            
            if not all([doctor_name,doctor_sp,years,rating,fees,f,months,day_one,
                        from_time,to_time]):
                flash("Please fill the all field ! ","error")
                return render_template("adddoctor.html")
            
            cursor.execute("select count(*) from doctorlist where name =%s and specailist =%s",   (doctor_name,doctor_sp))
            exists = cursor.fetchone()[0]
            if exists:
                flash(f"{doctor_name} is already available", "error")
                return redirect(url_for('adding_doctor'))
            
            cursor.execute("INSERT INTO doctorlist (image,imagetype,name,specailist,year,rating,fees) VALUES (%s,%s,%s,%s,%s,%s,%s)",(image_data,image_type,doctor_name,doctor_sp,years,rating,fees))
            doctor_id = cursor.lastrowid 
            
            cursor.execute("insert into doctoravailability (doctor_id,doctor_name,months,day_1,day_2,    day_3,from_time,to_time) values (%s,%s,%s,%s,%s,%s,%s,%s)",(doctor_id,doctor_name,months,    day_one,day_two,day_three,from_time,to_time))
            
            con.commit()  
                
            flash(f"{doctor_name} is added successfully !","success")
            return redirect(url_for('adding_doctor'))
    
    except mysql.connector.IntegrityError as e:
        flash("database are not matching ","error")
        return redirect(url_for('adding_doctor'))
    
    except mysql.connector.Error as E:
        flash("database connection error ","error")
        return redirect(url_for('adding_doctor'))
    
    return render_template("adddoctor.html")

#edit the doctor 


@app.route("/admin/edit",methods=["GET","POST"])
def edit():
    if 'admin' not in session:
        return redirect(url_for('login'))
    
    doctor_id = request.args.get("doctor_id") or request.form.get('doctor_id')
    print(doctor_id)
    
    con = mysql.connector.connect(
                                    host ='localhost',
                                    user='root',
                                    password ='password',
                                    database ='doctorapplication'
                                )
    cursor = con.cursor()
    
    try:    
        if request.method =="POST":
            try:        
                doctor_name = request.form.get("doctor_name","").strip()
                doctor_sp = request.form.get("doctor_sp","").strip()
                years = Decimal(request.form.get("years","").strip())
                rating = request.form.get("rating","")
                fees = Decimal(request.form.get("fees","").strip())
                f = request.files.get('image')
                image_data = f.read()
                image_type = f.mimetype
                
                months =request.form.get("month","")
                day_one =request.form.get("day_one","").strip()
                day_two =request.form.get("day_two","").strip()
                day_three =request.form.get("day_three","").strip()
                from_time =request.form.get("time_from","")
                to_time =request.form.get("time_to","")
                
                if image_type == 'application/octet-stream':
                    cursor.execute("update doctorlist set name=%s,specailist=%s, year =%s,rating=%s,fees=%s where doctor_id =%s",(doctor_name,doctor_sp,years,rating,fees,doctor_id))
                    
                    cursor.execute("update doctoravailability set months=%s,day_1=%s,day_2=%s,    day_3=%s,from_time=%s,to_time=%s where doctor_id =%s",(months,day_one,day_two, day_three,from_time,to_time,doctor_id))
                    con.commit()
                    flash("doctor Data uploaded successfully","Error")
                    return redirect(url_for('edit',doctor_id=doctor_id))
                    
                
                cursor.execute("update doctorlist set image=%s,imagetype=%s,name=%s,specailist=%s,year =%s,rating=%s,fees=%s where doctor_id =%s",(image_data,image_type,doctor_name,doctor_sp,years,rating,fees,doctor_id))
                
                cursor.execute("update doctoravailability set months=%s,day_1=%s,day_2=%s,day_3=%s,from_time=%s,to_time=%s where doctor_id =%s",(months,day_one,day_two,day_three,from_time,to_time,doctor_id))
                con.commit()
                
            except mysql.connector.IntegrityError as e:
                flash("database table error ","error")
                return redirect(url_for('edit',doctor_id=doctor_id))
                
                
            flash("doctor Data uploaded successfully","Error")
            return redirect(url_for('edit',doctor_id=doctor_id))
        
        cursor.execute("select * from doctorlist where doctor_id = %s",(doctor_id,))
        doctor_data = cursor.fetchall()
        doctor = []
        for i in doctor_data:
            img = base64.b64encode(i[1]).decode('utf-8') if i[1] else ''    
            doctor.append({
                'image':img,
                'imagetype':i[2],
                'name':i[3],
                'specalist':i[4],
                'year':i[5],
                'rating':i[6],
                'fees':i[7],
            })
        cursor.execute("select*from doctoravailability where doctor_id = %s",(doctor_id,))
        datas = cursor.fetchall()
        
        return render_template("aedit.html",results= doctor,datas= datas,doctor_id=doctor_id)
 
   
    except mysql.connector.Error as e:
        flash(f"Database error: {e}", "error")
        print("eeror",e)
        return redirect(url_for('edit',doctor_id=doctor_id))
    
    finally:
        cursor.close()
        con.close()
        
@app.route("/admin/delete",methods=["GET","POST"])
def del_doctor():
    con = mysql.connector.connect(
                                        host ='localhost',
                                        user='root',
                                        password ='password',
                                        database ='doctorapplication'
                                    )
    cursor = con.cursor()
    try:
        cursor.execute("select * from doctorlist;")
        data = cursor.fetchall()
        
        doctorlist =[]
        for i in data:
            img = base64.b64encode(i[1]).decode('utf-8') if i[1] else ''
            doctorlist.append({
                'id':i[0],
                'image':img,
                'imagetype':i[2] ,
                'name':i[3],
                'specalist':i[4],
                'year':i[5],
                'rating':i[6],
                'fees':i[7],
                'status':i[8]
            })
        if request.method =='POST':
            doctor_id = request.form.get("doctor_id","")
            cursor.execute("delete from doctoravailability where doctor_id = %s",(doctor_id,))
            cursor.execute("delete from doctorlist where doctor_id = %s",(doctor_id,))
            con.commit()
            
            return redirect(url_for('add_doctor'))
    except mysql.connector.Error as e:
        print(f"database connection error {e}","error")
        return redirect(url_for('add_doctor'))
        
    finally:
        cursor.close()
        con.close()
    return render_template("afinddoctor.html",results = doctorlist)

        
    
# login page
@app.route("/login",methods=["GET"])
def login():
    if "username" in session:
        return redirect(url_for("home"))
    return render_template("login.html")

# home page

@app.route("/home",methods=["GET"])
def home():
    if "username" not in session:
        return redirect(url_for("fhome"))
    
    return render_template("Home.html")

# about page
@app.route("/about",methods=["GET"])
def aboutus():
    if "username" not in session:
        return redirect(url_for("fhome"))
    return render_template("about.html")


# create new page

@app.route("/createnew",methods=["GET"])
def create_new():
    return render_template("createnew.html")


# forgot password

@app.route("/forgot")
def forgot():
    return render_template("forgot.html")

@app.route("/newpassword",methods=["GET","POST"])
def newpassword():
    con = mysql.connector.connect(
                                host ='localhost',
                                user='root',
                                password ='password',
                                database ='doctorapplication'
                            )
    cursor = con.cursor()
    
    try:
        if request.method =='POST':
            phone = request.form.get("phone","").strip()
            password = request.form.get("password","").strip()
            
            if not all([phone,password]):
                flash("fill the feild first","error")
                return redirect(url_for('newpassword'))
            if not re.fullmatch(r"[0-9]{10}",phone):
                flash("Enter a valid 10 digit phone number", "error")
                return redirect(url_for('newpassword'))
            
                        
            cursor.execute("select user_id FROM useraccount where phone =%s",(phone,))
            user_id = cursor.fetchone()[0]
            
            if not user_id:
                flash("phone number is not match","error")
                return redirect(url_for('newpassword'))
            
            cursor.execute("update useraccount set password=%s where user_id=%s",(password,user_id))
            con.commit()
            flash("New password create successfully ! ","success")
            return redirect(url_for("login"))
    except mysql.connector.Error as e :
        flash("connection error","error")
        return redirect(url_for('newpassword'))
    
    finally:
        cursor.close()
        con.close() 
    return render_template("forgot.html")       

# profile relate code
# password change

@app.route("/password",methods=["GET"])
def passwords():
    if "username" not in session:
        return redirect(url_for("fhome"))
    return render_template("password.html")

# appointment history
@app.route("/history",methods=["GET","POST"])
def history():
    if 'username' not in session:
        return redirect(url_for("fhome"))
    con = mysql.connector.connect(
                               host ='localhost',
                               user='root',
                               password ='password',
                               database ='doctorapplication'
                        )
    cursor = con.cursor()
    username = session.get("username")
    
    try:
        cursor.execute("SELECT COUNT(*) FROM book_appointment where username =%s ",(username,))
        total = cursor.fetchone()[0]
        cursor.execute("select COUNT(*) FROM book_appointment where status =%s and username =%s ",('confirmed',username,))
        t_complete = cursor.fetchone()[0]
        cursor.execute("select COUNT(*) FROM book_appointment where status =%s and username =%s ",('cancel',username))
        cancel_t = cursor.fetchone()[0]
        
        page = request.args.get("page",1,type=int)
        per_page = 5
        if page <1:
            page=1
        offset = (page-1)*per_page
        total_page = max(1,math.ceil(total/per_page))
       
        cursor.execute("select * from book_appointment where username = %s limit %s offset %s",(username,per_page,offset))
        data = cursor.fetchall()
    except mysql.connector.Error as e:
        flash("error relate to database","error")
        return redirect(url_for('history'))
    finally:
        cursor.close()
        con.close()
    
    return render_template("history.html",results=data,total=total,t_complete=t_complete,cancel_t=cancel_t,page=page,offset=offset,total_page=total_page)


## delete history data
@app.route("/deletehistory",methods=["GET","POST"])
def deleteHistory():
    con = mysql.connector.connect(
                                   host ='localhost',
                                   user='root',
                                   password ='password',
                                   database ='doctorapplication'
                            )
    cursor = con.cursor()
    try:
        if request.method =="POST":
            booked_id = request.form.get("book_id","").strip()
            
            if not booked_id:
                flash("Booked_id is not avaialable","error")
                return redirect(url_for("deleteHistory"))
            
            cursor.execute("delete from book_appointment where book_id = %s",(booked_id,))
            con.commit()
            return redirect(url_for('history'))
    
    finally:
        cursor.close()
        con.close()
    
    return render_template("history.html")
            
    

@app.route("/profile",methods=["GET"])
def profile():
    con = mysql.connector.connect(
                           host ='localhost',
                           user='root',
                           password ='password',
                           database ='doctorapplication'
                    )
    cursor = con.cursor()
    username = session.get("username")

    try:
        cursor.execute("select * from useraccount where username =%s",(username,))
        data = cursor.fetchall()
    except mysql.connector.Error as E:
        flash("Database connection Error ","error")
        return redirect(url_for("profile"))
    finally:
        cursor.close()
        con.close()
    
    return render_template("profile.html",results=data)

# password changed
@app.route("/passwordchanged",methods=["GET","POST"])
def password_changed():
    if "username" not in session:
        return redirect(url_for("fhome"))
    
    con = mysql.connector.connect(
                       host ='localhost',
                       user='root',
                       password ='password',
                       database ='doctorapplication'
                )
    cursor = con.cursor()
    try:
        if request.method =="POST":
            old_pass = request.form.get("current","").strip()
            new_pass = request.form.get("newpassword","").strip()
            re_pass = request.form.get("password","").strip()
            
            if not all([old_pass,new_pass,re_pass]):
                flash("please write the password first ","error")
                return redirect(url_for("password_changed"))
            
            cursor.execute("select user_id FROM useraccount where passwords =%s",(old_pass,))
            data = cursor.fetchone()
            
            if data is None:
                flash("Your current password doesnot match","error")
                return redirect(url_for("password_changed"))
            
            user_id = data[0]
            
            if new_pass != re_pass:
                flash("New password is not match","error")
                return redirect(url_for("password_changed"))
            
            cursor.execute("update useraccount set passwords=%s where user_id = %s",(re_pass,user_id));
            con.commit()
            flash("Password changed successfully ! ","success")
            
            return redirect(url_for("passwords"))
    
    finally:
        cursor.close()
        con.close()
    
    return render_template("password.html")
              
    
    
# lagout 
@app.route("/logout",methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("fhome"))
    
    

# this for the login page
@app.route("/loginform",methods=["GET","POST"])
def login_account():
    con = mysql.connector.connect(
                   host ='localhost',
                   user='root',
                   password ='password',
                   database ='doctorapplication'
            )
    cursor = con.cursor()
    try:
        if request.method =="POST":
            username = request.form.get("named","").strip()
            password = request.form.get("password","").strip()
            
            if not all([username,password]):
                flash("fill the feild first","error")
                return redirect(url_for("login_account"))
            
            if username =='admin' and password=='admin123':
                session["admin"] = username
                return redirect(url_for('admin_home'))
            print(username,password)
                
            cursor.execute("SELECT COUNT(*) FROM useraccount where username =%s",(username,))
            user_value = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM useraccount where passwords =%s",(password,))
            password_value = cursor.fetchone()[0]
            
            
            if user_value >= 1 and password_value >= 1:
                session["username"] =username
                return redirect(url_for("home"))
            elif user_value >=1 and password_value ==0:
                flash("password is wrong ! ","error")
                return redirect(url_for("login_account"))
            else:
                flash("unauthorized is wrong ! ","error")
                return redirect(url_for("login_account"))
        
    except mysql.connector.Error as e:
        flash("mysql connection Error","error")
        return redirect(url_for("login_account"))
        
    finally:
        cursor.close()
        con.close()
        
    return render_template("login.html") 


# this is for the create account of the user

sender = os.environ.get("GMAIL_SENDER")
app_password = os.environ.get("GMAIL_APP_PASSWORD")

def send_code(to_email):
    code = str(random.randint(100000,999999))
    session["otp"] =code
    session["otp_time"] = time.time()
    session["otp_tries"] =0
    
    msg = EmailMessage()
    msg["Subject"] = "your verification code"
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(f" Your code is {code}. IT expires in 60 sec")
    
    
    with smtplib.SMTP_SSL("smtp.gmail.com",465) as s:
        s.login(sender,app_password)
        s.send_message(msg)
    


@app.route("/send_code",methods=["GET","POST"])
def new_account():
    con = mysql.connector.connect(
               host ='localhost',
               user='root',
               password ='password',
               database ='doctorapplication'
        )
    cursor = con.cursor()
    try:
        if request.method =="POST":
            
            gmail = request.form.get("email","").strip().lower()
            password = request.form.get("password","").strip()
            
            
            if not all([password,gmail]):
                flash("Please fill all fields", "error")
                return redirect(url_for("new_account"))
             
                    
            if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", gmail):
                flash("Enter a valid email address", "error")
                return redirect(url_for("new_account"))
                
            
            if len(password) <6:
                flash("Password must be at least 6 characters long","error")
                return redirect(url_for("new_account"))
            
            cursor.execute("select count(*) from useraccount where username = %s limit 1",(gmail,))
            data = cursor.fetchone()[0]
            if data == 1:
                flash(f"{gmail} is already in used","error")
                return redirect(url_for("new_account"))
            session["pending_email"] = gmail
            session["pending_pass"]  = password
            
            try:
                send_code(gmail)
            except Exception as e:     
                flash("Could not send email. Check the address and try again.", "error")
                return redirect(url_for("new_account"))
                    
            return redirect(url_for("verification"))
            
    except mysql.connector.Error:
        flash("database connection error , please try again","error")
        return redirect(url_for("new_account"))
        
        
    finally:
        cursor.close()
        con.close() 
    
    return render_template("createnew.html")

@app.route("/verification")
def verification():
    if "pending_email" not in session:
        return redirect(url_for('new_account'))
    return render_template("verif.html",email =session["pending_email"])

@app.route("/getverification",methods =["GET","POST"])
def verify():
    if "pending_email" not in session:
        return redirect(url_for('new_account'))
    
    if time.time() - session.get("otp_time",0)>120:
        flash("Code expired. Please sign up again.", "error")
        return redirect(url_for('new_account'))
    
    session["otp_tries"] = session.get("otp_tries",0)+1
    if session["otp_tries"] >5:
        flash("Too many attempts. Please sign up again.", "error")
        return redirect(url_for('new_account'))
    
    con = mysql.connector.connect(
               host ='localhost',
               user='root',
               password ='password',
               database ='doctorapplication'
        )
    cursor = con.cursor()
    if request.form.get("code", "").strip() != session.get("otp"):
        flash("Wrong code", "error")
        return redirect(url_for("verification"))
    try:
       cursor.execute("insert into useraccount (username,passwords,optcode) values(%s,%s,%s)",   (session["pending_email"], session["pending_pass"],session["otp"]))       
       con.commit()
         
    finally:
        cursor.close()
        con.close()
    for k in ("otp", "otp_time", "otp_tries", "pending_email", "pending_pass"):
        session.pop(k, None)            
    
    return render_template(url_for("login"))


def get_connection():
    return mysql.connector.connect(
           host ='localhost',
           user='root',
           password ='password',
           database ='doctorapplication'
    )


### show all data  relate doctor ....

@app.route("/finddoctor",methods =["GET","POST"])
def show():
    if "username" not in session:
        return redirect(url_for("fhome"))
    con = mysql.connector.connect(
           host ='localhost',
           user='root',
           password ='password',
           database ='doctorapplication'
    )
    cursor = con.cursor()
    try:
        cursor.execute("select * from doctorlist;")
        data = cursor.fetchall()
        doctorlist =[]
        for i in data:
            img = base64.b64encode(i[1]).decode('utf-8') if i[1] else ''
            doctorlist.append({
                'id':i[0],
                'image':img,
                'imagetype':i[2],
                'name':i[3],
                'specalist':i[4],
                'year':i[5],
                'rating':i[6],
                'fees':i[7],
                'status':i[8]
            })
        
        if request.method =="POST":
            input_data = request.form.get("input")
            pattern = "%"+input_data+"%"
            
            con = get_connection()
            cursor = con.cursor()
            cursor.execute("SELECT * FROM doctorlist WHERE name like %s OR specailist LIKE %s ",(pattern,pattern))
            data = cursor.fetchall()
            cursor.close()
            con.close()
            
            doctor=[]
            for i in data:
                img = base64.b64encode(i[1]).decode('utf-8') if i[1] else ''
                doctor.append(
                    {
                        'id':i[0],
                        'image':img,
                        'imagetype':i[2],
                        'name':i[3],
                        'specalist':i[4],
                        'year':i[5],
                        'rating':i[6],
                        'fees':i[7],
                        'status':i[8]
                    }
                )
            
            return render_template('finddoctor.html',results=doctor)

             
    finally:
        cursor.close()
        con.close()
    
    return render_template('finddoctor.html',results=doctorlist)

# not available
@app.route("/disable/<int:doctor_id>")
def disable(doctor_id):
    if "username" not in session:
        return redirect(url_for("gotologin"))
    con = mysql.connector.connect(
               host ='localhost',
               user='root',
               password ='password',
               database ='doctorapplication'
        )
    cursor = con.cursor()
    cursor.execute("select * from doctor_reason where id = %s", (doctor_id,))
    data = cursor.fetchall()
    return render_template("disable.html",results = data)
    

#  booked the doctor 

@app.route("/booked/<int:doctor_id>")
def take_appointment(doctor_id):
    if "username" not in session:
        return redirect(url_for("gotologin"))
    con = mysql.connector.connect(
           host ='localhost',
           user='root',
           password ='password',
           database ='doctorapplication'
    )
    cursor = con.cursor()
    cursor.execute("select * from  doctoravailability where doctor_id = %s;",(doctor_id,))
    data = cursor.fetchall()
    
    cursor.close()
    con.close()
    
    return render_template("book.html",results = data)

# image relate worked
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024*1024

# booking appointment or fill form
@app.route("/fillform",methods=["POST","GET"])
def fillforms(): 
    
    doctor_id = request.values.get("doctor_id", "").strip()   # works for GET and POST
    con = get_connection()
    cursor = con.cursor()
    status = 'confirmed'
    try:
        cursor.execute("select * from  doctorlist where doctor_id = %s", (doctor_id,))
        data = cursor.fetchall()
        
        cursor.execute("select * from  doctoravailability where doctor_id = %s",(doctor_id,))
        data2 = cursor.fetchall()
        
        if not data:
            flash("Doctor_id was not found", "error")
            return redirect(url_for("fillforms"))
    
        if not data2:
            flash("Doctor_id was not found", "error")
            return redirect(url_for("fillforms"))
        
        img = base64.b64encode(data[0][1]).decode('utf-8') if data[0][1] else ''
        doctor_name = data[0][2]
        doctor_specialist = data[0][3]
        username = session.get("username")
        payment = 'paid'
        
        
        if request.method =='POST':
            fullname = request.form.get("named","").strip()
            district = request.form.get("district","").strip()
            day = request.form.get("day","").strip()
            municipality = request.form.get("Municipality","").strip()
            ward = request.form.get("ward","").strip()
            phone = request.form.get("phone","").strip()
            email = request.form.get("email","").strip().lower() 
            fulladdress = district+" "+municipality+" "+ward
            
            # print({ "named": fullname, "district": district, "day": day,"Municipality": municipality, "ward": ward,"phone": phone, "email": email, "doctor_name": doctor_name})
            
            #  image relate worked
            f = request.files['image']
            image_data = f.read()
            image_type = f.mimetype
            
            if not image_data and image_type:
                flash("image isnot insert ","error")
                return render_template("book.html",doctor_id=doctor_id,results=data2)
                
            
            if not all([fullname,username,district,municipality,ward,day,phone,email,doctor_name,status,doctor_specialist]):
                flash("Please fill all fields", "error")
                return render_template("book.html",doctor_id=doctor_id,results=data2)
            
            
            if not re.fullmatch(r"9[78][0-9]{8}",phone):
                flash("Enter a valid 10 digit phone number", "error")
                return render_template("book.html",doctor_id=doctor_id,results=data2)
        
            if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
                flash("Enter a valid email address", "error")
                return render_template("book.html",doctor_id=doctor_id,results=data2)
            
            cursor.execute("select count(*) from book_appointment where  (doctor_name =%s and day_name = %s) and status = %s",(doctor_name,day,status))
            
            book_seat = cursor.fetchone()[0]
            
            if book_seat == 8 :
                flash(f"Sorry! All 8 appointment slots for this {day} are already booked. Please select another day. Thank you for your understanding!","error")
                return render_template("book.html",doctor_id=doctor_id,results=data2)

            
            cursor.execute("SELECT 1 FROM book_appointment WHERE doctor_name = %s AND phone = %s AND day_name = %s AND booking_time >= NOW() - INTERVAL 24 HOUR  LIMIT 1",(doctor_name,phone,day))
            if cursor.fetchone():
                flash("You already booked this doctor for that day", "error")
                return render_template("book.html",doctor_id=doctor_id,results=data2)
            
            
            cursor.execute("insert into payments (username,QR_image,image_type) values (%s,%s,%s)",(username,image_data,image_type))
             
            cursor.execute("INSERT INTO book_appointment  (doctor_name,specailist,fullname,address,phone,gmail,day_name,image,status,username,payment_s) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",(doctor_name,doctor_specialist,fullname,fulladdress,phone,email,day,img,status,username,payment))
            con.commit() 
            
            return redirect(url_for("booked"))                   
    
    except mysql.connector.Error as e:
        flash("unable to connect the database","error")
        return render_template("book.html",doctor_id=doctor_id,results=data2)
        
            
    finally:
        cursor.close()
        con.close()
        
    return render_template("book.html",results=data2)
        

@app.route("/booked_s",methods =["GET"])
def booked():
    return render_template("booked.html")

# this is for the myappointment of the project

@app.route("/show_appointment",methods=["GET"])
def show_Appoint():
    if "username" not in session:
        return redirect(url_for("fhome"))
    con = mysql.connector.connect(
           host ='localhost',
           user='root',
           password ='password',
           database ='doctorapplication'
    )
    cursor = con.cursor()
    cursor.execute("SELECT * FROM book_appointment WHERE TIMESTAMP(booking_data, booking_time) >= NOW() -INTERVAL 24 HOUR AND TIMESTAMP(booking_data, booking_time) <= NOW()")
    alldata = cursor.fetchall()
    cursor.close()
    con.close()
    appointment_list = []
    for i in alldata:
        img = (i[10]).decode('utf-8') if i[10] else ''
        appointment_list.append(
            {
                'id':i[0],
                'doctor_name':i[1],
                'doctor_spe':i[2],
                'fullname':i[3],
                'day':i[7],
                'date':str(i[8]),
                'time':str(i[9]),        # time and date for to store in json, otherwise error
                'image':img,
                'status':i[11],
                'username':i[12]
            }
        )  
    
        
    return render_template("myappointment.html",results = appointment_list)          


# searched Appointment 

@app.route("/searchAppointment",methods=["GET","POST"])
def searched_A():
    con = mysql.connector.connect(
        host ='localhost',
        user='root',
        password ='password',
        database ='doctorapplication'
    )
    cursor = con.cursor()
    if request.method =='POST':
        input = request.form.get("input","").strip()
        pattern ="%"+input+"%"
    
  
        cursor.execute("select * from book_appointment where (doctor_name like %s or fullname like %s) and TIMESTAMP(booking_data, booking_time) BETWEEN NOW() - INTERVAL 24 HOUR AND NOW() ",    (pattern,pattern))
        data = cursor.fetchall()
        cursor.close()
        con.close()
        data_1 = []
        for i in data:
            img =i[10].decode('utf-8') if i[10] else ''
            data_1.append({
                 'id':i[0],
                 'doctor_name':i[1],
                 'doctor_spe':i[2],
                 'fullname':i[3],
                 'day':i[7],
                 'date':str(i[8]),
                 'time':str(i[9]),        
                 'image':img,
                 'status':i[11],
                 'username':i[12]
            })
        
        return render_template("myappointment.html",results = data_1)  
    return render_template("myappointment.html")


@app.route("/cancel",methods=["GET","POST"])
def cancel():
    con = mysql.connector.connect(
            host ='localhost',
            user='root',
            password ='password',
            database ='doctorapplication'
        )
    cursor = con.cursor()
    status ='cancel'
    if request.method == 'POST':
        id = request.form.get("book_id","")
        cursor.execute("update book_appointment set status =%s where book_id =%s;",(status,id))
        con.commit()
        cursor.close()
        con.close()
        return redirect(url_for("show_Appoint"))
    
    return render_template("myappointment.html")


def datachange(row):
    data = []
    for i in row:
        img =i[10].decode('utf-8') if i[10] else ''
        data.append({
             'id':i[0],
             'doctor_name':i[1],
             'doctor_spe':i[2],
             'fullname':i[3],
             'day':i[7],
             'date':str(i[8]),
             'time':str(i[9]),        
             'image':img,
             'status':i[11],
             'username':i[12]
        })
    return data    

@app.route("/order",methods =["GET","POST"])
def ordering():
    if 'username' not in session:
        return redirect(url_for('f_myappointment'))
    con = mysql.connector.connect(
                host ='localhost',
                user='root',
                password ='password',
                database ='doctorapplication'
                )
    cursor = con.cursor()

    select_value = request.form.get("filter","").strip()
    order = {
            "alphabet":"fullname asc",
            "first":"book_id asc",
            "last":"book_id desc"
        }
    if select_value not in order:
            return redirect(url_for("show_Appoint"))
    try:
        cursor.execute(f"select * from book_appointment where TIMESTAMP(booking_data, booking_time) BETWEEN NOW() - INTERVAL 24 HOUR AND NOW() order by {order[select_value]}")
        data = cursor.fetchall()
    finally:
        cursor.close()
        con.close()  
    return render_template("myappointment.html",results = datachange(data),selected=select_value)
    
    
if __name__ =='__main__':
    app.run(debug=True)