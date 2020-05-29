from flask import Flask

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D://PL/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
