from nameko.rpc import rpc

from app import mongo_database


class ApprovalPersistorService:
    name = "approval_persistor_service"

    @rpc
    def persist(self, approval):
        try:
            (mongo_database.approvals
             .replace_one({"_id": approval["id"]}, approval, upsert=True))
        except Exception as e:
            print("ApprovalPersistorService.persist: "
                  f"exception - {e}")
