
$(document).ready(function() {
    const socket = new WebSocket("ws://localhost:4000/ws");
    socket.onopen = () => console.log("✅ Connected to WebSocket");
    socket.onclose = () => console.log("❌ Disconnected");

    // Initialize jQuery Terminal
//    $("#terminal").terminal(async function(command, term) {
//        if (command.trim() === "") return;
//
//        return new Promise((resolve, reject) => {
//            socket.send(JSON.stringify({ command: command }));            
//            // Handle response from server
//            socket.onmessage = (event) => {
//                const response = JSON.parse(event.data);
//                resolve(response.return);
//            };
//
//            socket.onerror = () => reject("Error: Unable to connect to WebSocket");
//        });
//    }, {
//        greetings: "🚀 Welcome to Web CLI\nType commands below:",
//        prompt: "$ ",
//        history: true,
//        clear: false,
//        checkArity: false, // Allows any number of arguments
//        completion: function(command, callback) {
//            console.log("completion: "+command);
//            console.log("completion this: "+this.get_command());
//            // Example: Simple Tab Completion (can be replaced with dynamic data)
//            const availableCommands = ["ls", "cd", "pwd", "mkdir", "rm", "cp", "mv", "echo", "exit", "clear"];
//            callback(availableCommands.filter(cmd => cmd.startsWith(command)));
//        }
//    });

    $("#terminal").terminal("rpc", {
        greetings: "Greetings, Professor Falken!",
        completion: true,
        processRPCResponse: function(response) {
            $("#result").html(response);
        },
        onRPCError: function(err) {
            $("#error_message").html(err.message);
            $("#error_data").html(JSON.stringify(err.data));
        }
    })

});
