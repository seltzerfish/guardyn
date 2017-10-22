import requests
import pyrebase
import datetime

config = {
  "apiKey": "AIzaSyBFnI4X3DnGo5elpXnlj6Jzt1N_nxal7WA",
  "authDomain": "guardyn-vh.firebaseapp.com",
  "databaseURL": "https://guardyn-vh.firebaseio.com",
  "storageBucket": "guardyn-vh.appspot.com"
}

firebase = pyrebase.initialize_app(config)

def text_alert(alert_message, subbody="", complexion=None):
    r = requests.post('https://us-central1-guardyn-vh.cloudfunctions.net/sendAlert', data = {'message':alert_message, 'subbody':subbody, 'complexion':complexion})

def image_alert(image_path):
    storage = firebase.storage()
    storage.child("images/suspect_"+ str(datetime.datetime.now()) + ".png").put(image_path)

def upload_face(image_path):
    storage = firebase.storage()
    storage.child("images/face_"+ str(datetime.datetime.now()) + ".png").put(image_path)