1) install mongodb
https://www.mongodb.com/dr/fastdl.mongodb.org/win32/mongodb-win32-x86_64-2012plus-4.2.8-signed.msi/download

2) add mongodb to environment variables
 i) controlpanel > system > advanced system settings > environment variables > 
	add to path C:\Program Files\MongoDB\Server\4.2\bin

3) make sure mongodb is running

4) do database restore from provided dump
	i)  go to project directory > dump 
	ii) open command prompt as administrator
	iii) change directory to '08-23' 
		> cd "08-23  dump"
	iv) > mongorestore .

5) install python 32 bit - WORKS ONLY ON 32 BIT PYTHON as machine learning model has been trained with 32 bit python
6) add python to environment variables
 i) controlpanel > system > advanced system settings > environment variables > 
	add to path 
		C:\Users\'Your Username'\AppData\Local\Programs\Python\Python37-32

6) install python package installer 'pip' with
	Project Directory> python get-pip.py
7) install all required packages with pip 
	pip install flask
	pip install bcrypt
	pip install time
	pip install pymongo
	pip install flask_login
	pip install joblib
	pip install pandas
	pip install sklearn

8) run application with 
	Project Directory> python app.py

9) credentials for administrator is 
 
	username: admin
	password: admin
10) doctor and patient can be registered within the system

		