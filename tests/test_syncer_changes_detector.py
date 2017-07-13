import mock
from services.syncer_changes_detector import SyncerChangesDetectorService

from nameko.testing.services import worker_factory


@mock.patch("services.syncer_changes_detector.get_approval_by_id",
            return_value=None)
def test_dispatches_event_if_was_none(*args):
    service = worker_factory(SyncerChangesDetectorService)

    approval = {"id": 1, "approval_status": "approved"}
    service.detect_changes(approval)

    service.dispatch.called_once_with(approval)


APPROVAL_PENDING_FXT = {"id": 1, "approval_status": "pending"}


@mock.patch("services.syncer_changes_detector.get_approval_by_id",
            return_value=APPROVAL_PENDING_FXT)
def test_dispatches_event_if_was_pending(*args):
    service = worker_factory(SyncerChangesDetectorService)

    approval = {"id": 1, "approval_status": "approved"}
    service.detect_changes(approval)

    service.dispatch.called_once_with(approval)


APPROVAL_APPROVED_FXT = {"id": 1, "approval_status": "approved"}


@mock.patch("services.syncer_changes_detector.get_approval_by_id",
            return_value=APPROVAL_APPROVED_FXT)
def test_does_not_dispatch_event_as_already_approved(*args):
    service = worker_factory(SyncerChangesDetectorService)

    approval = {"id": 1, "approval_status": "approved"}
    service.detect_changes(approval)

    assert not service.dispatch.called
