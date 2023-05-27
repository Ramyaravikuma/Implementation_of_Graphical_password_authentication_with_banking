from flask import Flask,render_template,request,flash,redirect,url_for,session
import pymysql 
import random
import mysql.connector
import re
import hashlib
import datetime




app=Flask(__name__)
app.secret_key = 'super secret key'
now = datetime.datetime.now()
today=now.strftime("%d/%m/%Y")

conn=mysql.connector.connect(host="localhost",user="root",password="root",autocommit=True)
mycursor=conn.cursor(dictionary=True,buffered=True)
mycursor.execute("create database if not exists bank_db")
mycursor.execute("use bank_db")

mycursor.execute("create table if not exists bank_account(acc_no int primary key auto_increment,name varchar(30),email varchar(30) unique,mobile_no varchar(30),city char(30),gender varchar(30),bal int(6),password text, registration_date Text)")
mycursor.execute("create table if not exists transaction(acc_no int,amount int(6),ttype varchar(10),foreign key(acc_no) references bank_account(acc_no), transaction_date Text)")

# -----------homepage--------#
@app.route('/')
def index():
    return render_template('index.html')

# -----------contact--------#
@app.route('/contact')
def contact():
    return render_template("contact.html")     

# -----------signup--------#

@app.route('/signup')
def signup():
    N = 6
    images_ = random.sample(range(10, 46), N * N)
    images = []
    for i in range(0, N * N, N):
        images.append(images_[i:i + N])
    return render_template('signup.html',images=images)

@app.route('/signup', methods =['GET', 'POST'])
def signup_post():
    
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'mnum' in request.form and 'city' in request.form and 'gender' in request.form and 'balance' in request.form:
        name = request.form.get('name')
        email = request.form.get('email')
        mnum = request.form.get('mnum')
        city = request.form.get('city')
        gender = request.form.get('gender')
        balance=request.form.get('balance')
        
        
        if(request.form.get('row') and request.form.get('column')):
            row = request.form.get('row')
            col = request.form.get('column')
            password = row+col
            print(password, ".....")
        else:
            password_1 = sorted(request.form.getlist('password'))
            password_1 = ''.join(map(str, password_1))
            print("password is",password_1)
            if len(password_1) < 8:
                flash("password must be minimum 4 selections")
                return redirect(url_for('signup'))
            else:
                password = password_1
                result = hashlib.sha256(password.encode())
                password=result.hexdigest()
                print("password is",password)
        mycursor.execute("SELECT * FROM bank_account WHERE email = '"+ email +"' ")
        account = mycursor.fetchone()
        if account:
            flash('You are already registered, please log in')

        
        else:
            
            mycursor.execute("insert into bank_account values(NULL,'"+ name +"','"+ email +"','"+ mnum +"','"+ city +"','"+ gender +"','"+ balance +"','"+ password +"','"+ today +"')")
            msg=flash('You have successfully registered !')
            mycursor.execute("select acc_no,name,email,mobile_no,city,gender,bal from bank_account where email = '"+ email +"' ")
            account=mycursor.fetchone()
            
            account=account.values()
            print(account)
            li=[]
            for i in account:
                print(i)
                li.append(i)
            print(li)
            return render_template('singup_pro.html',data=li,msg=msg)
       
    
    return render_template('signup.html', msg = msg)


@app.route("/profile")
def profile():
    return render_template('singup_pro.html')

#----------login----------#


@app.route('/login')
def login():
    N = 6
    images_ = random.sample(range(10, 46), N * N)
    images = []
    for i in range(0, N * N, N):
        images.append(images_[i:i + N])
    return render_template('login.html',images=images)




@app.route('/login', methods =['GET', 'POST'])
def login_post():
    msg = ''
    global ACCOUNT_NO
    if request.method == 'POST' and 'email' in request.form and 'num' in request.form:
        email_id = request.form['email']
        ACCOUNT_NO = request.form['num']
        if(request.form.get('row') and request.form.get('column')):
            row = request.form.get('row')
            col = request.form.get('column')
            password = row+col
            print(password, ".....")
        else:
            password_1 = sorted(request.form.getlist('password'))
            password_1 = ''.join(map(str, password_1))
            if len(password_1) < 8:
                flash("password must be minimum 4 selections")
                return redirect(url_for('signup'))
            else:
                password = password_1
                result = hashlib.sha256(password.encode())
                password=result.hexdigest()
                print("password is",password)
        mycursor.execute("SELECT * FROM bank_account WHERE email = '"+ email_id +"' AND acc_no = '"+ ACCOUNT_NO +"' AND password ='"+ password +"'")
        account = mycursor.fetchone()

        print(type(account))
        if account:
            session['loggedin'] = True
            session['ACCOUNT_NO'] = account['acc_no']
            session['email_id'] = account['email']

            msg = flash('Logged in successfully !')
            print(msg)
            mycursor.execute("SELECT name,bal FROM bank_account WHERE acc_no = '"+ ACCOUNT_NO +"'")
            amount=mycursor.fetchone()
            amount=amount.values()
            money=list(amount)
            li=[]
            for i in money:
                print(i)
                li.append(i)
           
            return render_template('login_menu.html',msg=msg,amount=li)
        else:
            msg = flash('Incorrect username / password !')
            return render_template('login.html',msg=msg)
            
    return render_template('login.html')



@app.route('/deposit',methods =['GET', 'POST'])
def deposit():
    login_post()
    if request.method == 'POST' and 'anum' in request.form:
        acco_no=ACCOUNT_NO
        amount= request.form['anum']
        ttype="deposit"
        mycursor.execute("insert into transaction values('"+ acco_no+"','"+ str(amount)+"','"+ ttype+"','"+ today+"')")
        mycursor.execute("update bank_account set bal=bal+ '"+ str(amount)+"' where acc_no='"+ acco_no+"'")
        mycursor.execute("select bal from bank_account where acc_no= '"+ acco_no+"'")
        account=mycursor.fetchone()
        return render_template('deposit.html',account=account)
    return render_template('deposit.html')


@app.route('/withdrawal',methods =['GET', 'POST'])
def withdrawal():
    login_post()
    if request.method == 'POST' and 'anum' in request.form:
        acco_no=ACCOUNT_NO
        amount= request.form['anum']
        mycursor.execute("select bal from bank_account where acc_no='"+ acco_no+"'" )
        bal=mycursor.fetchone()
        bal=bal.values()
        # print(bal)
        for i in bal:
            pass
        balance=int(i)
        amount=int(amount)
        print("balance is",balance)
        if amount < balance:
            ttype="withdrawal"
            mycursor.execute("insert into transaction values('"+ acco_no+"','"+ str(amount)+"','"+ ttype+"','"+ today+"')")
            mycursor.execute("update bank_account set bal=bal- '" + str(amount)+"' where acc_no='"+ acco_no+"'")
            mycursor.execute("select bal from bank_account where acc_no= '"+ acco_no+"'")
            account=mycursor.fetchone()
            return render_template('withdrawal.html',account=account)    
        else:
            print("insufficient balance")
    return render_template('withdrawal.html')

@app.route('/transaction',methods =['GET', 'POST'])
def trans():  
    login_post()
    print(ACCOUNT_NO)
    mycursor.execute("SELECT bank_account.acc_no,bank_account.name,bank_account.bal,transaction.ttype,transaction.amount,transaction.transaction_date FROM bank_account  join transaction ON bank_account.acc_no=transaction.acc_no  where bank_account.acc_no='"+ ACCOUNT_NO+"'and transaction.acc_no='"+ ACCOUNT_NO+"'")
    account=mycursor.fetchall()
    #print(account)
    if len(account) == 0:
        msg= flash("You not yet transacted ")
        return render_template('trans.html',msg=msg)
    else:
        li=[]
        for i in account:
            accounts=i.values()
            accounts=list(accounts)
            print(accounts)
            li.append(accounts)
        return render_template('trans.html',account=li)
    
@app.route('/account_transfer')
def account_transfers():
    N = 6
    images_ = random.sample(range(10, 46), N * N)
    images = []
    for i in range(0, N * N, N):
        images.append(images_[i:i + N])
    return render_template('account_transfer.html',images=images)   

@app.route('/account_transfer',methods =['GET', 'POST'])
def account_transfer():
    login_post()
    msg = ''
    global ACCOUNT_NO
    if request.method == 'POST' and 'anum' in request.form and 'num' in request.form:
        acco_no=ACCOUNT_NO
        acc_no=request.form['num']
        amount= request.form['anum']
        if(request.form.get('row') and request.form.get('column')):
            row = request.form.get('row')
            col = request.form.get('column')
            password = row+col
            print(password, ".....")
        else:
            password_1 = sorted(request.form.getlist('password'))
            password_1 = ''.join(map(str, password_1))
            if len(password_1) < 8:
                flash("please select password")
                return redirect(url_for('account_transfer'))
            else:
                password = password_1
                result = hashlib.sha256(password.encode())
                password=result.hexdigest()
                print("password is",password)
        mycursor.execute("SELECT * FROM bank_account WHERE acc_no = '"+ ACCOUNT_NO +"' AND password ='"+ password +"'")
        account = mycursor.fetchone()
        print(type(account))
        if account:
            session['loggedin'] = True
            session['ACCOUNT_NO'] = account['acc_no']
            session['email_id'] = account['email']

            msg = flash('Logged in successfully !')
        mycursor.execute("select bal from bank_account where acc_no='"+ acco_no+"'" )
        bal=mycursor.fetchone()
        bal=bal.values()
        # print(bal)
        for i in bal:
            pass
        balance=int(i)
        amount=int(amount)
        print("balance is",balance)
        if amount < balance:
            ttype="wbank"
            ttyp="Dbank"
            mycursor.execute("insert into transaction values('"+ acco_no+"','"+ str(amount)+"','"+ ttype+"','"+ today+"')")
            mycursor.execute("update bank_account set bal=bal- '" + str(amount)+"' where acc_no='"+ acco_no+"'")
            mycursor.execute("insert into transaction values('"+ acc_no+"','"+ str(amount)+"','"+ ttyp+"','"+ today+"')")
            mycursor.execute("update bank_account set bal=bal+ '" + str(amount)+"' where acc_no='"+ acc_no+"'")
            mycursor.execute("select bal from bank_account where acc_no= '"+ acco_no+"'")
            account=mycursor.fetchone()
            return render_template('account_transfer.html',account=account)    
        else:
            print("insufficient balance")
    return render_template('account_transfer.html')



#----------admin----------#

@app.route('/admin', methods =['GET', 'POST'])
def admin():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        
        mycursor.execute("SELECT * FROM admin WHERE username = '"+ username +"' AND apassword = '"+ password +"'")
        account = mycursor.fetchone()
        print(account)
        if account:
            session['loggedin'] = True
            session['username'] = account['username']
            msg = flash('Logged in successfully !')
                
            return redirect(url_for('admin_profile', msg = msg))
        else:
            msg = flash('Incorrect username / password !')
            return render_template('admin.html',msg=msg)
    return render_template('admin.html')

@app.route('/admin_profile')
def admin_profile():
    mycursor.execute('SELECT acc_no,name,email,mobile_no,gender,bal FROM bank_account' )
    account = mycursor.fetchall()
    print(account)
    li=[]
    for i in account:
        accounts=i.values()
        accounts=list(accounts)
        print(accounts)
        li.append(accounts)
    print(li)
    return render_template('admin_profile.html',account=li)

@app.route('/cdata', methods =['GET', 'POST'])
def cdata():
    if request.method == 'POST' and 'account_no' in request.form and 'email' in request.form:
        Account_no = request.form['account_no']
        email_id = request.form['email']
        mycursor.execute("SELECT * FROM bank_account WHERE Acc_no = '"+ Account_no +"' AND email = '"+ email_id +"' ")
        data = mycursor.fetchone()
        print(data)
        data=data.values()
        datas=list(data)
        print(datas)
        return render_template('cdata.html',data=datas)
    return render_template('cdata.html')

@app.route('/cdata_profile', methods =['GET', 'POST'])
def cdata_profile():
    if request.method == 'POST' and 'num' in request.form:
        Account_no = request.form['num']
        mycursor.execute("SELECT bank_account.acc_no,bank_account.name,bank_account.bal,transaction.ttype,transaction.amount,transaction.transaction_date FROM bank_account  join transaction ON bank_account.acc_no=transaction.acc_no  where bank_account.acc_no='"+ Account_no+"'and transaction.acc_no='"+ Account_no+"'")
        account=mycursor.fetchall()
        print(account)
        li=[]
        for i in account:
            accounts=i.values()
            accounts=list(accounts)
            print(accounts)
            li.append(accounts)
        if len(li) == 0:
            print(li)
            msg= flash("You not yet transacted ")
            return render_template('cdata_profile.html',msg=msg)
        else:
            print(account)
            return render_template('cdata_profile.html',account=li)
    return render_template('cdata_profile.html')
 
@app.route('/money')
def money():
    mycursor.execute("SELECT bank_account.acc_no,bank_account.name,bank_account.bal,transaction.ttype,transaction.amount ,transaction.transaction_date FROM bank_account  join transaction ON bank_account.acc_no=transaction.acc_no where bank_account.bal  > 50000 and transaction_date='" +today+"'")        
    data=mycursor.fetchall()
    if len(data) == 0:
        msg= flash("Money laundering is not possible as per today data ")
        return render_template('money.html',msg=msg)
    else:
        li=[]
        for i in data:
            accounts=i.values()
            accounts=list(accounts)
            print(accounts)
            li.append(accounts)
        return render_template('money.html',account=li)

@app.route('/password_reset')
def password_Re():
    N = 6
    images_ = random.sample(range(10, 46), N * N)
    images = []
    for i in range(0, N * N, N):
        images.append(images_[i:i + N])
    return render_template('password_reset.html',images=images)

@app.route('/password_reset',methods =['GET', 'POST'])
def password_reset():
    msg = ''
    if request.method == 'POST' and 'pnum' in request.form and 'pemail' in request.form:
        ACCOUNT_NO = request.form.get('pnum')
        email = request.form.get('pemail')
        print("account num",ACCOUNT_NO)
        print("email",email)

        if(request.form.get('row') and request.form.get('column')):
            row = request.form.get('row')
            col = request.form.get('column')
            password = row+col
            print(password, ".....")
        else:
            password_1 = sorted(request.form.getlist('password'))
            password_1 = ''.join(map(str, password_1))
            if len(password_1) < 8:
                flash("password must be minimum 4 selections")
                return redirect(url_for('signup'))
            else:
                password = password_1
                result = hashlib.sha256(password.encode())
                password=result.hexdigest()
                print("password is",password)
        mycursor.execute("UPDATE bank_account SET password ='"+ password +"' WHERE Acc_no = '"+ ACCOUNT_NO +"' AND email = '"+ email +"' ")
        msg = flash('Successfully Reset!')
        return render_template('password_reset.html',msg=msg)
    return render_template('password_reset.html')
    
       
        
if __name__ =="__main__":
    app.run(debug=True)