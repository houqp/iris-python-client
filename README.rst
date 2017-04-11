.. image:: https://travis-ci.org/houqp/iris-python-client.svg?branch=master
    :target: https://travis-ci.org/houqp/iris-python-client

Python client for Iris API
==========================

Usage
-----

.. code-block:: python

    from irisclient import IrisClient

    client = IrisClient(
        app='SERVICE_FOO',
        key='IRIS_API_KEY',
        api_host='http://localhost:5000'
    )
    # create an incident
    print client.incident('plan-foo', context={'key-foo': 'abc', 'key-bar': 1})
    # send an adhoc notification
    print client.notification(role='user', target='alice', priority='urgent', subject='Yo')


Test
----

.. code-block:: bash

    pip install tox
    tox
