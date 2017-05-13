#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pytest
from httmock import all_requests, HTTMock
from irisclient import IrisClient


path_to_resp = {
    '/v0/incidents': {
        'status_code': 200,
        'content': '123'
    },
    '/v0/notifications': {
        'status_code': 200,
    }
}


@all_requests
def mock_response(url, request):
    return path_to_resp[url.path]


@pytest.fixture
def iris_client():
    return IrisClient(
        app='SERVICE_FOO',
        key='IRIS_API_KEY',
        api_host='http://iris.foo.bar'
    )


def test_incident(iris_client):
    with HTTMock(mock_response):
        re = iris_client.incident('plan-foo', context={'foo': 123})
    assert re == 123


def test_invalid_argument(iris_client):
    from irisclient.exceptions import InvalidArgument
    with pytest.raises(InvalidArgument):
        with HTTMock(mock_response):
            iris_client.notification(role='user', target='foo', subject='test')


def test_encoding_in_hmac(mocker):
    mocker.patch('irisclient.time').time.return_value = 1000

    IrisClient(
        app='SERVICE_FOO',
        key='IRIS_API_KEY',
        api_host='http://iris.foo.bar'
    )

    client = IrisClient(
        app=b'SERVICE_FOO',
        key=b'IRIS_API_KEY',
        api_host='http://iris.foo.bar'
    )

    @all_requests
    def check_auth_header(url, request):
        header_bytes = bytes(request.headers['Authorization'])
        assert header_bytes.startswith('hmac SERVICE_FOO:'.encode('utf-8'))
        return {'status_code': 200}

    with HTTMock(check_auth_header):
        client.notification(
            role='user', target='foo', priority='high', subject='test')
