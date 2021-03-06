from typing import List
import sendgrid
from sendgrid.helpers.mail import Email, Mail, Content, Personalization
from hasoffers import Hasoffers
from hasoffers import Error
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
            if int(affiliate_id) in settings.UNSUBSCRIBED_AFFILIATES:
                print(f"Affiliate #{affiliate_id} is in blacklist, so return")
                return

            offer = get_offer(offer_id, api)

            tr_link = get_tracking_link(offer_id, affiliate_id, api)

            payout = find_payout(affiliate_id, offer, api)

            # Conversion Cap and Daily Revenue
            caps = get_offer_convesion_caps(affiliate_id, api)
            caps_for_offer = list(filter(cmp_offer_id(offer_id), caps))

            try:
                conversion_cap = int(caps_for_offer[0]["conversion_cap"])
                revenue_cap = float(caps_for_offer[0]["revenue_cap"])
            except IndexError:
                conversion_cap = 0
                revenue_cap = 0.0

            payout_value = f"${payout}"

            if conversion_cap:
                cap_value = f"{conversion_cap} conversions"
            elif revenue_cap:
                cap_value = f"${revenue_cap}"
            else:
                cap_value = "Ask your account manager"

            data = {
                "thumbnail": (offer.Thumbnail["thumbnail"]
                              if offer.Thumbnail
                              else None),
                "offer_id": offer.id,
                "offer_name": offer.name,
                "payout_value": payout_value,
                "cap_value": cap_value,
                "preview_url": offer.preview_url,
                "tracking_link": tr_link,
                "offer_description": offer.description,
                "network_domain": settings.NETWORK_DOMAIN
            }

            affiliate = get_affiliate_by_id(affiliate_id, api)
            employee = get_employee_by_id(affiliate.account_manager_id, api)

            emails = get_affiliate_emails(affiliate_id, api)
            emails.append(employee.email)

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


def find_payout(affiliate_id, offer, api):
    # custom payout
    payouts = get_offer_payouts(affiliate_id, api)
    # offer payout
    payouts_for_offer = list(filter(cmp_offer_id(offer.id), payouts))
    # goal payout
    goals = get_offer_goals(offer.id, api)
    non_zero_goals = list(
        filter(
            lambda goal: bool(float(goal.default_payout)),
            goals))
    # choose payout
    if payouts_for_offer and float(payouts_for_offer[0]["payout"]):
        payout = float(payouts_for_offer[0]["payout"])
    elif float(offer.default_payout):
        payout = float(offer.default_payout)
    elif non_zero_goals:
        payout = float(non_zero_goals[0].default_payout)
    else:
        payout = 0.0
    return payout


def cmp_offer_id(offer_id: int):
    def f(d: dict) -> bool:
        return d["offer_id"] == offer_id
    return f


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
                  filters={"affiliate_id": affiliate_id, "status": "active"})
    affiliate_users = (client.AffiliateUser
                       .findAll(**params)
                       .extract_all())
    emails = [affiliate_user.email
              for affiliate_user in affiliate_users]
    return emails


def get_affiliate_by_id(affiliate_id: int, client: Hasoffers) -> Model:
    """
    @returns Affiliate object
    """
    try:
        return client.Affiliate.findById(id=affiliate_id).extract_one()
    except Error as e:
        print(f"get_affiliate_by_id: exception {e}")


def get_employee_by_id(employee_id: int, client: Hasoffers) -> Model:
    """
    @returns Employee object
    """
    try:
        return client.Employee.findById(id=employee_id).extract_one()
    except Error as e:
        print(f"get_employee_by_id: exception {e}")


def get_offer_payouts(affiliate_id: int, client: Hasoffers) -> list:
    """
    @returns
        [
            {
                "id": ...,
                "affiliate_id": ...,
                "offer_id": ...,
                "payout": ...
            },
            {
                "id": ...,
                "affiliate_id": ...,
                "offer_id": ...,
                "payout": ...
            }
        ]
    """
    try:
        resp = client.Affiliate.getOfferPayouts(id=affiliate_id)
        if resp.data:
            # if result is not empty, then it is in dict
            return [scope["OfferPayout"]
                    for _, scope in resp.data.items()]
        else:
            # when no data, there is empty list
            return []
    except Error as e:
        print(f"get_offer_payouts: exception {e}")


def get_offer_convesion_caps(affiliate_id: int, client: Hasoffers) -> list:
    """
    @returns
        [
            {
                "id": "1",
                "affiliate_id": "1",
                "offer_id": "1",
                "conversion_cap": "5",
                "revenue_cap": "0.00",
            },
            ...
        ]
    """
    try:
        resp = client.Affiliate.getOfferConversionCaps(id=affiliate_id)
        if resp.data:
            return [scope["OfferConversionCap"]
                    for _, scope in resp.data.items()]
        else:
            return []
    except Error as e:
        print(f"get_offer_convesion_caps: exception {e}")


def get_offer_goals(offer_id: int, client: Hasoffers) -> List[Model]:
    """
    @returns
        [
            {
                "id": "1",
                "offer_id": "1",
                "default_payout": "1.00"
            },
            ...
        ]
    """
    filters = dict(offer_id=offer_id)
    fields = ["id", "offer_id", "default_payout"]
    return (client
            .Goal
            .findAll(filters=filters, fields=fields)
            .extract_all())


def create_content(data: dict) -> str:
    download_link = (f"http://{data['network_domain']}"
                     f"/offer_files/download_all/{data['offer_id']}")
    html = f"""
        <div>
            <a href="{data['preview_url']}" target="_blank">
                <img src="{data['thumbnail']}">
            </a>
        </div>
        <p>#{data['offer_id']}: {data['offer_name']}</p>
        <p>Payout: {data['payout_value']}</p>
        <p>Offer Cap: {data['cap_value']}</p>
        <p>Preview:
            <a href="{data['preview_url']}" target="_blank">
                {data['preview_url']}
            </a>
        </p>
        <p>Tracking link: {data['tracking_link']}</p>
        <p>
            <a href="{download_link}" target="_blank">
               Download creatives
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
