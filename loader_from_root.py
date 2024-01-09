import json
import serial
import threading
import loader_to_db

DEBUG_MODE = False


class SerialCommunication:
    def __init__(self, port, baudrate):
        self.serial_port = serial.Serial(port, baudrate, timeout=1)

    def read_serial(self):
        ac_ctl_prefix = "[ac_ctl]"

        while True:
            data = self.serial_port.readline().decode('utf-8').strip()
            if DEBUG_MODE:
                print(data)

            if data.startswith(ac_ctl_prefix):
                data = data.lstrip(ac_ctl_prefix)

                try:
                    data = json.loads(data)
                    if type(data.get("value")) is list:
                        data_to_db.put_report_data(data)

                    elif type(data.get("value")) is int:
                        data_to_db.put_response_data(data)

                except:
                    pass

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


if __name__ == "__main__":
    port_name = "/dev/ttyUSB0"
    baud_rate = 115200
    print("1- 開機 2- 關機 11- 寫入設定溫度20度 12- 寫入設定溫度26度")
    serial_communication = SerialCommunication(port_name, baud_rate)
    data_to_db = loader_to_db.DataQueueToDB()

    read_thread = threading.Thread(
        target=serial_communication.read_serial, daemon=True)
    write_thread = threading.Thread(
        target=serial_communication.write_serial, daemon=True)

    read_thread.start()
    write_thread.start()
    data_to_db.start()

    try:
        data_to_db.join()
        read_thread.join()
        write_thread.join()

    except KeyboardInterrupt:
        pass
    finally:
        serial_communication.serial_port.close()
