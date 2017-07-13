import sys
import time
import logging
import requests
from collections import OrderedDict

from .mapper import Mapper
from .http_build_query import http_build_query


logger = logging.getLogger('hasoffers')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stderr))


class Error(Exception):
    pass
class APIUsageExceededRateLimit(Error):
    pass


class Hasoffers(object):

    BASE_URL = 'https://api.hasoffers.com/Apiv3/json'

    """
    Usage:
        client = Api(TOKEN, ID, debug=False, retry_count=1)
        response = client.call(target='Conversion', method='findAll', params={'limit': 10, 'contain': ['Offer']})
        response.extract_all()

    Short usage:
        client = Api(TOKEN, ID, debug=False, retry_count=1)
        client.Conversion.findAll(limit=10, contain=['Offer']).extract_all()

    More examples:
        offer = client.Offer.findById(id=1, contain=['Advertiser']).extract_one()

        print(offer.name)

        if offer.Advertiser:
            print(offer.Advertiser['id'])
    """

    class MethodProxy(object):

        def __init__(self, master):
            self.master = master
            self.target = None
            self.method = None

        def __call__(self, **kwargs):
            return self.master.call(target=self.target, method=self.method, params=kwargs)

        def __getattr__(self, method):
            self.method = method
            return self

    def __init__(self, network_token, network_id, debug=False, retry_count=1, api_type='brand', proxies=None):
        self.network_token = network_token
        self.network_id = network_id

        if debug:
            self.level = logging.INFO
        else:
            self.level = logging.DEBUG

        self.config = {}

        if api_type == 'brand':
            self.config = dict(
                NETWORK_TOKEN_PARAMETER_NAME='NetworkToken',
                TARGET_PREFIX=''
            )
        elif api_type == 'affiliate':
            self.config = dict(
                NETWORK_TOKEN_PARAMETER_NAME='api_key',
                TARGET_PREFIX='Affiliate_'
            )

        self.retry_count = retry_count

        self.proxies = proxies

        self.method_proxy = self.MethodProxy(self)

    def call(self, target, method, params=None):
        # request = self.create_request(target, method, params)
        _params = {
            'NetworkId': self.network_id,
            self.config['NETWORK_TOKEN_PARAMETER_NAME']: self.network_token,
            'Target': self.config['TARGET_PREFIX'] + target,
            'Method': method
        }
        if params:
            _params.update(params)

        # url = self.build_url(_params)
        url = self.BASE_URL + '?' + http_build_query(_params)

        request = RequestFactory.create(self, target, method, _params, url)

        return self.send_request(request)

    def build_url(self, params):
        return self.BASE_URL + '?' + http_build_query(params)

    # def create_request(self, target, method, params):
    #     _params = {
    #         'NetworkId': self.network_id,
    #         self.config['NETWORK_TOKEN_PARAMETER_NAME']: self.network_token,
    #         'Target': self.config['TARGET_PREFIX'] + target,
    #         'Method': method
    #     }
    #     if params:
    #         _params.update(params)
    #
    #     url = self.build_url(_params)
    #
    #     return Request(self, target, method, _params, url)

    def send_request(self, request):

        request.attempts += 1

        self.log('Executing %s' % request.get_url())
        start = time.time()

        http_response = requests.get(request.get_url(), proxies=self.proxies)

        complete_time = time.time() - start
        self.log('Received %s in %.2fms: %s' % (http_response.status_code, complete_time * 1000, http_response.text))

        json_response = http_response.json(object_pairs_hook=OrderedDict)

        if ('response' not in json_response
                or 'status' not in json_response['response']
                or json_response['response']['status'] != 1):

            # raise self.cast_error(json_response)
            try:
                raise self.cast_error(json_response)
            except APIUsageExceededRateLimit:
                if request.attempts < self.retry_count:
                    self.log('Resending request: attempt %d!' % request.attempts)
                    time.sleep(0.25)
                    return self.send_request(request)
                else:
                    raise self.cast_error(json_response)

        return Response(request, json_response)

    def cast_error(self, response_body):
        if not 'response' in response_body or not 'status' in response_body['response']:
            return Error('Unexpected error: %r' % response_body)
        if 'API usage exceeded rate limit' in response_body['response']['errorMessage']:
            return APIUsageExceededRateLimit(response_body['response']['errorMessage'])
        return Error(response_body['response']['errorMessage'])

    def log(self, *args, **kwargs):
        """Proxy access to the hasoffers logger, changing the level based on the debug setting"""
        logger.log(self.level, *args, **kwargs)

    def __getattr__(self, target):
        self.method_proxy.target = target
        return self.method_proxy


class RequestFactory(object):

    @classmethod
    def create(cls, master, target, method, params, url):
        return Request(master, target, method, params, url)


class Request(object):

    def __init__(self, master, target, method, params, url):
        self.master = master
        self.target = target
        self.method = method
        self.params = params
        self.url = url

        self.attempts = 0

    def get_url(self):
        return self.url


class Response(object):

    def __init__(self, request, json_response):
        self.request = request
        self.json_response = json_response

        self.data = json_response['response']['data']
        self.status = json_response['response']['status']
        self.httpStatus = json_response['response']['httpStatus']
        self.errors = json_response['response']['errors']
        self.errorMessage = json_response['response']['errorMessage']

    def __iter__(self):
        if 'page' not in self.data:
            raise StopIteration
        else:
            return RequestIterator(self.request, self.data['page'], self.data['pageCount'])

    def extract_all(self, model_name=None):
        model_name = model_name or self.request.target

        if 'page' in self.data:
            data = self.data['data']
        else:
            data = self.data

        return Mapper.extract_all(data, model_name)

    def extract_one(self, model_name=None):
        model_name = model_name or self.request.target

        return Mapper.extract_one(self.data, model_name)


class RequestIterator(object):

    def __init__(self, request, page, page_count):
        self.request = request
        self.page = page
        self.page_count = page_count

    def __next__(self):
        if self.page <= self.page_count:
            self.request.params['page'] = self.page
            self.page += 1
            return self.request.master.send_request(self.request)
        else:
            raise StopIteration


