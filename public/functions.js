// Establish a WebSocket connection with the server
const socket = new WebSocket('ws://' + window.location.host + '/websocket');

let webRTCConnection;

// Allow users to send messages by pressing enter instead of clicking the Send button
document.addEventListener("keypress", function (event) {
    if (event.code === "Enter") {
        sendItem();
    }
});

function sendImage(){
    const imageBox = document.getElementById("item-image");
    const image = imageBox.value.split('fakepath\\')[1];
    console.log(image);
    imageBox.value = "";
    // , 'image': image
}

async function sendFile() {
    var file = document.getElementById('item-image').files[0];
    console.log(file)
    var reader = new FileReader();
    var rawData = new ArrayBuffer();            
    reader.loadend = function() {
    }
    reader.onload = function(e) {
        rawData = e.target.result;
        console.log(e.target.result);
        socket.send(theJson = JSON.stringify({'messageType': 'imageUpload', 'image_data': rawData}));
        alert("the File has been transferred.")
    }
    reader.onerror = function(e) {
		console.log('Error : ' + e.type);
	};
    if (file){
	    reader.readAsBinaryString(file);
    }
}

// async function sendFile(){
//     let formData = new FormData();
//     formData.append('file', imageupload.files[0]);
//     await fetch('/image-upload', {method: "POST", body: formData});
//     alert("the File has been transferred.");
//     socket.send(theJson = JSON.stringify({'messageType': 'imageUpload', 'image_data': "img_nmae.jpg"}));
// }

// function uploadFile(form)
// {
//  const formData = new FormData(form);
//  var oOutput = document.getElementById("static_file_response")
//  var oReq = new XMLHttpRequest();
//      oReq.open("POST", "upload_static_file", true);
//  oReq.onload = function(oEvent) {
//      if (oReq.status == 200) {
//        oOutput.innerHTML = "Uploaded!";
//        console.log(oReq.response)
//      } else {
//        oOutput.innerHTML = "Error occurred when trying to upload your file.<br \/>";
//      }
//      };
//  oOutput.innerHTML = "Sending file!";
//  console.log("Sending file!")
//  oReq.send(formData);
// }

// Read the item name and quanity the user is sending to chat and send it to the server over the WebSocket as a JSON string
function sendItem() {
    const itemNameBox = document.getElementById("item-name");
    const itemName = itemNameBox.value;
    const quantityBox = document.getElementById("quantity");
    const quantity = quantityBox.value;
    itemNameBox.value = "";
    quantityBox.value = "";
    itemNameBox.focus();
    theJson = JSON.stringify({'messageType': 'addItem', 'item-name': itemName, 'quantity': quantity})
    console.log(theJson)
    if (itemName !== "") {
        socket.send(theJson);
    }
}

// Renders a new item to the page
function addMessage(addItem) {
    let chat = document.getElementById('items');
    chat.innerHTML += "<b>" + addItem['item-name'] + "</b>: " + addItem["quantity"] + "<br/>"; //+ "<img src='image/flamingo.jpg'>";
}

// called when the page loads to get the chat_history
function get_chat_history() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            const messages = JSON.parse(this.response);
            for (const message of messages) {
                addMessage(message);
            }
        }
    };
    request.open("GET", "/chat-history");
    request.send();
}


// Called whenever data is received from the server over the WebSocket connection
socket.onmessage = function (ws_message) {
    const message = JSON.parse(ws_message.data);
    const messageType = message.messageType

    switch (messageType) {
        case 'addItem':
            addMessage(message);
            console.log(message)
            break;
        default:
            console.log("received an invalid WS messageType");
    }
}

function startVideo() {
    const constraints = {video: true, audio: true};
    navigator.mediaDevices.getUserMedia(constraints).then((myStream) => {
        const elem = document.getElementById("myVideo");
        elem.srcObject = myStream;

        // Use Google's public STUN server
        const iceConfig = {
            'iceServers': [{'url': 'stun:stun2.1.google.com:19302'}]
        };

        // create a WebRTC connection object
        webRTCConnection = new RTCPeerConnection(iceConfig);

        // add your local stream to the connection
        webRTCConnection.addStream(myStream);

        // when a remote stream is added, display it on the page
        webRTCConnection.onaddstream = function (data) {
            const remoteVideo = document.getElementById('otherVideo');
            remoteVideo.srcObject = data.stream;
        };

        // called when an ice candidate needs to be sent to the peer
        webRTCConnection.onicecandidate = function (data) {
            socket.send(JSON.stringify({'messageType': 'webRTC-candidate', 'candidate': data.candidate}));
        };
    })
}


function connectWebRTC() {
    // create and send an offer
    webRTCConnection.createOffer().then(webRTCOffer => {
        socket.send(JSON.stringify({'messageType': 'webRTC-offer', 'offer': webRTCOffer}));
        webRTCConnection.setLocalDescription(webRTCOffer);
    });
}

function welcome() {
    // document.getElementById("paragraph").innerHTML += "<br/>This text was added by JavaScript 🦆"

    // get_chat_history()

    // use this line to start your video without having to click a button. Helpful for debugging
    // startVideo();
}

function displayList() {
    document.getElementById("pp").innerHTML += "<br/>Add items and submit to save list!"

    get_chat_history()

    // use this line to start your video without having to click a button. Helpful for debugging
    // startVideo();
}