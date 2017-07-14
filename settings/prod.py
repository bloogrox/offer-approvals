import os


AMQP_URI = os.environ["CLOUDAMQP_URL"]
MONGO_URI = os.environ["MONGODB_URI"]
HASOFFERS_NETWORK_TOKEN = os.environ["HASOFFERS_NETWORK_TOKEN"]
HASOFFERS_NETWORK_ID = os.environ["HASOFFERS_NETWORK_ID"]
MIN_APPROVAL_ID = os.environ["MIN_APPROVAL_ID"]
PAGE_SIZE = 10000
PROXIES = {
    'http': os.environ['PROXIMO_URL'],
    'https': os.environ['PROXIMO_URL']
}
SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]
