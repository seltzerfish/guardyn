var functions = require('firebase-functions');
var admin = require('firebase-admin');
var path = require('path');

admin.initializeApp(functions.config().firebase);

function sendAlert(title, message, callback) {

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
            'body': notifMessage
        }
    };

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

function sendMessageAlert(title, callback) {
        
        var payload = {
            notification: {
                'click_action': 'shooter_topic',
                'title': title,
                'mutable_content': 'true'
            }
        };
    
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

    sendAlert(req.body.message, req.body.subbody, function(error) {
        if (error == null) {
            res.send('Payload Delivered.');
        } else {
            res.send('Error sending notification:', error);
        }
    });

    function formatAMPM(date) {
        var hours = date.getHours();
        var minutes = date.getMinutes();
        var ampm = hours >= 12 ? 'pm' : 'am';
        hours = hours % 12;
        hours = hours ? hours : 12; // the hour '0' should be '12'
        minutes = minutes < 10 ? '0'+minutes : minutes;
        var strTime = hours + ':' + minutes + ' ' + ampm;
        return strTime;
    }

    var timeString = formatAMPM(new Date());

    var detailsString = 'Deadly weapon detected in Hallway XYZ @ ' + timeString + '.';
    if (req.body.complexion != null) {
        detailsString += ' The suspect appeared to have a ' + req.body.complexion + ' complexion.';
    }

    var timestamp = req.body.timestamp;
    
    var suspectImageUrl = 'https://firebasestorage.googleapis.com/v0/b/guardyn-vh.appspot.com/o/images/'
        + 'suspect_' + timestamp;
    var faceImageUrl = 'https://firebasestorage.googleapis.com/v0/b/guardyn-vh.appspot.com/o/images/'
        + 'face_' + timestamp;

    var event = {
        cameraLocation: {
            description: 'Hallway XYZ',
            lat: 36.142972,
            long: -86.805722    
        },
        details: detailsString,
        suspectImageUrl: suspectImageUrl,
        faceImageUrl: faceImageUrl,
        timestamp: new Date().toISOString()
    }
    // Create Alert here
    admin.database().ref('/events').push(event);
});

exports.sendSuspectMessage = functions.storage.object().onChange(event => {
    console.log('Received trigger from file storage');

    const fileName = path.basename(event.data.name);

    if (!fileName.startsWith('suspect_')) {
        console.log('No need to send the non-suspect images.');
        return true;
    }
    
    if (event.data.resourceState === 'not_exists') {
        console.log('This is a deletion event.');
        return true;
    }

    sendMessageAlert('Image of the suspect:', function(error) {
        console.log('Sent suspect image.');
    });  
    
    return true;
});

