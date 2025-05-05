const recordButton = document.getElementById('record')
const result = document.getElementById('result')
recordButton.innerText = "Record"
const address = "localhost:5000"
let processing = false;

// Creates the room for the host and displays the host the code
document.getElementById('createRoom').addEventListener("click", function(event) {

    let code = Math.floor(Math.random() * 9000) + 1000;

    const formData = new FormData();
    formData.append('code', code);

    fetch('/room/host', {
        method: 'POST',
        body: formData
    })

    window.location.href = `room/host?code=${code}`;

})

// Will enter the person into the room if the code is valid
document.getElementById('joinRoom').addEventListener("click", function(event) {

    let code = document.getElementById('roomCode').value;

    const formData = new FormData();
    formData.append('code', code);

    fetch('/room/user', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.status == 926) {
            document.getElementById("errorMsg").innerText = "Invalid code. Please try again.";
            return;
        }

        window.location.href= `room/user?code=${code}`;
    })

})

// Upload button. Eventually we can use querySelector instead when we make classes for styling
document.getElementById('uploadForm').addEventListener('submit', function(event) {
    // Use normal HTTP requests here since we are sending one file a single time
    result.innerText = "Waiting for result";

    // Prevents a Method not Allowed error by allowing us to specify where the request is going instead of going to the default
    event.preventDefault();

    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    let upload_id;

    if (file) {
        const formData = new FormData();
        formData.append('file', file);

        fetch('/upload_file', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.status === 200) {
                console.log("File uploaded successfully (code 200)");
                // response.text() returns a promise which is asynchronous. We need to return it here so the next .then() statement can use it (it goes into upload_id)
                return response.text();
            } else if (response.status === 400) {
                console.log("File uploaded unsuccessfully (code 400)");
                throw new Error("File uploaded unsuccessfully (code 400)")
            } else if (response.status === 500) {
                console.log("File uploaded unsuccessfully (code 500)");
                result.innerText = "Failed with error code 500";
                throw new Error("File uploaded unsuccessfully (code 500)")
            }
        })
        .then(upload_id => {
            return fetch(`/display/${upload_id}`);
        })
        // response comes from the previous .then which returns from a fetch
        .then(response => response.text())
        .then(data => {
            result.innerText = data;
        })
        .catch(error => {
            console.error('Error uploading file:', error);
            result.innerText = 'Error uploading file.';
        });
    }
});

// Live record button
document.getElementById('recordHost').addEventListener('click', function(event) {
    if(document.getElementById('button')) {
        return;
    }
    // Since we are sending data quite often it is beneficial to use a websocket instead of remaking HTTP requests 100 times
    // https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder
    if (navigator.mediaDevices) {
        console.log("getUserMedia supported.");
        // ask for audio (microphone) access
        const constraints = { audio: true };
        // chunks will contain our audio
        let chunks = [];
        let recording = false;
        let headerBlob = null;
        result.innerText = "Result: "
    
        navigator.mediaDevices
        .getUserMedia(constraints)
        .then((stream) => {
            // create mediaRecorder object and start recording
            const mediaRecorder = new MediaRecorder(stream, {
                // webm format to improve compatibility (ogg didnt work for chrome)
                // https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder/mimeType
                mimeType: 'audio/webm'
              });
            // 1000 means ondatavailable will be called every 2000 ms or 2 seconds
            mediaRecorder.start(1000);

            // create socket https://socket.io/docs/v4/tutorial
            const socket = io(); 
            
            console.log("WebSocket created")
            socket.on('connect', () => {
                console.log("Websocket connected")
            })
            
            socket.on('disconnect', () => {
                console.log("Websocket disconnected")
            }) 
            recording = true;
            recordButton.innerText = "Recording";
            
            // create stop button
            const stopButton = document.createElement("button");
            stopButton.textContent = "Stop";
            document.body.appendChild(stopButton)

            stopButton.onclick = () => {
                console.log("Stop clicked");
                recordButton.innerText = "Record";
                mediaRecorder.stop(); 
                recording = false;
                document.body.removeChild(stopButton);
            }
            // change styling of website here while recording
            mediaRecorder.onstop = () => {
                console.log("Mediarecorder stopped")
                if(processing === false) {
                    // concatenate all remaining data we have and send it
                    // chunks should already contain header 
                    let concatenatedBlob = new Blob(chunks, { type: 'audio/webm' });
                    socket.emit('message', concatenatedBlob)
                    socket.close()
                }
            }
            // this aggregates data into chunks from the event e (takes place everytime new data is available)
            mediaRecorder.ondataavailable = async (e) =>  {
                console.log(chunks.length)
                // send to backend via websocket
                // await message so we dont overload backend
                if(headerBlob == null) {
                    console.log("headerBlob is null")
                    // get webm header. if we don't append this to every chunk we send it won't be recognized as valid
                    // get first 100 bytes
                    headerBlob = e.data.slice(0, 2000);
                    chunks.push(headerBlob)
                }  
                if(processing) {
                    chunks.push(e.data);
                    return;
                }
                chunks.push(e.data)
                // concatenate audio chunks and send to backend
                let conBlob = new Blob(chunks, { type: 'audio/webm' });
                socket.emit('message', conBlob) 
                console.log("Message sent")
                processing = true;
                // await response from server
                await new Promise((resolve, reject) => {
                    socket.on('message', (msg) => {
                        // formData fetch here and post msg to the backend wheere it is added to a data base
                        result.innerText = msg;
                        console.log(`MESSAGE RECEIVED ${msg}`);
                        resolve();
                    });
                })
                processing = false;
                // window.scrollTo(0, document.body.scrollHeight); cool bit we can do after text is transcribed
                // add an area below the icon and have text displayed there
                // need to change element from recordButton for that
            }
        })
        .catch((err) => {
            console.error(`Error occured: ${err}`)
        });
    }
})
