

$(document).ready(function() {
    const socket = new WebSocket("ws://localhost:4000/ws");
    socket.onopen = () => console.log("✅ Connected to WebSocket");
    socket.onclose = () => console.log("❌ Disconnected");
    var commandCnt = 0;

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

    function rpc(command, parameters) {
        input = {
            jsonrpc: "2.0",
            method: command,
            params: parameters,
            id: commandCnt++
        }
        return new Promise((resolve, reject) => {
            socket.send(JSON.stringify(input));
            socket.onmessage = (event) => {
                const response = JSON.parse(event.data);
                if(response.result) {
                    resolve(response.result);
                } else if(response.error) {
                    reject(response.error);
                } else {
                    reject({code: 1, message: "unknown error", data: null})
                }
            };

            socket.onerror = () => reject({code: 2, message: "Error: Unable to connect to WebSocket", data: null});
        });
    }

    var element_result = $("#result");
    var element_error_message = $("#error_message");
    var element_error_data = $("#error_data");

    function handle_result(resp) {
        element_result.html(resp)
    }

    function handle_error(json_rpc_error) {
        element_error_message.html(json_rpc_error.message);
        element_error_data.html(JSON.stringify(json_rpc_error.data));
    }
    
    $("#terminal").terminal(function(command) {
        cmdline = command.split(" ").filter((word) => word.length > 0);
        rpc(cmdline[0], cmdline.slice(1)).then(handle_result, handle_result);
    }, {
        greetings: "Greetings, Professor Falken!",
        completion: function(command, callback) {
            let cursorPos = this.get_position();
            let linestart = 0
            while(linestart < command.length && command[linestart] === ' ') {
                linestart++;
            }
            let line = this.get_command().slice(linestart);
            let endidx = Math.max(cursorPos-linestart, 0);
            let splitAt = line.lastIndexOf(" ", endidx-1);
            let begidx = splitAt + 1
            if(splitAt == -1) {
                splitAt = 0
            }
            let text = line.slice(begidx, endidx);
            $("#linestart").html(linestart);
            $("#cursorPos").html(cursorPos);
            $("#text").html(text);
            $("#line").html(line);
            $("#begidx").html(begidx);
            $("#endidx").html(endidx);
            rpc("system.completions", [text, line, begidx, endidx]).then(callback, handle_error);
        },
        height: 100
    });

//    $("#terminal").cmd({
//        prompt: "> ",
//        commands: function(command) {
//            cmdline = command.split(" ").filter((word) => word.length > 0);
//            rpc(cmdline[0], cmdline.slice(1)).then((resp) => { $("#result").html(resp) })
//        },
//        keymap: {
//            'TAB': function() {
//            console.log("tab");
//            this.focus();
//        }}
//    })
});
