from nameko.rpc import rpc
from nameko.events import event_handler

from app import mongo_database
from services.syncer_changes_detector import APPROVED_EVENT


class ApprovalPersistorService:
    name = "approval_persistor_service"

    @event_handler("syncer_changes_detector_service", APPROVED_EVENT)
    def persist(self, approval):
        try:
            (mongo_database.approvals
             .replace_one({"_id": approval["id"]}, approval, upsert=True))
        except Exception as e:
            print("ApprovalPersistorService.persist: "
                  f"exception - {e}")
