const recordButton = document.getElementById('record')
const result = document.getElementById('result')
recordButton.innerText = "Record"
const address = "localhost:5000"
let processing = false;

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

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
document.getElementById('record').addEventListener('click', function(event) {
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
            // 2000 means ondatavailable will be called every 2000 ms or 2 seconds
            mediaRecorder.start(2000);

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
            mediaRecorder.onstart = () => {
                sleep(30);
                headerBlob = mediaRecorder.requestData();
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
                    console.log("null")
                    // get webm header. if we don't append this to every chunk we send it won't be recognized as valid
                    headerBlob = e.data;
                    chunks.push(headerBlob)
                }
                // processing refers to if we are currently awaiting a response from the server or not
                if(processing) {
                    chunks.push(e.data)
                    console.log("processing happening pushing chunk for later")
                    return
                }
                console.log("Processing is false, sending chunk")
                chunks.push(e.data)
                // concatenate audio chunks and send to backend
                let conBlob = new Blob(chunks, { type: 'audio/webm' });
                socket.emit('message', conBlob) 
                console.log("Message sent")
                
                // reset chunks. if we want to pass the audio cumulatively (helpful for context, better transcription) then don't do this
                //chunks = [];
                chunks.length = 0;
                // push header to make next audio chunk valid
                chunks.push(headerBlob);

                processing = true;
                // await response from server
                await new Promise((resolve, reject) => {
                    socket.on('message', (msg) => {
                        result.innerText += msg;
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
