import math
import hasoffers

from nameko.rpc import rpc, RpcProxy

import settings


def get_approvals_count():
    client = hasoffers.Hasoffers(settings.HASOFFERS_NETWORK_TOKEN,
                                 settings.HASOFFERS_NETWORK_ID,
                                 proxies=settings.PROXIES)

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
        count = get_approvals_count()
        print(f"SyncerService.run: total approvals count {count}")
        for page in range(1, math.ceil(count / settings.PAGE_SIZE) + 1):
            self.syncer_approvals_loader_service.load_page.call_async(page)
