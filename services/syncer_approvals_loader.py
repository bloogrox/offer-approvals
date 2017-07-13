from nameko.rpc import rpc, RpcProxy


def get_approvals(limit, page_number):
    # @todo perform a call to a hasoffers and take
    #  an amount of `approved` approvals
    return [
        {
            "id": 1,
            "approval_status": "approved",
            "affiliate_id": 1,
            "offer_id": 1
        }
    ]


class SyncerApprovalsLoaderService:
    name = "syncer_approvals_loader_service"

    syncer_changes_detector_service = (
        RpcProxy("syncer_changes_detector_service"))

    @rpc
    def load_page(self, page_number):
        approvals = get_approvals(10000, page_number)
        for approval in approvals:
            (self.syncer_changes_detector_service.detect_changes
             .call_async(approval))
        print(f"SyncerApprovalsLoaderService.load_page: "
              "processed page {page_number}")
