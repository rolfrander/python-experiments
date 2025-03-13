from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles

COMMANDS = ["ls", "cd", "pwd", "mkdir", "rm", "cp", "mv", "touch", "cat", "echo", "exit", "clear"]

PARAMS = ["alcohol",
"arrival",
"article",
"audience",
"bath",
"birthday",
"camera",
"cell",
"city",
"classroom",
"clothes",
"college",
"committee",
"communication",
"complaint",
"control",
"conversation",
"courage",
"data",
"dealer",
"decision",
"department",
"description",
"difficulty",
"direction",
"dirt",
"discussion",
"disk",
"distribution",
"drama",
"establishment",
"event",
"examination",
"expression",
"family",
"flight",
"goal",
"government",
"grocery",
"growth",
"hair",
"health",
"highway",
"imagination",
"importance",
"injury",
"inspection",
"leader",
"library",
"magazine",
"management",
"manufacturer",
"meaning",
"member",
"mixture",
"mood",
"mud",
"nature",
"night",
"people",
"perception",
"person",
"policy",
"possession",
"possibility",
"potato",
"power",
"presentation",
"quality",
"relation",
"resource",
"sample",
"satisfaction",
"series",
"setting",
"signature",
"situation",
"skill",
"skill",
"software",
"song",
"stranger",
"student",
"success",
"supermarket",
"sympathy",
"tale",
"teacher",
"temperature",
"theory",
"topic",
"tradition",
"transportation",
"vehicle",
"virus",
"week",
"world"]

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        print(data.__class__, data)
        if "command" in data:
            ret = {"return": data["command"]}
        elif "complete" in data:
            if data["complete"]["begidx"] == 0:
                ret = {"completions": [x for x in COMMANDS if x.startswith(data["complete"]["text"])]}
            else:
                ret = {"completions": [x for x in PARAMS if x.startswith(data["complete"]["text"])]}
        else:
            ret = data
        await websocket.send_json(ret)

app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
