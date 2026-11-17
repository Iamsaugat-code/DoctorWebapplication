

from flask import Flask,jsonify,render_template,request,redirect,flash,url_for,session,Response
import mysql.connector
import base64
import re

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
    try:
        cursor.execute("select * from useraccount where username =%s",(username,))
        data = cursor.fetchone()
    finally:
        cursor.close()
        con.close()
    if data is None:
        return {"current_user":"none"}
    return {"current_user":data[2],"username":username}

# login page
@app.route("/",methods=["GET"])
def login():
    if "username" in session:
        return redirect(url_for("home"))
    return render_template("login.html")

# home page

@app.route("/home",methods=["GET"])
def home():
    if "username" not in session:
        return redirect(url_for("login"))
    
    return render_template("Home.html")

# about page
@app.route("/about",methods=["GET"])
def aboutus():
    if "username" not in session:
        return redirect(url_for("login"))
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
        return redirect(url_for("login"))
    return render_template("password.html")

# appointment history
@app.route("/history",methods=["GET","POST"])
def history():
    if 'username' not in session:
        return redirect(url_for("login"))
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

        cursor.execute("select * from book_appointment where username = %s",(username,))
        data = cursor.fetchall()
    except mysql.connector.Error as e:
        flash("error relate to database","error")
        return redirect(url_for('history'))
    finally:
        cursor.close()
        con.close()
    
    return render_template("history.html",results=data,total=total,t_complete=t_complete,cancel_t=cancel_t)


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
        return redirect(url_for("login"))
    
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
            
            cursor.execute("select user_id FROM useraccount where password =%s",(old_pass,))
            data = cursor.fetchone()
            
            if data is None:
                flash("Your current password doesnot match","error")
                return redirect(url_for("password_changed"))
            
            user_id = data[0]
            
            if new_pass != re_pass:
                flash("New password is not match","error")
                return redirect(url_for("password_changed"))
            
            cursor.execute("update useraccount set password=%s where user_id = %s",(re_pass,user_id));
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
    return redirect(url_for("login"))
    
    

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
                
        
            cursor.execute("SELECT COUNT(*) FROM useraccount where username =%s",(username,))
            user_value = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM useraccount where password =%s",(password,))
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


#  message_box:
message_box = {
    "gmail":"This email is already registered.",
    "username":"This username is taken.",
    "phone":"This phone number is already in use."
}

# this is for the create account of the user 

@app.route("/account",methods=["GET","POST"])
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
            username = request.form.get("named","").strip()
            fullname = request.form.get("fullname","").strip()
            password = request.form.get("password","").strip()
            phone = request.form.get("phone","").strip()
            gmail = request.form.get("email","").strip()
            
            # "" this respresent the default value
            
            if not all([username,fullname,password,phone,gmail]):
                flash("Please fill all fields", "error")
                
                return redirect(url_for("new_account"))
                # return render_template("createnew.html")
                
            
            if not re.fullmatch(r"[0-9]{10}",phone):
                flash("Enter a valid 10 digit phone number", "error")
                return redirect(url_for("new_account"))
                return render_template("createnew.html")
                    
            if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", gmail):
                flash("Enter a valid email address", "error")
                return redirect(url_for("new_account"))
                # return render_template("createnew.html")
                
            
            if len(password) <6:
                flash("Password must be at least 6 characters long","error")
                # return redirect(url_for("new_account"))
                return render_template("createnew.html")
                
            
            cursor.execute("insert into useraccount (username,fullname,password,phone,gmail) values(%s,%s,%s,%s,%s)",(username,fullname,password,phone,gmail))
            con.commit()
            flash("new account create successfully! ","success")
            return redirect(url_for("login"))
    except mysql.connector.IntegrityError as e:
        con.rollback()
        if e.errno == 1062:
            key = e.msg.split("for key")[-1].strip(" '").split(".")[-1]
            flash(message_box.get(key,"duplicate value"),"error")
                    # if 'username' in key.lower():
                    #     feild_e ="username"
                    # elif 'phone' in key.lower():
                    #     feild_e ="phone"
                    # elif 'gmail' in key.lower():
                    #     feild_e ="gmail"
                    # else:
                    #     flash("duplicate data is detected ! ","error")
            return redirect(url_for("new_account"))
            # return render_template("createnew.html")
                         
        else:
            flash("database error : ","error")
            # return render_template("createnew.html")
            return redirect(url_for("new_account"))
            
    except mysql.connector.Error:
        flash("database connection error , please try again","error")
        # return render_template("createnew.html")
        return redirect(url_for("new_account"))
        
        
    finally:
        cursor.close()
        con.close() 
    
    return render_template("createnew.html")


def get_connection():
    return mysql.connector.connect(
           host ='localhost',
           user='root',
           password ='password',
           database ='doctorapplication'
    )

### data are searched 
@app.route("/dataSearched",methods=["POST","GET"])
def searchedData():
    if request.method =='POST':
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
                    'name':i[2],
                    'specalist':i[3],
                    'year':i[4],
                    'rating':i[5],
                    'fees':i[6],
                    'status':i[7]
                }
            )
        
        return render_template("finddoctor.html",results = doctor)
    
    return render_template("finddoctor.html")



### show all data  relate doctor ....

@app.route("/finddoctor",methods =["GET"])
def show():
    if "username" not in session:
        return redirect(url_for("login"))
    con = mysql.connector.connect(
           host ='localhost',
           user='root',
           password ='password',
           database ='doctorapplication'
    )
    cursor = con.cursor()
    cursor.execute("select * from doctorlist;")
    data = cursor.fetchall()
    cursor.close()
    con.close()
    
    doctorlist =[]
    for i in data:
        img = base64.b64encode(i[1]).decode('utf-8') if i[1] else ''
        doctorlist.append({
            'id':i[0],
            'image':img,
            'name':i[2],
            'specalist':i[3],
            'year':i[4],
            'rating':i[5],
            'fees':i[6],
            'status':i[7]
        }) 
    
    return render_template('finddoctor.html',results=doctorlist)

# not available
@app.route("/disable/<int:doctor_id>")
def disable(doctor_id):
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
    if "username" not in session:
        return redirect(url_for("login"))
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
            
            if not re.fullmatch(r"[0-9]{10}",phone):
                flash("Enter a valid 10 digit phone number", "error")
                return render_template("book.html",doctor_id=doctor_id,results=data2)
        
            if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
                flash("Enter a valid email address", "error")
                return render_template("book.html",doctor_id=doctor_id,results=data2)
            
            cursor.execute("SELECT 1 FROM book_appointment WHERE doctor_name = %s AND phone = %s AND day_name = %s AND booking_time >= NOW() - INTERVAL 24 HOUR  LIMIT 1",(doctor_name,phone,day))
            if cursor.fetchone():
                flash("You already booked this doctor for that day", "error")
                return render_template("book.html",doctor_id=doctor_id,results=data2)
            
            
            cursor.execute("insert into payments (username,QR_image,image_type) values (%s,%s,%s)",(username,image_data,image_type))
             
            cursor.execute("INSERT INTO book_appointment  (doctor_name,specailist,fullname,address,phone,gmail,day_name,image,status,username,payment_s) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",(doctor_name,doctor_specialist,fullname,fulladdress,phone,email,day,img,status,username,payment))
            con.commit() 
            
            return redirect(url_for("booked"))
                    
        return render_template("book.html",results=data2)
    
    except mysql.connector.Error as e:
        flash("unable to connect the database","error")
        return render_template("book.html",doctor_id=doctor_id,results=data2)
        
            
    finally:
        cursor.close()
        con.close()

# imaged last part
@app.route("/pic")
def picture():
    con = mysql.connector.connect(
               host ='localhost',
               user='root',
               password ='password',
               database ='doctorapplication'
        )
    cursor = con.cursor()
    username = session.get("username")
    cursor.execute("select * from payments where username =%s order by pay_id desc",(username,))
    data = cursor.fetchone()
    
    if not data or data[2] or data[3]:
        flash("no data is available ","error")
    
    return Response(data[2],mimetype=data[3])
    

@app.route("/booked_s",methods =["GET"])
def booked():
    return render_template("booked.html")

# this is for the myappointment of the project

@app.route("/show_appointment",methods=["GET"])
def show_Appoint():
    if "username" not in session:
        return redirect(url_for("login"))
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
    
  
        cursor.execute("select * from book_appointment where doctor_name like %s or fullname like %s ",    (pattern,pattern))
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
    print("ordering route is running")
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
        cursor.execute(f"select * from book_appointment order by {order[select_value]};")
        data = cursor.fetchall()
    finally:
        cursor.close()
        con.close()  
    return render_template("myappointment.html",results = datachange(data),selected=select_value)
    
    
if __name__ =='__main__':
    app.run(debug=True)