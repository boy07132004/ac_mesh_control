import logging
import threading
import loader_to_db
import command_handler
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from loader_from_root import SerialCommunication

PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200
MESH_ROOT = SerialCommunication(PORT, BAUD_RATE)
CMD_HANDLER = command_handler.CmdHandler(MESH_ROOT)

threading.Thread(target=MESH_ROOT.read_serial, daemon=True, args=(CMD_HANDLER,)).start()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("start")
    yield
    # Leave
    MESH_ROOT.close()

app = FastAPI(lifespan=lifespan)


@app.get("/ac_control/{dest}/{address}/{cmd}")
async def process_data(dest: str, address: str, cmd: int):
    message = {}
    if dest == "dest" or dest == "group":
        message[dest] = address
    else:
        raise HTTPException(
            status_code=400, detail="Invalid destination type.")

    if not (0 <= cmd <= 26):
        raise HTTPException(
            status_code=400, detail="Invalid command index.")

    message["cmd"] = cmd
    MESH_ROOT.dispatch_command(message)
    if "group" in message and message["group"] == "all": await CMD_HANDLER.monitor_all_send(cmd)


    return {"result": "Finish"}

@app.get("/ac_control/list_online")
def list_online():
    return CMD_HANDLER.list_online()

@app.get("/ac_control/list_cmd")
def list_cmd():
    return {0 : "讀取全部狀態", 1: "開機", 2: "關機", \
         3: "讀取工作狀態", 4: "冷氣模式", 5: "送風模式", \
         6: "讀取鎖定狀態", 7: "解鎖面板", 8: "鎖定面板", \
         9: "讀取風速狀態", 10: "風速HIGH", 11: "風速MID", 12: "風速LOW", \
         13: "讀取冰水閥", 14: "讀取室內溫度", 15: "讀取設定溫度", \
         16: "設定溫度20度", 22: "設定溫度26度", 23:"設定溫度27度", 24:"設定溫度28度"
    }
