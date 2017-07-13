from nameko.rpc import rpc, RpcProxy
from nameko.events import EventDispatcher


def get_approval_by_id(id_):
    # @todo find one approval in mongodb
    return {"id": 1, "approval_status": "approved"}


class SyncerChangesDetectorService:
    name = "syncer_changes_detector_service"

    approval_persistor_service = RpcProxy("approval_persistor_service")

    dispatch = EventDispatcher()

    @rpc
    def detect_changes(self, approval):
        db_approval = get_approval_by_id(approval["id"])

        if not db_approval:
            is_approved = True
        elif db_approval["approval_status"] != "approved":
            is_approved = True
        else:
            is_approved = False

        if is_approved:
            self.dispatch("approval.approved", approval)
            print("SyncerChangesDetectorService.detect_changes: "
                  f"approval approve detected {approval}")
