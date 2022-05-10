// Establish a WebSocket connection with the server
const socket = new WebSocket('ws://' + window.location.host + '/websocket');

let webRTCConnection;

// Allow users to send messages by pressing enter instead of clicking the Send button
document.addEventListener("keypress", function (event) {
    if (event.code === "Enter") {
        sendItem();
    }
});

function sendDM(){
    const userEmail = document.getElementById("user_email").value;
    const toUserBox = document.getElementById("to-user");
    const toUser = toUserBox.value;
    const messageBox = document.getElementById("dm");
    const message = messageBox.value;
    const theJson = JSON.stringify({'messageType': 'DirectMessage', 'from': userEmail, 
                            'to': toUser, 'message': message});
    socket.send(theJson);
    toUserBox.value = "";
    messageBox.value = "";
    toUserBox.focus();
}

// Read the item name and quanity the user is sending to chat and send it to the server over the WebSocket as a JSON string
function sendItem() {
    const itemNameBox = document.getElementById("item-name");
    const itemName = itemNameBox.value;
    const quantityBox = document.getElementById("quantity");
    const quantity = quantityBox.value;
    const listName = document.getElementById("list_name").value;
    var file = document.getElementById('item-image').files[0];
    var reader = new FileReader();
    var imageData = ""           
    reader.loadend = function() {
    } // do nothing
    reader.onload = function(e) {
        const rawData = e.target.result;
        imageData = rawData.replace('data:image/jpeg;base64,', '')
        const theJson = JSON.stringify({'messageType': 'addItem', 'list_name': listName, 
                            'item-name': itemName, 'quantity': quantity, 
                            'image_data': imageData});
        socket.send(theJson);
        // alert("the File has been transferred.")
        return imageData
    }
    reader.onerror = function(e) {
		console.log('Error : ' + e.type, "No image uploaded");
        alert("error");
	};
    if (file){
	    reader.readAsDataURL(file);
    }

    itemNameBox.value = "";
    quantityBox.value = "";
    itemNameBox.focus();
}

// Renders a new item to the page
function addMessage(addItem) {
    let chat = document.getElementById('items');
    chat.innerHTML += "<b>" + addItem['item-name'] + "</b>: " + addItem["quantity"] + "<br/>"+ "<img src='image/"+ addItem['img_name'] + "' class='post_images'> <br/>";
    console.log(addItem['img_name']);
}

// called when the page loads to get the chat_history
function get_chat_history() {
    const list_name = document.getElementById("list_name").value;
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            const messages = JSON.parse(this.response);
            for (const message of messages) {
                addMessage(message);
            }
        }
    };
    request.open("GET", "/list-"+list_name);
    request.send();
}


// Called whenever data is received from the server over the WebSocket connection
socket.onmessage = function (ws_message) {
    const message = JSON.parse(ws_message.data);
    const messageType = message.messageType
    switch (messageType) {
        case 'addItem':
            addMessage(message);
            console.log("messae",message)
            break;
        default:
            console.log("received an invalid WS messageType");
    }
}

function welcome() {}

function displayList() {
    document.getElementById("pp").innerHTML += "<br/>Add items and submit to save list!"

    get_chat_history()
}