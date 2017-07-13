import os


AMQP_URI = os.environ["CLOUDAMQP_URL"]
MONGO_URI = os.environ["MONGODB_URI"]
HASSOFFERS_NETWORK_TOKEN = os.environ["HASSOFFERS_NETWORK_TOKEN"]
HASSOFFERS_NETWORK_ID = os.environ["HASSOFFERS_NETWORK_ID"]
MIN_APPROVAL_ID = os.environ["MIN_APPROVAL_ID"]
PAGE_SIZE = 10000
PROXIES = {
    'http': os.environ['PROXIMO_URL'],
    'https': os.environ['PROXIMO_URL']
}
