var functions = require('firebase-functions');
var admin = require('firebase-admin');
admin.initializeApp(functions.config().firebase);

function sendAlert(id, message, attachImage, callback) {

    var msg = 'Possible Gunman in Hall XYZ';
    
    if (message != null) {
        msg = message;
    }

    var payload = {
        notification: {
            'click_action': 'shooter_topic',
            'title': msg,
            'event_id': id
        }
    };

    if (attachImage) {
        // payload.notification['content_available'] = 'true';
        payload.notification['mutable_content'] = 'true';
    } else {
        payload.notification['body'] = 'Seek cover and wait for authorities.';
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
    sendAlert(req.body.message, false, function(error) {
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

        sendAlert('IMAGE OF THE SUSPECT:', true, function(error) {
            console.log('Sent suspect image.');
        });  

    //}, 1000);

    return true;
});

