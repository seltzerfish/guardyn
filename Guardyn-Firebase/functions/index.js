var functions = require('firebase-functions');
var admin = require('firebase-admin');
admin.initializeApp(functions.config().firebase);

exports.sendAlert = functions.https.onRequest((req, res) => {
    

    var msg = '';
    if (req.body.message != null) {
        msg = req.body.message;
    }

    var payload = {
        notification: {
          title: 'Possible Active Shooter',
          body: msg
        }
    };

    const topic = 'shooter_topic';    
    admin.messaging().sendToTopic(topic, payload)
        .then(function(response) {
      
        console.log('Successfully sent message:', response);
        res.send('Sent.')
      
    })
    .catch(function(error) {
        console.log('Error sending message:', error)
        res.send('Error.')
    });
    
});