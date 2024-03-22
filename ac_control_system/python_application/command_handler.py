import heapq
import logging
import asyncio
import datetime

EXPIRE_HOUR = 3
MAX_RETRY = 5


class CmdHandler:
    def __init__(self, meshroot):
        self.status = {}  # {device: 5}
        self.online = []
        self.meshroot = meshroot

    async def retry_send_cmd(self, cmd_index):
        # {"dest":loc, "cmd":cmd}
        traverse = list(self.status.keys())
        for dev in traverse:
            if dev not in self.status.keys(): continue
            if dev == "M3SR01" or dev == "D3PR01":
                self.recv_from_device(dev)
                continue

            print(f"{dev} retry...")

            if self.status[dev] > 0:
                msg = {"dest": dev, "cmd": cmd_index}
                self.meshroot.dispatch_command(msg)
                self.status[dev] -= 1
            else:
                print(f"{dev} timeout.")
                self.status.pop(dev, None)

            await asyncio.sleep(1)

    def recv_from_device(self, device):
        self.status.pop(device, None)

    async def monitor_all_send(self, cmd):
        self.check_online()
        start_time = datetime.datetime.now().strftime("%H:%M:%S")

        for _, device in self.online:
            self.status[device] = MAX_RETRY
        await asyncio.sleep(5)

        for i in range(5):
            if len(self.status) == 0: break
            print(f"============= Retry : {i+1} =============")
            await self.retry_send_cmd(cmd)
            await asyncio.sleep(10)

        logging.info(f"[FINISH] {cmd} at {start_time}")

    def check_online(self):
        while self.online and (datetime.datetime.now()-datetime.timedelta(hours=EXPIRE_HOUR) > self.online[0][0]):
            heapq.heappop(self.online)

    def im_online(self, device):
        heapq.heappush(self.online, (datetime.datetime.now(), device))
        self.check_online()

    def list_online(self):
        ret = {}
        for data in self.online:
            ret[data[1]] = max(data[0], ret.get(data[1], datetime.datetime.fromtimestamp(0)))
        
        return dict(sorted(ret.items()))
