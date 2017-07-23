from typing import List
import sendgrid
from sendgrid.helpers.mail import Email, Mail, Content, Personalization
from hasoffers import Hasoffers
from hasoffers.mapper import Model

from nameko.events import event_handler

from services.syncer_changes_detector import APPROVED_EVENT
import settings


class EmailerService:
    name = "emailer_service"

    @event_handler("syncer_changes_detector_service", APPROVED_EVENT)
    def send(self, payload):
        print(f"EmailerService.send: received {payload} ")
        try:
            api = Hasoffers(network_token=settings.HASOFFERS_NETWORK_TOKEN,
                            network_id=settings.HASOFFERS_NETWORK_ID,
                            proxies=settings.PROXIES)

            affiliate_id = payload["affiliate_id"]
            offer_id = payload["offer_id"]

            # Check Affiliate is not in blacklist
            if affiliate_id in settings.UNSUBSCRIBED_AFFILIATES:
                print(f"Affiliate #{affiliate_id} is in blacklist, so return")
                return

            offer = get_offer(offer_id, api)

            tr_link = get_tracking_link(offer_id, affiliate_id, api)

            data = {
                "thumbnail": (offer.Thumbnail["thumbnail"]
                              if offer.Thumbnail
                              else None),
                "offer_id": offer.id,
                "offer_name": offer.name,
                "payout": offer.default_payout,
                "conversion_cap": offer.conversion_cap,
                "revenue_cap": offer.revenue_cap,
                "preview_url": offer.preview_url,
                "tracking_link": tr_link,
                "offer_description": offer.description
            }

            emails = get_affiliate_emails(affiliate_id, api)

            html = create_content(data)

            config = create_mail_config(
                from_email=settings.COMPANY_EMAIL,
                subject=f"You are approved for the offer #{offer.id}",
                to_emails=emails,
                content=html)

            sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)

            res = send(config, sg)

            print(f"EmailerService.send: sent email payload {payload} "
                  f"result {res}")
        except Exception as e:
            print(f"EmailerService.send: exception {e}")


def get_offer(offer_id: int,
              client: Hasoffers) -> Model:
    return (client.Offer.findById(id=offer_id, contain=["Thumbnail"])
            .extract_one())


def get_tracking_link(offer_id: int,
                      affiliate_id: int,
                      client: Hasoffers) -> str:
    params = dict(offer_id=offer_id, affiliate_id=affiliate_id)
    resp = client.Offer.generateTrackingLink(**params)
    return resp.data["click_url"]


def get_affiliate_emails(affiliate_id: int, client: Hasoffers) -> List[str]:
    params = dict(fields=["email"],
                  filters={"affiliate_id": affiliate_id})
    affiliate_users = (client.AffiliateUser
                       .findAll(**params)
                       .extract_all())
    emails = [affiliate_user.email
              for affiliate_user in affiliate_users]
    return emails


def create_content(data: dict) -> str:
    if data['conversion_cap']:
        cap_value = f"{data['conversion_cap']} conversions"
    elif data['revenue_cap']:
        cap_value = f"{data['revenue_cap']} as revenue"
    else:
        cap_value = "Ask your account manager"

    html = f"""
        <div>
            <a href="{data['preview_url']}" target="_blank">
                <img src="{data['thumbnail']}">
            </a>
        </div>
        <p>#{data['offer_id']}: {data['offer_name']}</p>
        <p>Payout: {data['payout']}</p>
        <p>Offer Cap: {cap_value}</p>
        <p>Preview:
            <a href="{data['preview_url']}" target="_blank">
                {data['preview_url']}
            </a>
        </p>
        <p>Tracking link: {data['tracking_link']}</p>
        <p>
            <a href="http://{settings.NETWORK_DOMAIN}/offer_files/download_all/{data['offer_id']}" target="_blank">download
            </a>
        </p>
        <p>Description: {data['offer_description']}</p>
    """
    return html


def create_mail_config(from_email: str,
                       subject: str,
                       to_emails: List[str],
                       content: str) -> dict:
    mail = Mail()

    mail.from_email = Email(from_email)
    mail.subject = subject
    personalization = Personalization()
    for email in to_emails:
        personalization.add_to(Email(email))
    mail.add_personalization(personalization)
    mail.add_content(Content("text/html", content))

    return mail.get()


def send(config: dict, client: sendgrid.SendGridAPIClient):
    res = client.client.mail.send.post(request_body=config)
    return res
