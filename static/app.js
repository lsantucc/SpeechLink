// The main javascript code for index.html 

document.addEventListener("DOMContentLoaded", function () {
    let result = document.getElementById('result')
    const address = "localhost:5000"

    let processing = false;

    // Creates the room for the host and displays the host the code
    document.getElementById('createRoom').addEventListener("click", function(event) {
        let code = Math.floor(Math.random() * 9000) + 1000;

        const formData = new FormData();
        formData.append('code', code);
        // Use POST request to send SessionID to backend for storage in database
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
        // Send session ID to backend
        fetch('/room/user', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            // Error checking to see if code is valid
            if (response.status == 926) {
                document.getElementById("errorMsg").innerText = "Invalid code. Please try again.";
                return;
            }

            window.location.href= `room/user?code=${code}`;
        })

    })
});