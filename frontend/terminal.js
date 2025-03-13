const term = new Terminal({
    cursorBlink: true,
    rows: 20,
});
term.open(document.getElementById("terminal-container"));

const socket = new WebSocket("ws://localhost:4000/ws");

let commandBuffer = "";      // Current command being edited
let commandHistory = [];     // Stores past commands
let historyIndex = -1;       // Index for navigating history
let cursorPos = 0;           // Cursor position within the commandBuffer
const availableCommands = ["ls", "cd", "pwd", "mkdir", "rm", "cp", "mv", "touch", "cat", "echo", "exit", "clear"];

function cols(strings, padding = 2) {
    const termWidth = term.cols; // Get terminal width
    const colWidth = Math.max(...strings.map(s => s.length)) + padding; // Find max column width
    const numColumns = Math.max(1, Math.floor(termWidth / colWidth)); // Fit as many as possible

    // Organize strings into rows
    let output = "";
    for (let i = 0; i < strings.length; i++) {
        output += strings[i].padEnd(colWidth, " "); // Align columns
        if ((i + 1) % numColumns === 0 || i === strings.length - 1) {
            term.writeln(output);
            output = "";
        }
    }
    
}

socket.onopen = () => {
    term.writeln("Connected to backend...\n");
    prompt();  // Start terminal prompt
}

socket.onmessage = (event) => {
    const response = JSON.parse(event.data);
    if(response.hasOwnProperty("return")) {
        term.writeln("return: "+response.return); // Print server response
    } else if(response.hasOwnProperty("completions")) {
        suggestions = response.completions;
        if (suggestions.length == 1) {
            replaceFrom = commandBuffer.lastIndexOf(" ", cursorPos-1)+1
            commandBuffer = commandBuffer.slice(0, replaceFrom)+suggestions[0]
            cursorPos = commandBuffer.length;
        } else if (suggestions.length > 1) {
            term.writeln("");
            cols(suggestions);
        }
    } else {
        console.log("Message from server ", event);
        $("#debug").html(event.data);
    }
    prompt(); // Show prompt again
    updateDisplay()    
};

function prompt() {
    term.write("$ ");  // Custom prompt
}

function updateDisplay() {
    // Move cursor back, clear line, and reprint updated command
    term.write("\r\x1b[2K$ " + commandBuffer);
    // Reposition cursor to the correct place
    let moveLeft = commandBuffer.length - cursorPos;
    if (moveLeft > 0) term.write("\x1b[" + moveLeft + "D");
}

// Handles tab completion
function handleTabCompletion() {
    let linestart = 0
    while(linestart < commandBuffer.length && commandBuffer[linestart] === ' ') {
        linestart++
    }
    let line = commandBuffer.slice(linestart);
    let endidx = Math.max(cursorPos-linestart, 0);
    let splitAt = line.lastIndexOf(" ", endidx-1);
    let begidx = splitAt + 1
    if(splitAt == -1) {
        splitAt = 0
    }
    let text = line.slice(begidx, endidx);

    socket.send(JSON.stringify({ complete: {text: text, line: line, begidx: begidx, endidx: endidx} }));
}

term.onData((input) => {
    if (input === "\r") {  // Enter key
        if (commandBuffer.trim() !== "") {
            commandHistory.push(commandBuffer); // Save to history
            historyIndex = commandHistory.length;
        }
        term.write("\r\n");
        socket.send(JSON.stringify({ command: commandBuffer }));
        commandBuffer = "";
        cursorPos = 0;
    } else if (input === "\u007F") {  // Backspace
        if (cursorPos > 0) {
            commandBuffer = commandBuffer.slice(0, cursorPos - 1) + commandBuffer.slice(cursorPos);
            cursorPos--;
            updateDisplay();
        }
    } else if (input === "\x1b[A") {  // Arrow Up (History Back)
        if (historyIndex > 0) {
            historyIndex--;
            commandBuffer = commandHistory[historyIndex];
            cursorPos = commandBuffer.length;
            updateDisplay();
        }
    } else if (input === "\x1b[B") {  // Arrow Down (History Forward)
        if (historyIndex < commandHistory.length - 1) {
            historyIndex++;
            commandBuffer = commandHistory[historyIndex];
        } else {
            historyIndex = commandHistory.length;
            commandBuffer = "";
        }
        cursorPos = commandBuffer.length;
        updateDisplay();
    } else if (input === "\x1b[C") {  // Arrow Right (Move Cursor Right)
        if (cursorPos < commandBuffer.length) {
            cursorPos++;
            term.write("\x1b[C");
        }
    } else if (input === "\x1b[D") {  // Arrow Left (Move Cursor Left)
        if (cursorPos > 0) {
            cursorPos--;
            term.write("\x1b[D");
        }
    } else if (input === "\x1b[F") {  // End
        cursorPos = commandBuffer.length;
        pos = cursorPos + 2
        term.write("\r\x1b["+pos+"C");
    } else if (input === "\x1b[H") {  // Home
        cursorPos = 0;
        term.write("\r\x1b[2C");
    } else if (input === "\t") {  // Tab key (Autocomplete)
        handleTabCompletion();
    } else {  // Normal character input
        commandBuffer = commandBuffer.slice(0, cursorPos) + input + commandBuffer.slice(cursorPos);
        cursorPos++;
        updateDisplay();
    }
    $("#cursorPos").html(cursorPos);

});

