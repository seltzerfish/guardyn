var functions = require('firebase-functions');
var admin = require('firebase-admin');
admin.initializeApp(functions.config().firebase);

function sendAlert(id, title, message, attachImage, callback) {

    var notifTitle = 'Possible Gunman in Hall XYZ';
    var notifMessage = 'Seek cover and wait for authorities';
    
    if (title != null) {
        notifTitle = title;
    }

    if (message != null) {
        notifMessage = message;
    }

    var payload = {
        notification: {
            'click_action': 'shooter_topic',
            'title': notifTitle,
            'body': notifMessage,
            'event_id': id
        }
    };

    if (attachImage) {
        payload.notification['mutable_content'] = 'true';
    } 

    const topic = 'shooter_topic';    
    admin.messaging().sendToTopic(topic, payload)
        .then(function(response) {
      
        console.log('Successfully sent message:', response);
        callback(null);
        
    }).catch(function(error) {

        console.log('Error sending message:', error);
        callback(error);

    });
}

exports.sendAlert = functions.https.onRequest((req, res) => {
    sendAlert('12', req.body.message, req.body.subbody, false, function(error) {
        if (error == null) {
            res.send('Payload Delivered.');
        } else {
            res.send('Error sending notification:', error);
        }
    });
});

exports.sendSuspectMessage = functions.storage.object().onChange(event => {
    console.log('Received trigger from file storage');
    
    if (event.data.resourceState === 'not_exists') {
        console.log('This is a deletion event.');
        return true;
    }

    //setTimeout(function() {
    sendAlert('12', 'Image of the suspect:', '', true, function(error) {
        console.log('Sent suspect image.');
    });  
    //}, 1000);

    
    return true;
});

