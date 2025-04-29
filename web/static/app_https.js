const recordButton = document.getElementById('record')
const resultButton = document.getElementById('result')
recordButton.innerText = "Record"

async function getBuffer(chunks) {
    // need to get last 200 ms from chunks audio
    // first need to convert chunks audio into real audio

    // create blob 
    const blob = new Blob(chunks, { type: 'audio/webm' });
    const arrayBuffer = await blob.arrayBuffer();
    const audioContext = new AudioContext();
    const decodedAudio = await audioContext.decodeAudioData(arrayBuffer);
    
    // get length of audio clip
    const duration = decodedAudio.duration

    // extract the last 200 ms as a buffer

}

// Upload button. Eventually we can use querySelector instead when we make classes for styling
document.getElementById('uploadForm').addEventListener('submit', function(event) {
    resultButton.innerText = "Waiting for result";

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
                throw new error("File uploaded unsuccessfully (code 400)")
            } else if (response.status === 500) {
                console.log("File uploaded unsuccessfully (code 500)");
                resultButton.innerText = "Failed with error code 500";
                throw new error("File uploaded unsuccessfully (code 500)")
            }
        })
        .then(upload_id => {
            return fetch(`/display/${upload_id}`);
        })
        // response comes from the previous .then which returns from a fetch
        .then(response => response.text())
        .then(data => {
            resultButton.innerText = data;
        })
        .catch(error => {
            console.error('Error uploading file:', error);
            resultButton.innerText = 'Error uploading file.';
        });
    }
});

// Live record button
document.getElementById('record').addEventListener('click', function(event) {
    
    if (navigator.mediaDevices) {
        console.log("getUserMedia supported.");
        // ask for audio (microphone) access
        const constraints = { audio: true };
        // will contain our audio
        let chunks = [];
        let recording = false;
        let num_iteration = 0
    
        navigator.mediaDevices
        .getUserMedia(constraints)
        .then((stream) => {
            const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
            mediaRecorder.start(500);
            recording = true;
            recordButton.innerText = "Recording";
            // creates top button
            const stopButton = document.createElement("button");
            stopButton.textContent = "Stop";
            document.body.appendChild(stopButton)

            stopButton.onclick = () => {
                console.log("Stop clicked");
                mediaRecorder.stop(); 
                recording = false;
                recordButton.innerText = "Record";
                resultButton.innerText = "Transcribing..."

                document.body.removeChild(stopButton);
            }
            // change styling of website here while recording
            mediaRecorder.onstop = () => {
                // we have our final raw data since we stopped. send the data in e over to backend. 
                // to do this we fetch to the endpoint upload and attach the blob into a form and into the
                // body of the request
                const blobFormData = new FormData();
                const blob = new Blob(chunks, {type: "audio/webm"});
                blobFormData.append("audio", blob);
                fetch('/upload_raw_audio', {
                    method: 'POST',
                    body: blobFormData
                })
                .then(response => {
                    if (response.status === 200) {
                        console.log("File uploaded successfully (code 200)");
                        // response.text() returns a promise which is asynchronous. We need to return it here so the next .then() statement can use it (it goes into upload_id)
                        return response.text();
                    } else if (response.status === 401) {
                        console.log(response.textContent);
                        throw new error("File uploaded unsuccessfully (code 400)")
                    } else if (response.status === 500) {
                        console.log("File uploaded unsuccessfully (code 500)");
                        document.getElementById('result').innerText = "Failed with error code 500";
                        throw new error("File uploaded unsuccessfully (code 500)")
                    }
                })
                .then(upload_id => {
                    return fetch(`/display/${upload_id}`);
                })
                // response comes from the previous .then which returns from a fetch
                // need error checking on the fetch
                .then(response => response.text())
                .then(data => {
                    document.getElementById('result').innerText = data;
                })
                .catch(error => {
                    console.error('Error uploading file:', error);
                    document.getElementById('result').innerText = 'Error uploading file.';
                });
            }
            // this aggregates data into chunks from the event e (takes place everytime new data is available)
            mediaRecorder.ondataavailable = async (e) =>  {
                // called when 500 ms have passed.

                // push new data onto chunks
                chunks.push(e.data);

                const blobFormData = new FormData();
                const blob = new Blob(chunks, {type: "audio/webm"});
                blobFormData.append("audio", blob);
                fetch('/upload_raw_audio', {
                    method: 'POST',
                    body: blobFormData
                })
                .then(response => {
                    if (response.status === 200) {
                        console.log("File uploaded successfully (code 200)");
                        // response.text() returns a promise which is asynchronous. We need to return it here so the next .then() statement can use it (it goes into upload_id)
                        return response.text();
                    } else if (response.status === 401) {
                        console.log(response.textContent);
                        throw new error("File uploaded unsuccessfully (code 400)")
                    } else if (response.status === 500) {
                        console.log("File uploaded unsuccessfully (code 500)");
                        document.getElementById('result').innerText = "Failed with error code 500";
                        throw new error("File uploaded unsuccessfully (code 500)")
                    }
                })
                // get transcribed text as a rseponse
                .then(upload_id => {
                    return fetch(`/display/${upload_id}`);
                })
                // response comes from the previous .then which returns from a fetch
                // need error checking on the fetch
                // extract text
                .then(response => response.text())
                .then(data => {
                    // set text on frontend
                    document.getElementById('result').innerText = data;
                })
                // error checking
                .catch(error => {
                    console.error('Error uploading file:', error);
                    document.getElementById('result').innerText = 'Error uploading file.';
                });
            };
            })   
            .catch((err) => {
                console.error(`Error occured: ${err}`)
            });
    }
    })
