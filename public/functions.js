// Establish a WebSocket connection with the server
const socket = new WebSocket('ws://' + window.location.host + '/websocket');

let webRTCConnection;

// Allow users to send messages by pressing enter instead of clicking the Send button
document.addEventListener("keypress", function (event) {
    if (event.code === "Enter") {
        sendItem();
    }
});


// Read the item name and quanity the user is sending to chat and send it to the server over the WebSocket as a JSON string
function sendItem() {
    const itemNameBox = document.getElementById("item-name");
    const itemName = itemNameBox.value;
    const quantityBox = document.getElementById("quantity");
    const quantity = quantityBox.value;
    const imageBox = document.getElementById("item-image");
    const image = imageBox.value.split('fakepath\\')[1];
    console.log(image);
    itemNameBox.value = "";
    quantityBox.value = "";
    imageBox.value = "";
    itemNameBox.focus();
    theJson = JSON.stringify({'messageType': 'chatMessage', 'item-name': itemName, 'quantity': quantity, 'image': image})
    console.log(theJson)
    if (itemName !== "") {
        socket.send(theJson);
    }
}

// Renders a new item to the page
function addMessage(chatMessage) {
    let chat = document.getElementById('items');
    chat.innerHTML += "<b>" + chatMessage['item-name'] + "</b>: " + chatMessage["quantity"] + "<br/>";  //<img src='"+chatMessage["image"];
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
        case 'chatMessage':
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
    document.getElementById("paragraph").innerHTML += "<br/>This text was added by JavaScript 🦆"

    get_chat_history()

    // use this line to start your video without having to click a button. Helpful for debugging
    // startVideo();
}

function displayList() {
    document.getElementById("pp").innerHTML += "<br/>Add items and submit to save list!"

    get_chat_history()

    // use this line to start your video without having to click a button. Helpful for debugging
    // startVideo();
}