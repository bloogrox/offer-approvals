import mock
from services.syncer import SyncerService

from nameko.testing.services import worker_factory


@mock.patch("settings.PAGE_SIZE", 10000)
@mock.patch("services.syncer.get_approvals_count",
            return_value=10000)
def tests_get_count_and_call_approvals_loader_service(*args):
    service = worker_factory(SyncerService)

    service.run()

    assert (service.syncer_approvals_loader_service
            .load_page.call_async.call_count) == 1
