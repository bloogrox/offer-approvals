from nameko.events import event_handler


class EmailerService:
    name = "emailer_service"

    @event_handler("syncer_changes_detector_service", "approval.created")
    def send(self, payload):
        # @todo send email via sendgrid
        print(f"EmailerService.send: sent email {payload}")
