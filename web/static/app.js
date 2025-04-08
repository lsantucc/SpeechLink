document.getElementById('uploadForm').addEventListener('submit', function(event) {
    document.getElementById('result').innerText = "Waiting for result";

    // Prevents a Method not Allowed error by allowing us to specify where the request is going instead of going to the default
    event.preventDefault();

    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    let upload_id;

    if (file) {
        const formData = new FormData();
        formData.append('file', file);

        fetch('/upload', {
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
            } else if (response.status === 500) {
                console.log("File uploaded unsuccessfully (code 500)");
            }
        })
        .then(upload_id => {
            return fetch(`/display/${upload_id}`);
        })
        // response comes from the previous .then which returns from a fetch
        .then(response => response.text())
        .then(data => {
            document.getElementById('result').innerText = data;
        })
        .catch(error => {
            console.error('Error uploading file:', error);
            document.getElementById('result').innerText = 'Error uploading file.';
        });
    }
});
