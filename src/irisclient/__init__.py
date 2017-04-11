from __future__ import absolute_import

import base64
import hashlib
import hmac
import time

import requests

from .exceptions import InvalidArgument


__version__ = "0.0.1"


class IrisAuth(requests.auth.AuthBase):
    def __init__(self, app, key):
        self.header = 'hmac %s:' % app
        self.HMAC = hmac.new(key, '', hashlib.sha512)

    def __call__(self, request):
        HMAC = self.HMAC.copy()
        path = request.path_url
        method = request.method
        body = request.body or ''
        window = int(time.time()) // 5
        HMAC.update('%s %s %s %s' % (window, method, path, body))
        digest = base64.urlsafe_b64encode(HMAC.digest())
        request.headers['Authorization'] = self.header + digest
        return request


class IrisClient(requests.Session):
    def __init__(self, app, key, api_host, version=0):
        super(IrisClient, self).__init__()
        self.auth = IrisAuth(app, key)
        self.url = api_host + '/v%d/' % version

    def incident(self, plan, context):
        r = self.post(self.url + 'incidents',
                      json={'plan': plan, 'context': context})
        r.raise_for_status()
        try:
            return r.json()
        except:
            raise ValueError('Failed to decode json: %s' % r.text)

    def notification(self, role, target, subject, priority=None, mode=None, body=None, template=None, context=None):
        data = {
            'role': role,
            'target': target,
            'subject': subject,
        }
        if mode:
            data['mode'] = mode
        else:
            if not priority:
                raise InvalidArgument('Missing both priority and mode arguments, need to at least specify one.')
            data['priority'] = priority
        if template and context:
            data['template'] = template
            data['context'] = context
            data['context']['iris'] = {}
            data['body'] = None
        elif body:
            data['body'] = body
        r = self.post(self.url + 'notifications', json=data)
        if r.status_code == 200:
            return True
        else:
            raise ValueError('Error response from server, %s: %s' % (r.status_code, r.content))
