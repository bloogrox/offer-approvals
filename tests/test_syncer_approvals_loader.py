import mock
from services.syncer_approvals_loader import SyncerApprovalsLoaderService

from nameko.testing.services import worker_factory


APPROVAL_FXT = {
    "AffiliateOffer": {
        "id": 1,
        "offer_id": 1,
        "affiliate_id": 1,
        "approval_status": "pending"
    },
    "Offer": {},
    "Affiliate": {}
}
APPROVALS_FXT = [APPROVAL_FXT]


@mock.patch("services.syncer_approvals_loader.get_approvals",
            return_value=APPROVALS_FXT)
def test_get_approvals_and_call_changes_detector(*args):
    service = worker_factory(SyncerApprovalsLoaderService)

    service.load_page(page_number=1)

    (service.syncer_changes_detector_service.detect_changes.
     call_async.called_once_with(APPROVAL_FXT["AffiliateOffer"]))
