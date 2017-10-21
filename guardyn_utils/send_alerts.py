import requests

def text_alert(alert_message):
    r = requests.post('https://us-central1-guardyn-vh.cloudfunctions.net/sendAlert', data = {'message':alert_message})