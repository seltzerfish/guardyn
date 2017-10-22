import requests
import pyrebase


config = {
  "apiKey": "AIzaSyBFnI4X3DnGo5elpXnlj6Jzt1N_nxal7WA",
  "authDomain": "guardyn-vh.firebaseapp.com",
  "databaseURL": "https://guardyn-vh.firebaseio.com",
  "storageBucket": "guardyn-vh.appspot.com"
}

firebase = pyrebase.initialize_app(config)

def text_alert(alert_message, now, subbody, complexion=None):
    r = requests.post('https://us-central1-guardyn-vh.cloudfunctions.net/sendAlert', data = {'message':alert_message, 'subbody':subbody, 'complexion':complexion, 'timestamp':now})

def image_alert(image_path, now):
    storage = firebase.storage()
    storage.child("images/suspect_"+ now + ".png").put(image_path)
    # storage.child("images/suspect.png").put(image_path)

def upload_face(image_path, now):
    storage = firebase.storage()
    storage.child("images/face_"+ now + ".png").put(image_path)