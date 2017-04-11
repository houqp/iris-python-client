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
