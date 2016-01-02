var messageText = document.getElementById("messageText");
var sendButton = document.getElementById("sendButton");
var userName = prompt("Enter your name:");

if(typeof(WebSocket)!="undefined") {
    var socket = new WebSocket("ws://127.0.0.1:8888/messages/");

    sendButton.onclick = function(){
        socket.send(userName + ": " + messageText.value);
    };

    socket.onopen = function () {
        console.log("Socket opened");
    };
    socket.onclose = function (event) {
    };
    socket.onmessage = function (event) {
        var messagesDiv = document.getElementById("messages");
        messagesDiv.innerHTML = event.data + "<br>" + messagesDiv.innerHTML;
    };
}
