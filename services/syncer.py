import math

from nameko.rpc import rpc, RpcProxy


def get_approvals_count():
    return 15000


class SyncerService:
    name = "syncer_service"

    syncer_approvals_loader_service = (
        RpcProxy("syncer_approvals_loader_service"))

    @rpc
    def run(self):
        # @todo request to HO
        #  get total count of approved objects
        count = get_approvals_count()
        print(f"SyncerService.run: total approvals count {count}")
        # send rpc call to process each page
        for page in range(math.ceil(count / 10000)):
            self.syncer_approvals_loader_service.load_page.call_async(page)
