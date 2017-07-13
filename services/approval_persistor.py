from nameko.rpc import rpc


class ApprovalPersistorService:
    name = "approval_persistor_service"

    @rpc
    def persist(self):
        # create or replace object with a new one
        pass
