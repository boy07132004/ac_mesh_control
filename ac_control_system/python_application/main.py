import os
import logging
import requests
import threading
import command_handler
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from loader_from_root import SerialCommunication

PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200
MESH_ROOT = SerialCommunication(PORT, BAUD_RATE)
CMD_HANDLER = command_handler.CmdHandler(MESH_ROOT)

DATABASE = os.environ['INFLUXDB_DB']
DATABASE_HOST = os.environ['DATABASE_IP']

MAX_PEOPLE = 180

threading.Thread(target=MESH_ROOT.read_serial,
                 daemon=True, args=(CMD_HANDLER,)).start()


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

    if not (0 <= cmd <= 28):
        raise HTTPException(status_code=400, detail="Invalid command index.")

    if 20 > cmd >= 16:
        raise HTTPException(status_code=400, detail="Index duprecated.")

    if 28 >= cmd >= 20:
        cmd -= 4
    message["cmd"] = cmd

    MESH_ROOT.dispatch_command(message)
    if "group" in message:
        await CMD_HANDLER.monitor_group_send(cmd, message["group"])

    return {"result": "Finish"}


@app.get("/ac_control/check_people_in_area")
async def check_people():
    url = f"http://{DATABASE_HOST}:8086/query"
    params = {"db": DATABASE, "q": 'SELECT LAST(count) FROM "v5f_flow"'}

    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return {"result": "Failed request.", 'status_code': resp.status_code}

    people = resp.json().get('results', [{}])[0].get('series', [{}])[
        0].get('values', [[None, None]])[0][1]
    if people is None or type(people) is not int:
        return {"result": "Failed get result.", "resp": people}

    if people >= 0.8 * MAX_PEOPLE:
        logging.info(f"People over than 80%. All MID")
        await process_data("group", "Yellow", 11)
        await process_data("group", "Blue", 11)

    elif people >= 0.6 * MAX_PEOPLE:
        logging.info(
            f"People between 60% and 80%. Y: Wind > MID B: Wind > LOW")
        await process_data("group", "Yellow", 11)
        await process_data("group", "Blue", 12)

    else:
        logging.info(
            f"People less than 60%. Y: Wind > LOW B: turn off C301, D301, C401, D401")
        await process_data("group", "Yellow", 12)
        await process_data("dest", "C301", 2)
        await process_data("dest", "D301", 2)
        await process_data("dest", "C401", 2)
        await process_data("dest", "D401", 2)

    return {"count": people}


@app.get("/ac_control/list_online")
def list_online():
    return CMD_HANDLER.list_online()


@app.get("/ac_control/list_cmd")
def list_cmd():
    return {0: "讀取全部狀態", 1: "開機", 2: "關機",
            3: "讀取工作狀態", 4: "冷氣模式", 5: "送風模式",
            6: "讀取鎖定狀態", 7: "解鎖面板", 8: "鎖定面板",
            9: "讀取風速狀態", 10: "風速HIGH", 11: "風速MID", 12: "風速LOW",
            13: "讀取冰水閥", 14: "讀取室內溫度", 15: "讀取設定溫度",
            20: "設定溫度20度", 26: "設定溫度26度", 27: "設定溫度27度", 28: "設定溫度28度"
            }
