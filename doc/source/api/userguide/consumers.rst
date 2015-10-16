*************************
Consumers API - User Guide
*************************

This guide will assume you will be using a local running development environment of Barbican.
If you need assistance with getting set up, please reference the :doc:`development guide </setup/dev>`.


What is a Consumer?
###################

A consumer is a way to to register as an interested party for a container. All registered
consumers can be viewed by performing a GET on the container reference /consumers. The idea
being that before a container is deleted all consumers should be notified of the delete.



.. _create_consumer:

How to Create a Consumer
########################

.. code-block:: bash

     curl -X POST -H 'X-Project-Id:12345' -H 'Content-Type: application/json' \
     -d '{"name": "consumername", "URL": "consumerURL"}' \
      http://localhost:9311/v1/containers/74bbd3fd-9ba8-42ee-b87e-2eecf10e47b9/consumers

This should provide a response as follows:

.. code-block:: json
{
    "status": "ACTIVE",
    "updated": "2015-10-15T21:06:33.121113",
    "name": "container name",
    "consumers": [
        {
            "URL": "consumerurl",
            "name": "consumername"
        }
    ],
    "created": "2015-10-15T17:55:44.380002",
    "container_ref":
    "http://localhost:9311/v1/containers/74bbd3fd-9ba8-42ee-b87e-2eecf10e47b9",
    "creator_id": "b17c815d80f946ea8505c34347a2aeba",
    "secret_refs": [
        {
            "secret_ref": "http://localhost:9311/v1/secrets/b61613fc-be53-4696-ac01-c3a789e87973",
            "name": "private_key"
        }
    ],
    "type": "generic"
}


.. _retrieve_consumer:

How to Retrieve a Consumer
##########################

To retrieve a consumer simply perform a GET on the {container_ref}/consumers
This will return all consumers for this container and you can optionally add a
limit and offset query parameter.

.. code-block:: bash

    curl -H 'X-Project-Id:12345' \
    http://192.168.99.100:9311/v1/containers/74bbd3fd-9ba8-42ee-b87e-2eecf10e47b9/consumers

This should provide a response as follows:

.. code-block:: json
{
    "total": 1,
    "consumers": [
        {
            "status": "ACTIVE",
            "URL": "consumerurl",
            "updated": "2015-10-15T21:06:33.123878",
            "name": "consumername",
            "created": "2015-10-15T21:06:33.123872"
        }
    ]
}

This is a list of all consumers for the container provided. All of the listed
consumers will have the meta data listed.

If an offset and limit parameter are added you will also be provided with next
and previous references to cycle through consumers.

.. code-block:: bash

    curl -H 'X-Project-Id:12345' \
    http://192.168.99.100:9311/v1/containers/74bbd3fd-9ba8-42ee-b87e-2eecf10e47b9/consumers?limit=1\&offset=1

This should provide a response as follows:

.. code-block:: json
{
    "total": 3,
    "next": "http://localhost:9311/v1/consumers?limit=1&offset=2",
    "consumers": [
        {
            "status": "ACTIVE",
            "URL": "consumerURL2",
            "updated": "2015-10-15T21:17:08.092416",
            "name": "consumername2",
            "created": "2015-10-15T21:17:08.092408"
        }
    ],
    "previous": "http://localhost:9311/v1/consumers?limit=1&offset=0"
}

.. _delete_consumer:

How to Delete a Consumer
########################

To delete a consumer we will need to know the consumer name and url used
in the initial creation.

.. code-block:: bash

    curl -X DELETE -H 'X-Project-Id:12345' -H 'Content-Type: application/json' \
     -d '{"name": "consumername", "URL": "consumerURL"}' \
      http://localhost:9311/v1/containers/74bbd3fd-9ba8-42ee-b87e-2eecf10e47b9/consumers

The following will be the response

.. code-block:: json
{
    "status": "ACTIVE",
    "updated": "2015-10-15T17:56:18.626724",
    "name": "container name",
    "consumers": [],
    "created": "2015-10-15T17:55:44.380002",
    "container_ref": "http://localhost:9311/v1/containers/74bbd3fd-9ba8-42ee-b87e-2eecf10e47b9",
    "creator_id": "b17c815d80f946ea8505c34347a2aeba",
    "secret_refs": [
        {
            "secret_ref": "http://localhost:9311/v1/secrets/b61613fc-be53-4696-ac01-c3a789e87973",
            "name": "private_key"
        }
    ],
    "type": "generic"
}

When a delete is processed you will recieve a 200 OK. The response content
of the delete call will be the container with the consumer list, without
the deleted consumer.