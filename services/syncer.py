import math
import hasoffers

from nameko.rpc import rpc, RpcProxy

import settings


def get_approvals_count():
    client = hasoffers.Hasoffers(settings.HASSOFFERS_NETWORK_TOKEN,
                                 settings.HASSOFFERS_NETWORK_ID)

    resp = client.Offer.findAllAffiliateApprovals(
        filters={
            "id": {"GREATER_THAN_OR_EQUAL_TO": settings.MIN_APPROVAL_ID},
            "approval_status": "approved"
        },
        limit=1)
    return resp.data["count"]


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
