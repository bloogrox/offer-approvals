import sendgrid
from sendgrid.helpers.mail import Email, Mail, Content, Personalization
from hasoffers import Hasoffers

from nameko.events import event_handler

from services.syncer_changes_detector import APPROVED_EVENT
import settings


class EmailerService:
    name = "emailer_service"

    @event_handler("syncer_changes_detector_service", APPROVED_EVENT)
    def send(self, payload):
        api = Hasoffers(network_token=settings.HASOFFERS_NETWORK_TOKEN,
                        network_id=settings.HASOFFERS_NETWORK_ID,
                        proxies=settings.PROXIES)

        affiliate_id = payload["AffiliateOffer"]["affiliate_id"]
        offer_id = payload["AffiliateOffer"]["offer_id"]
        offer_name = payload["Offer"]["name"]
        payout = payload["Offer"]["default_payout"]
        offer_description = payload["Offer"]["description"]
        offer_cap = payload["Offer"]["conversion_cap"]

        # get Affiliate Emails
        affiliate_users = (api.AffiliateUser
                           .findAll(fields=["email"],
                                    filters={"affiliate_id": affiliate_id})
                           .extract_all())
        emails = [affiliate_user.email for affiliate_user in affiliate_users]

        # get Tracking Link
        params = dict(offer_id=offer_id, affiliate_id=affiliate_id)
        resp = api.Offer.generateTrackingLink(**params)
        tracking_link = resp.data["click_url"]

        # get Thumbnail
        resp = api.Offer.findById(id=offer_id, contain=["Thumbnail"])
        thumbnail = (resp.data["Thumbnail"]["thumbnail"]
                     if resp.data.get("Thumbnail")
                     else None)

        # Send Email
        html = f"""
            <div>
                <img src="{thumbnail}">
            </div>
            <p>#{offer_id}: {offer_name}</p>
            <p>Payout: {payout}</p>
            <p>Offer Cap: {offer_cap}</p>
            <p>Tracking link: {tracking_link}</p>
            <p>Description: {offer_description}</p>
        """

        mail = Mail()

        mail.from_email = Email("info@performancerevenues.com")
        mail.subject = ("You are approved for the offer "
                        f"#{offer_id}: {offer_name}")
        personalization = Personalization()
        for email in emails:
            personalization.add_to(Email(email))
        mail.add_content(Content("text/html", html))

        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
        res = sg.client.mail.send.post(request_body=mail.get())

        print(f"EmailerService.send: sent email payload {payload} "
              f"result {res}")
