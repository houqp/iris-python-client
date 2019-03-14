from __future__ import absolute_import

from .compat import str, bytes

import base64
import hashlib
import hmac
import time

import requests

from .exceptions import InvalidArgument


__version__ = "1.3.0"


class IrisAuth(requests.auth.AuthBase):
    def __init__(self, app, key):
        if not isinstance(app, bytes):
            app = app.encode('utf-8')
        self.header = b'hmac ' + app + b':'
        if not isinstance(key, bytes):
            key = key.encode('utf-8')
        self.HMAC = hmac.new(key, b'', hashlib.sha512)

    def __call__(self, request):
        HMAC = self.HMAC.copy()

        path = request.path_url.encode('utf8')
        method = request.method.encode('utf8')
        body = request.body or b''
        window = str(int(time.time()) // 5).encode('utf8')
        HMAC.update(b'%s %s %s %s' % (window, method, path, body))

        digest = base64.urlsafe_b64encode(HMAC.digest())
        request.headers['Authorization'] = self.header + digest
        return request


class IrisClient(requests.Session):
    def __init__(self, app, key, api_host, version=0):
        super(IrisClient, self).__init__()
        self.app = app
        self.auth = IrisAuth(app, key)
        self.url = api_host + '/v%d/' % version

    def incident(self, plan, context, dynamic_targets=None):
        incident_json={'plan': plan, 'context': context}
        if dynamic_targets:
            incident_json['dynamic_targets'] = dynamic_targets
        r = self.post(self.url + 'incidents', json=incident_json)
        if r.status_code == 401:
            err_desc = r.json()['description']
            if err_desc.startswith('Application not found'):
                apps = self.get(self.url + 'applications').json()
                raise ValueError(
                    '"%s" not in list of available applications: %s' % (
                        self.app, ', '.join([app['name'] for app in apps])))
        r.raise_for_status()
        try:
            return r.json()
        except:
            raise ValueError('Failed to decode json: %s' % r.text)

    def notification(self, role, target, subject,
                     priority=None, mode=None, body=None, template=None,
                     context=None, email_html=None):
        data = {
            'role': role,
            'target': target,
            'subject': subject,
        }
        if mode:
            data['mode'] = mode
        else:
            if not priority:
                raise InvalidArgument(
                    ('Missing both priority and mode arguments, '
                     'need to at least specify one.'))
            data['priority'] = priority
        if email_html:
            data['email_html'] = email_html
        else:
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
            raise ValueError(
                'Error response from server, %s: %s' % (
                    r.status_code, r.content))
