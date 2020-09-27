from flask import *
from flask_login import logout_user
import bcrypt
import time
import pymongo
from pymongo import MongoClient
from joblib import dump, load
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


#connect to MongoDB
client = MongoClient()
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
app = Flask(__name__,template_folder="static")
db = myclient["healthAI"]
col = db["users"]

#first page
@app.route('/')
def home():
    if request.method == 'POST' :
        if request.form.get('Admin')=='Admin':
            return redirect(url_for('admin'))       #SECTION - 3
        if request.form.get('Doctor')=='Doctor':
            return redirect(url_for('doctor'))      #SECTION - 2
        if request.form.get('Patient')=='Patient':
            return redirect(url_for('patient'))     #SECTION - 1
    return render_template('home.html')

##########################################################################
#####################.... START OF SECTION - 1 ....#######################

@app.route('/patient',methods=['POST','GET'])
def patient():
    if request.method == 'POST' :
        if request.form.get('Sign In')=='Sign In':
            return redirect(url_for('sign_in'))
        if request.form.get('Sign Up')=='Sign Up':
            return redirect(url_for('sign_up'))
    return render_template('patient.html')


@app.route('/sign_in',methods=['POST','GET'])
def sign_in():
    if request.method == 'POST' :
        current_username = request.form['username']
        login_user = col.find_one({'username' : current_username})
        if login_user:
        #check the password
            if bcrypt.hashpw(request.form['password'].encode('utf-8'),  login_user['password']) ==  login_user['password']:
                uname = login_user['name']
                _name = login_user['name']
                _gender = login_user['gender']
                
                return redirect(url_for('patient_details',name=_name,gender=_gender))
        flash('Invalid username or password')
                
    return render_template('sign_in.html')
    

@app.route('/sign_up',methods=['POST','GET'])
def sign_up():
    message = ''
    if request.method == 'POST' :
        name = request.form['Firstname']
        surname = request.form['Lastname']
        email = request.form['email']
        gender = request.form['Gender']
        user = request.form['Username']
        password = request.form['password']
        existing_user = col.find_one({'username' : user})
        if existing_user:
            message = 'This username already exist! Try another one'

        #check if user already exist
        if existing_user is None:
            hashpass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) #hash the password

            #insert data in database
            col.insert_one({'name' : name, 'surenane' : surname, 'email' : email, 'gender' : gender, 'password' : hashpass, 'username':user})

            session['username'] = name
            return redirect(url_for('sign_in'))

    return render_template('sign_up.html', message = message)


@app.route('/patient_details',methods=['POST','GET'])
def patient_details() :
    #login_user
    if request.method == 'POST' :
        if request.form.get('Disease Prediction')=='Disease Prediction':
            return redirect(url_for('prediction',name=request.args.get('name'),gender=request.args.get('gender')))
        if request.form.get('Doctor Search')=='Doctor Search':
            return redirect(url_for('doctor_search'))
        #if request.form.get('My Details')=='My Details':
            #return render_template('patient_details.html',name=name,gender=gender)
            #return redirect(url_for('patient_details',name=name,gender=gender))
        
    return render_template('patient_details.html',name=request.args.get('name'),gender=request.args.get('gender')) #TODO


@app.route('/prediction',methods=['POST','GET'])
def prediction(name='sud1',gender='sud1'):
    b=[]
    a=[]
    collection = db.dataset
    # predicted = db.predicted_disease
    symptoms_collection = db.symptoms
    symptoms = [(symptom["symptom"], symptom["symptom"].replace('_',' ')) for symptom in symptoms_collection.find()]


    allkeys = collection.find_one()
    for mykey in allkeys:
        a.append(mykey)
    print(a)
    a = a[:-1]
    if request.method == 'POST' :
        b.append(request.form['symptom0'])
        b.append(request.form['symptom1'])
        b.append(request.form['symptom2'])
        b.append(request.form['symptom3'])
        b.append(request.form['symptom4'])
        b.append(request.form['symptom5'])

        c = [i for i, item in enumerate(a) if item in b]
        count=len(c)
        bucket = [0]* len(a)
        for i in range(0,count):
                bucket[c[i]]=1
        print(bucket)
        test_data = [bucket]
        p = predict_symptom(test_data)
        flash(p)
        uname = col.find_one({'name' : name})
        #predicted.insert_one({'name' : name, 'surnane' : uname['surname'], 'email' : uname['email'], 'contact' : uname['contact'],
                    #'gender' : uname['gender'], 'symptom0' : b[0], 'symptom1':b[1], 'symptom2': b[2],'symptom3': b[3],'symptom4':b[4], 'symptom5':b[5], 'disease':p})

    return render_template('prediction.html', symptoms=symptoms)


def predict_symptom(test_data):
    try:    # Load Trained Model
        clf = load('random_forest.joblib')
    except Exception as e:   
        print(e)

    if test_data is not None:
        result = clf.predict(test_data)
        return result


@app.route('/doctor_search',methods=['POST','GET'])
def doctor_search():
    doc = db.doctors_data
    if request.method == 'POST' :
        fi = request.form['search']
        print(fi)
        try:
            stri = str(fi)
            li=[]
            
            allkeys = doc.find({'name' : stri})
            for mykey in allkeys:
                li.append(mykey)
            
            allkeys = doc.find({'address' : stri})
            for mykey in allkeys:
                li.append(mykey)
                
            allkeys = doc.find({'type' : stri})
            for mykey in allkeys:
                li.append(mykey)
                
            print(li)
            #if (key_doc['name']==li[0] or key_doc['type']==li[2])
            
            return render_template('search.html',data=li)
        except Exception as e:
            print(e)
            return render_template('search.html')
    return render_template('search.html')

#####################..... END OF SECTION - 1 .....#######################
##########################################################################




##########################################################################
#####################.... START OF SECTION - 2 ....#######################

@app.route('/doctor',methods=['POST','GET'])
def doctor():
    doc = db.doctors_data
    if request.method == 'POST' :
        doc_username = request.form['username']
        login_user = doc.find_one({'username' : doc_username})
        if login_user:
        #check the password
            if request.form['password'] ==  login_user['password']:
                session['username'] = login_user['name']
                print(request.form['password'],login_user['password'])
                return redirect(url_for('doctor_patient_list'))
        flash('Invalid username or password')
                
    return render_template('doctor.html')


@app.route('/doctor_patient_list',methods=['POST','GET'])
def doctor_patient_list():
    
    patient = col.find()
    if request.method == 'POST' :
        if request.form.get('Disease Details')=='Disease Details':
            return redirect(url_for('doctor_disease_list'),patient)
        if request.form.get('Patient Details')=='Patient Details':   
            return render_template('doctor_patient_list.html',patient=patient)
    return render_template('doctor_patient_list.html',patient=patient)



@app.route('/doctor_disease_list',methods=['POST','GET'])
def doctor_disease_list():
    a=[]
    collection = db.dataset
    allkeys = collection.find()
    for mykey in allkeys:
        a.append(mykey)
     
    return render_template('doctor_disease_list.html',a=a)


#####################.... END OF SECTION - 2 ....#######################
########################################################################



########################################################################
#####################....START OF SECTION - 3....#######################

@app.route('/admin',methods=['POST','GET'])
def admin():
    if request.method == 'POST' :
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            return redirect(url_for('admin_disease',uname='admin'))
        flash('Invalid username or password')
    return render_template('admin.html')



@app.route('/admin_disease',methods=['POST','GET'])
def admin_disease():
    a=[]
    collection = db.dataset
    allkeys = collection.find()
    for mykey in allkeys:
        a.append(mykey)


    if request.method == 'POST' :

        if request.form.get('Doctor_Details')=='Doctor Details':
            return redirect(url_for('admin_doctor',request.args.get('uname')))
        if request.form.get('Patient Details')=='Patient Details':
            return redirect(url_for('admin_patient',request.args.get('uname')))
        if request.form.get('Disease Details')=='Disease Details':
            return redirect(url_for('admin_disease',request.args.get('uname')))

        Symptom = request.form.get('Symptom')
        Disease = request.form.get('Disease')
        if (Symptom != None) and (Disease != None): 
            collection.insert_one({str(Symptom) : Symptom, 'prognosis' : Disease})
            flash('successfully inserted!')
        flash('Insert both fields!')
        
    return render_template('admin_disease.html',a=a)            



@app.route('/admin_doctor',methods=['POST','GET'])
def admin_doctor():
    doc = db.doctors_data
    data = doc.find()
    if data==None:
        data = []
    if request.method == 'POST' :
        name = request.form.get('Name')
        address = request.form.get('address')
        category = request.form.get('Type')
        username = request.form.get('uname')
        password = request.form.get('pwd')
        doc.insert_one({"name" : name, "address" : address, "type" : category, "username" : username, "password" : password})
        
        flash('successfully inserted 1 new doctor!')
        
        if request.form.get('Doctor Details')=='Doctor Details':
            return redirect(url_for('admin_doctor',request.args.get('uname')))
        if request.form.get('Patient Details')=='Patient Details':
            return redirect(url_for('admin_patient',request.args.get('uname')))
        if request.form.get('Disease Details')=='Disease Details':
            return redirect(url_for('admin_disease',request.args.get('uname')))
        
    return render_template('admin_doctor.html', data = data)


@app.route('/admin_patient',methods=['POST','GET'])
def admin_patient():
    collection = db.users
    data = collection.find()

    return render_template('admin_patient.html',data=data)



#####################.... END OF SECTION - 3 ....#######################
########################################################################



'''
#logout activity
@app.route("/logout")
def logout():
    session['username'] = None
    return redirect(url_for('host'))
'''

#main
if __name__ == "__main__":
    app.secret_key = 'sud'
    app.run(debug=True,port=8080)
