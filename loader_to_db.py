import queue
import time
import threading
import logging
from datetime import datetime

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

PORT = '/dev/ttyUSB0'
BAUDRATE = 115200
USER = "admin"
PASSWORD = "admin"
DATABASE = "auo"
DATABASEHOST = "127.0.0.1"
PROJECT = "ac_ctl"
RETENTIONPOLICY = 'autogen'
BUCKET = f'{DATABASE}/{RETENTIONPOLICY}'

CLIENT = InfluxDBClient(
    url=f'http://{DATABASEHOST}:8086', token=f'{USER}:{PASSWORD}', org='my-org')


class DataQueueToDB(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        logging.basicConfig(filename='to_db.log', filemode='a',
                            format='%(name)s - %(levelname)s - %(message)s')
        self.dataQueue = queue.Queue(maxsize=0)
        self.command_map = ["on_off", "work_mode",
                            "locked", "curr_temp", "set_temp", "wind_speed"]

    def put_report_data(self, data):
        # {"device":"508A", "value":[0,1,2,3,4,5], "rssi":-10, "layer":1}
        device = data.get("device")
        value_array = data.get("value")

        if device is None or len(value_array) != len(self.command_map):
            logging.error(f"Data format error. > {data}")
            return

        p = Point(PROJECT).tag("device", device)
        p.field(self.command_map[0], ["Off", "On"][value_array[0]])
        p.field(self.command_map[1], ["Cool", "Fan", "Heat",
                                      "Auto Cool", "Auto Heat"][value_array[1]-1])
        p.field(self.command_map[2], ["Off", "On"][value_array[2]])
        p.field(self.command_map[3], value_array[3]/10.0)
        p.field(self.command_map[4], value_array[4]/10.0)
        p.field(self.command_map[5], ["High", "Mid", "Low", "AutoHigh",
                                      "AutoMid", "AutoLow", "AutoStop"][value_array[5]-1])

        rssi = data.get("rssi")
        if type(rssi) is int:
            p.field("rssi", rssi)

        layer = data.get("layer")
        if type(layer) is int:
            p.field("layer", layer)

        p.time(datetime.utcnow())

        self.dataQueue.put(p)

    def put_response_data(self, data):
        # {"device":"508A", "cmd":0, "value":1}
        device = data.get("device")
        cmd = data.get("cmd")
        value = data.get("value")

        if device is None or cmd is None or value is None \
                or cmd >= len(self.command_map):
            logging.error(f"Data format error. > {data}")
            return

        try:
            if cmd == 0:
                value = ["Off", "On"][value]
            elif cmd == 1:
                value = ["Cool", "Fan", "Heat",
                         "Auto Cool", "Auto Heat"][value-1]
            elif cmd == 2:
                value = ["Off", "On"][value]
            elif cmd == 3 or cmd == 4:
                value /= 10.0
            elif cmd == 5:
                value = ["High", "Mid", "Low", "AutoHigh",
                         "AutoMid", "AutoLow", "AutoStop"][value-1]

        except:
            logging.error(f"Command parse. > {data}")
            return

        p = Point(PROJECT).tag("device", device)
        p.field(self.command_map[cmd], value)
        p.time(datetime.utcnow())

        self.dataQueue.put(p)

    def upload(self):
        payload = ""

        while not self.dataQueue.empty():
            payload += (self.dataQueue.get().to_line_protocol() + "\n")

        CLIENT.write_api(write_options=SYNCHRONOUS).write(
            bucket=BUCKET, record=payload)

    def run(self):
        while True:
            if not self.dataQueue.empty():
                self.upload()
            else:
                logging.warning(f"{datetime.now()} -> Queue empty")

            time.sleep(5)
