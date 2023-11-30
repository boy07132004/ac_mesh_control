from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/ac_control/{dest}/{address}/{cmd}")
async def process_data(dest: str, address: str, cmd: int):
    message = {}
    if dest == "device" or dest == "group":
        message[dest] = address
    else:
        raise HTTPException(
            status_code=400, detail="Invalid destination type.")

    if not (0 <= cmd <= 10):
        raise HTTPException(
            status_code=400, detail="Invalid command index.")

    message["cmd"] = cmd
    print(message)
