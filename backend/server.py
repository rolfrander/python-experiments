from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles

from typing import Any, Callable, Dict, Optional, Union, List
from pydantic import BaseModel
import inspect
from pathlib import Path

class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: List[Any] = []
    id: str | int | None = None

class JSONRPCError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[JSONRPCError] = None
    id: str | int | None = None

def rpc_method(name = None):
    """Decorator to register a method as a JSON-RPC callable."""
    def decorator(func: Callable):
        if name is not None:            
            func._rpc_method_name = name
        else:
            func._rpc_method_name = func.__name__
        return func
    return decorator

class JSONRPCHandler:
    """A generic JSON-RPC 2.0 request handler."""
    
    def __init__(self):
        self.methods: Dict[str, Callable] = {}
        self.register_annotated_methods()

    def register_method(self, name: str, func: Callable):
        """Registers a method that can be called via JSON-RPC."""
        if not callable(func):
            raise ValueError(f"Method {name} is not callable")
        self.methods[name] = func
    
    def register_annotated_methods(self):
        """Registers all methods of an object decorated with @rpc_method."""
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, "_rpc_method_name"):
                print("register method {}".format(attr))
                self.register_method(attr._rpc_method_name, attr)

    def system_describe(self):
        procs = []
        for m in self.methods.keys():
            procs.append({"name": m,
                          "params": inspect.getfullargspec(self.methods[m]).args[1:]})
        
        return {"sdversion": "1.0",
                "name": "none",
                "id": "5254ca32-01a8-11f0-b983-e0d4e8770aeb",
                "procs": procs}

    def completedefault(self, text, line, begidx, endidx):
        return []

    def system_completions(self, text, line, begidx, endidx):
        if begidx == 0:
            return [x for x in self.methods.keys() if x.startswith(text)]
        else:
            cmd = line.split(maxsplit=1)[0]
            complete_fn = getattr(self, "complete_"+cmd)
            print("complete '{}': {}".format(cmd, complete_fn))
            if callable(complete_fn):
                return complete_fn(text, line, begidx, endidx)
            else:
                return self.completedefault(text, line, begidx, endidx)

    def process_request(self, request: JSONRPCRequest) -> JSONRPCResponse:
        """Processes a JSON-RPC request and returns a JSON-RPC response."""
        try:
            if request.jsonrpc != "2.0" or not isinstance(request.method, str):
                return JSONRPCResponse(id=request.id, error=JSONRPCError(code=-32600, message="Invalid Request"))

            if request.method == "system.describe":
                return JSONRPCResponse(id=request.id, result=self.system_describe())
            
            if request.method == "system.completions":
                return JSONRPCResponse(id=request.id, result=self.system_completions(*request.params))

            if request.method not in self.methods:
                return JSONRPCResponse(id=request.id, error=JSONRPCError(code=-32601, message="Method not found: {}".format(request.method)))

            result = self.methods[request.method](*request.params)

            return JSONRPCResponse(id=request.id, result=result)
        except Exception as e:
            return JSONRPCResponse(id=request.id, error=JSONRPCError(code=-32603, message="Internal error", data=str(e)))

app = FastAPI()

class Cmd(JSONRPCHandler):
    @rpc_method()
    def add(self, x: int, y: int):
        return x+y

    @rpc_method()
    def sub(self, x: int, y: int):
        return x-y

    def complete_cat(self, text, line, begidx, endidx):
        return [f.name for f in Path(".").iterdir() if f.is_file() and f.name.startswith(text)]

    @rpc_method()
    def cat(self, args):
        with open(args, "r") as input:
            return input.readlines()

cmd = Cmd()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        json = await websocket.receive_json()
        rpcrequest = JSONRPCRequest.model_validate(json)
        print("process {}".format(rpcrequest))
        ret = cmd.process_request(rpcrequest)
        await websocket.send_text(ret.model_dump_json())

@app.post("/rpc")
async def handle_rpc(request: JSONRPCRequest):
    return cmd.process_request(request)

app.mount("/js", StaticFiles(directory="../frontend/node_modules"), name="node_modules")

app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
