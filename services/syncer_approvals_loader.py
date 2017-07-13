import hasoffers
from nameko.rpc import rpc, RpcProxy

import settings


def get_approvals(limit, page_number):
    client = hasoffers.Hasoffers(settings.HASSOFFERS_NETWORK_TOKEN,
                                 settings.HASSOFFERS_NETWORK_ID,
                                 proxies=settings.PROXIES)
    resp = client.Offer.findAllAffiliateApprovals(
        filters={
            "id": {"GREATER_THAN_OR_EQUAL_TO": settings.MIN_APPROVAL_ID},
            "approval_status": "approved"
        },
        sort={"id": "asc"},
        limit=limit,
        page=page_number)

    return list(map(lambda x: x[1], resp.data["data"].items()))


class SyncerApprovalsLoaderService:
    name = "syncer_approvals_loader_service"

    syncer_changes_detector_service = (
        RpcProxy("syncer_changes_detector_service"))

    @rpc
    def load_page(self, page_number):
        approvals = get_approvals(10000, page_number)
        for approval in approvals:
            affiliate_offer = approval["AffiliateOffer"]
            (self.syncer_changes_detector_service.detect_changes
             .call_async(affiliate_offer))
        print(f"SyncerApprovalsLoaderService.load_page: "
              "processed page {page_number}")
