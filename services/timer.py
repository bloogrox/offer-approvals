from nameko.rpc import RpcProxy
from nameko.timer import timer


class TimerService:
    name = "timer_service"

    syncer_service = RpcProxy("syncer_service")

    @timer(interval=3)
    def run_syncer(self):
        self.syncer_service.run.call_async()
        print("tick")
