import json
import serial
import threading
import loader_to_db

DEBUG_MODE = False


class SerialCommunication:
    def __init__(self, port, baudrate):
        self.serial_port = serial.Serial(port, baudrate, timeout=1)
        self.data_to_db = loader_to_db.DataQueueToDB()
        self.data_to_db.start()

    def read_serial(self, cmd_handler=None):
        ac_ctl_prefix = "[ac_ctl]"

        while True:
            data = self.serial_port.readline().decode('utf-8').strip()
            if DEBUG_MODE:
                print(data)

            if data.startswith(ac_ctl_prefix):
                data = data.lstrip(ac_ctl_prefix)

                try:
                    data = json.loads(data)
                    if cmd_handler and data.get("RECV", None):
                        print(data)
                        cmd_handler.recv_from_device(data.get("RECV"))

                    elif cmd_handler and data.get("HB", None):
                        cmd_handler.im_online(data.get("HB"))

                    elif type(data.get("value")) is list:
                        print(data)
                        self.data_to_db.put_report_data(data)

                    elif type(data.get("value")) is int:
                        self.data_to_db.put_response_data(data)

                    elif "temperature" in data:
                        self.data_to_db.put_dht_data(data)

                    else:
                        print(f"Not match {data}")
                except Exception as e:
                    print(f"EXCEPTION {e}")

    def write_serial(self):
        while True:
            message = {}
            while 1:
                category = input("單一位址(1) / 群組發送(2) / 全體發送(3)：")
                if category == "1":
                    message["dest"] = input("請輸入傳送位址：")
                elif category == "2":
                    message["group"] = input("請輸入群組名稱：")
                elif category == "3":
                    message["group"] = "all"
                else:
                    print("請輸入正確的指令")
                    continue
                break

            while 1:
                idx = input('輸入指令index：')

                if len(idx) == 0:
                    try:
                        temp = []
                        for i in range(8):
                            temp.append(int(input("0x"), 16))

                        message["manual"] = temp
                        break
                    except:
                        print("manual failed")

                if idx.isdigit() is False or not (0 <= int(idx) <= 19):
                    print("index not found")
                    continue

                message["cmd"] = int(idx)
                break

            message = str(message).replace("'", '"')
            self.serial_port.write(message.encode('utf-8'))
            print(f'Sent: {message}')

    def dispatch_command(self, command):
        message = str(command).replace("'", '"')
        self.serial_port.write(message.encode('utf-8'))
        print(f'Sent: {message}')

    def close(self):
        self.serial_port.close()


if __name__ == "__main__":
    port_name = "/dev/ttyUSB0"
    baud_rate = 115200
    print("1- 開機 2- 關機 11- 寫入設定溫度20度 12- 寫入設定溫度26度")
    serial_communication = SerialCommunication(port_name, baud_rate)

    read_thread = threading.Thread(
        target=serial_communication.read_serial, daemon=True)
    write_thread = threading.Thread(
        target=serial_communication.write_serial, daemon=True)

    read_thread.start()
    write_thread.start()

    try:
        read_thread.join()
        write_thread.join()

    except KeyboardInterrupt:
        pass
    finally:
        serial_communication.serial_port.close()
