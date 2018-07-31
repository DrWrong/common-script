#!/usr/bin/env python3
from time import time
from urllib.parse import urlparse
from base64 import standard_b64encode
from hashlib import md5, sha1
import requests
import json
import logging

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)


def version_greater_or_equal(v1, v2):
    v1_array = v1.split('.')
    v2_array = v2.split('.')
    for n1, n2 in zip(v1_array, v2_array):
        if n1 != n2:
            return int(n1) > int(n2)
    return len(v1_array) >= len(v2_array)


def is_version_in_range(app_version, version_range):
    min_version, max_version = version_range
    return version_greater_or_equal(app_version, min_version) and version_greater_or_equal(max_version, app_version)



class PutongAuth(requests.auth.AuthBase):
    def __init__(self, secrect_version, secrect, mac_version=7):
        self.secrect_version = secrect_version
        self.secrect = secrect
        self.mac_version=7

    def get_uri_path(self, r):
        o = urlparse(r.url)
        path = o.path
        if not path.startswith('/v1'):
            path = '/v1' + path
        return path

    def mac_info_v7(self, r):
        '''
        Mac authorization v7 E.G.
        Authorization: MAC ["7","android2.8.9","1519545892002","9742feb4c2ae6e818286de1b3f33cdc839b7a9d7cba9011853a2856c8e33b358","uA7yZcjUo7DeYszeO9jMXVoYa64=","2fgHAfuhg2n3Gcv9ORt4DVMFOUQ="]
        '''

        mac_info = [
            "7",  #version
            self.secrect_version, #secrect version
            "%d" % int(time() * 1000), #timestamp
            "0efbb5ca81f7e9c5d7a0ee0342cdb7a2f5f7e6c0d74a3452c0f0815b9716434f", #access token
            "CalYNA7ehDSr32z1nTr+4kIhoog=",
        ]


        message = (
            mac_info[2],
            mac_info[3],
            mac_info[4],
            self.get_uri_path(r),
            r.body
        )

        m = md5()
        m.update(self.secrect.encode('utf-8'))

        for item in message:
            if item is not None:
                if not isinstance(item, bytes):
                    item = item.encode('utf-8')
                m.update(item)

        md5_digest = m.digest()
        s = sha1()
        s.update(self.secrect[::-1].encode('utf-8'))
        s.update(md5_digest)

        mac_info.append(standard_b64encode(s.digest()).decode('utf-8'))

        return mac_info



    def __call__(self, r):

        info_generator = getattr(self, "mac_info_v%d" % self.mac_version)
        mac_info = info_generator(r)
        print('mac_info is', mac_info)
        r.headers['Authorization'] = "MAC %s" % (json.dumps(mac_info))
        return r

# class PutongAdapter(requests.adapters.HTTPAdapter):
#     def __init__(self, base_url, *args, **kwargs):
#         super().__init__(self, *args, **kwargs)
#         self.base_url = base_url


#     def request_url(self, request, proxies):
#         request.url = "%s%s" % (self.base_url, request.url)
#         return super().request_url(self, request, proxies)

class PutongSession(requests.Session):
    def __init__(self, base_url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = base_url


    def request(self, method, url, *args, **kwargs):
        return super().request(method, self.base_url+url, *args, **kwargs)


# X-Authorization-Type
class TantanMockClient(object):
    def __init__(self, app_version, client_os, base_url, proxies=None):
        self.app_version = app_version
        self.client_os = client_os
        s = PutongSession(base_url)
        s.headers['User-Agent'] = self.generate_user_agent()
        s.proxies = proxies
        version, secrect = self.get_secret_and_version()
        s.auth = PutongAuth(version, secrect)
        self.session = s

    def generate_user_agent(self):
        return "TantanMock/%s %s" % (self.app_version, self.client_os)


    def __load_hmac_secrects(self):
        with open('putong-core-service.json.2') as f:
            config = json.load(f)
            self._hmac_secrects = config['MacAccessToken']['HMacSecretsV2']


    def get_secret_and_version(self):
        if not hasattr(self, '_hmac_secrects'):
            self.__load_hmac_secrects()

        for key, value in self._hmac_secrects[self.client_os].items():
            if is_version_in_range(self.app_version, value['AppVersionRange']):
                return (key, value['Secret'])
        raise Exception("Not Found")

    def bind_user(self, uid):
        self.session.headers['X-Putong-User-Id'] = "%s" % uid
        return self

    def __getattr__(self, key):
        return getattr(self.__getattribute__('session'), key) #

def online_mock_client():
    return TantanMockClient(
        '3.0.0',
        'Android',
        # 'http://10.9.113.159:18223', #ABTEST
        'http://10.189.8.38:21268', #Gateway
        proxies={
            'http': 'socks5://127.0.0.1:8122'
        }
    )


if __name__ == '__main__':
    c = TantanMockClient(
        '2.8.9',
        'Android',
        'http://core.viptesting.p1staff.com/v1',
    )

    c.bind_user(531)
    response = c.get("/users?search=suggested,scenario-suggested")
    print(response.status_code)
    print(response.text)
    # for uid in range(808, 808+250):
    #     c.bind_user(uid)
    #     c.put('/users/me/relationships/1202', json={
    #         "state": "liked"
    #     })




    # set user 1 to boost
    # c.bind_user(1)
    # r = c.patch('/users/me', json={
    #     "id": "1",
    #     "settings": {
    #         "boost": {
    #             "active": True,
    #         },
    #     }
    # })
    # print(r.text)

    # user 2 like user 1
    # c.bind_user(2)
    # c.put('/users/me/relationships/1', json={
    #     "state": "liked"
    # })

    # user 1 looked person liked me
    # c.bind_user(1)
    # r = c.get('/users/me/relationships?filter=receviedLikes&with=users')
    # print(r.text)


    # # c.put('/users/me/relationships/3', json={
    # #     "state": "liked",
    # # })
    # r = c.get('/users/me/relationships?filter=receviedLikes&with=users')
    # print(r.text)
    # # r = c.get('/users/me')
    # # print('text')
    # # print(r.text)
