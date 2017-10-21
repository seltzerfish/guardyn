var functions = require('firebase-functions');
var admin = require('firebase-admin');
admin.initializeApp(functions.config().firebase);

function sendAlert(message, attachImage, callback) {

    var msg = 'Possible Gunman in Hall XYZ';
    
    if (message != null) {
        msg = message;
    }

    var payload = {
        notification: {
            'click_action': 'shooter_topic',
            'title': msg,
            'sound': 'signal',
        }
    };

    if (attachImage) {
        payload.notification['content_available'] = 'true';
        payload.notification['mutable_content'] = 'true';
    } else {
        payload.notification['body'] = 'Seek cover and wait for authorities.';
    }

    const topic = 'shooter_topic';    
    admin.messaging().sendToTopic(topic, payload)
        .then(function(response) {
      
        console.log('Successfully sent message:', response);

        if (callback != null) {
            callback(null);
        }
    }).catch(function(error) {

        console.log('Error sending message:', error);
        
        if (callback != null) {            
            callback(error);
        }

    });
}

exports.sendAlert = functions.https.onRequest((req, res) => {
    
    sendAlert(req.body.message, false, function(error) {
        if (error == null) {
            res.send('Payload Delivered.');
        } else {
            res.send('Error sending notification:', error);
        }
    });
});

exports.sendSuspectMessage = functions.storage.object().onChange(event => {
    sendAlert('Here\'s what the suspect looks like:', true, function(){});
});