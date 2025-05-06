**SpeechLink, a live transcription service**

**What is SpeechLink?**

SpeechLink is a live transcription service meant for use in situations where spoken words may not be easily heard or audience members do not speak the speaker's language. SpeechLink allows a speaker to create a Host room, in which the Host can begin recording and broadcasting a live transcription of their speech to anyone who has joined their room via a sessionID (code).


**Developed with the following dependencies:**

Python 3.11.x (WhisperX will **NOT BUILD** with Python 3.12.x or Python 3.13.x)

Flask v3.1.0

Flask-Limiter v3.12

WhisperX v3.3.2

Flask-SocketIO v5.5.1

NOTE: To run WhisperX with CUDA support, you need Torch with CUDA. By default, installing WhisperX will install Torch with CPU support **ONLY**.

We recommend you to visit this page to get a GPU compatible Torch version for your system after installing WhisperX (https://pytorch.org/get-started/locally/)



**How to use:**

Navigate to the project folder in your terminal and open "runflask.py" via python. (ex. python runflask.py). VSCode is weird about file paths so make sure to use the terminal. After the server loads, you will see that it is hosted locally on 127.0.0.1:80. Go to that address in any web browser to view the website.

The software has three pages: the frontpage where you can create a room or join a room, the host page seen after creating a room, and the user page seen after joining a room.

To begin a transcription, simply click "Create New Room", allow microphone access when prompted, and click the Record button to begin recording audio.

Any person with a code can join the associated room to view a live transcription of audio spoken by the host of that room. 



**Known Bugs:**

The websocket seems to have a limit of 1 MB of data transfer which is reached after around 60 seconds of transcription. This helps to prevent abuse so we decided not to fix it immediately.



**In the event that you cannot get the software to work locally, please contact Levi Tipton via email (ltipto11@vols.utk.edu) to get a link to the hosted version.**
