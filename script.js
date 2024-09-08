// Access the user's webcam and microphone
navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    .then(function(stream) {
        const localVideo = document.getElementById('localVideo');
        localVideo.srcObject = stream;
    })
    .catch(function(error) {
        console.error('Error accessing media devices.', error);
    });
