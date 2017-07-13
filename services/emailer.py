from nameko.events import event_handler

from services.syncer_changes_detector import APPROVED_EVENT


class EmailerService:
    name = "emailer_service"

    @event_handler("syncer_changes_detector_service", APPROVED_EVENT)
    def send(self, payload):
        print(f"EmailerService.send: sent email {payload}")
