*************************
Consumers API - Reference
*************************

GET {container_ref}/consumers
#############################
Lists a containers consumers.

The list of consumers can be filtered by the parameters passed in via the URL.

.. _consumer_parameters:

Parameters
**********

+----------+---------+----------------------------------------------------------------+
| Name     | Type    | Description                                                    |
+==========+=========+================================================================+
| offset   | integer | The starting index within the total list of the consumers that |
|          |         | you would like to retrieve.                                    |
+----------+---------+----------------------------------------------------------------+
| limit    | integer | The maximum number of records to return (up to 100). The       |
|          |         | default limit is 10.                                           |
+----------+---------+----------------------------------------------------------------+

.. _consumer_response_attributes:

Response Attributes
*******************

+----------+---------+---------------------------------------------------------------+
| Name     | Type    | Description                                                   |
+==========+=========+============================================================== +
| consumers| list    | Contains a list of dictionaries filled with consumer metadata.|
+----------+---------+---------------------------------------------------------------+
| total    | integer | The total number of consumers available to the user.          |
+----------+---------+---------------------------------------------------------------+
| next     | string  | A HATEOS url to retrieve the next set of consumers based on   |
|          |         | the offset and limit parameters. This attribute is only       |
|          |         | available when the total number of consumers is greater than  |
|          |         | offset and limit parameter combined.                          |
+----------+---------+---------------------------------------------------------------+
| previous | string  | A HATEOS url to retrieve the previous set of consumers based  |
|          |         | on the offset and limit parameters. This attribute is only    |
|          |         | available when the request offset is greater than 0.          |
+----------+---------+---------------------------------------------------------------+


.. _consumer_status_codes:

HTTP Status Codes
*****************

+------+-----------------------------------------------------------------------------+
| Code | Description                                                                 |
+======+=============================================================================+
| 200  | Successful Request                                                          |
+------+-----------------------------------------------------------------------------+
| 401  | Invalid X-Auth-Token or the token doesn't have permissions to this resource |
+------+-----------------------------------------------------------------------------+


.. _post_consumers:

POST {container_ref}/consumers
##############################

Creates a consumer

Attributes
**********

+----------------------------+---------+----------------------------------------------+------------+
| Attribute Name             | Type    | Description                                  | Default    |
+============================+=========+==============================================+============+
| name                       | string  | The name of the consumer set by the user.    | None       |
+----------------------------+---------+----------------------------------------------+------------+
| url                        | string  | The url for the user or service using the    | None       |
|                            |         | container.                                   |            |
+----------------------------+---------+----------------------------------------------+------------+

Request:
********

.. code-block:: json

    POST {container_ref}/consumers
    Headers:
        X-Project-Id: {project_id}

    Content:
    {
        "name": "ConsumerName",
        "url": "ConsumerURL"
    }

Response:
*********

.. code-block:: json

    200 OK

    {
        "status": "ACTIVE",
        "updated": "2015-10-15T17:56:18.626724",
        "name": "container name",
        "consumers": [
            {
                "URL": "consumerURL",
                "name": "consumername"
            }
        ],
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


HTTP Status Codes
*****************

+------+-----------------------------------------------------------------------------+
| Code | Description                                                                 |
+======+=============================================================================+
| 200  | OK                                              |
+------+-----------------------------------------------------------------------------+
| 400  | Bad Request                                                                 |
+------+-----------------------------------------------------------------------------+
| 401  | Invalid X-Auth-Token or the token doesn't have permissions to this resource |
+------+-----------------------------------------------------------------------------+
| 403  | Forbidden.  The user has been authenticated, but is not authorized to       |
|      | create a consumer. This can be based on the the user's role or the            |
|      | project's quota.                                                            |
+------+-----------------------------------------------------------------------------+


.. _delete_consumer:

DELETE {container_ref}/consumers
################################

Delete a consumer.

Attributes
**********

+----------------------------+---------+----------------------------------------------+------------+
| Attribute Name             | Type    | Description                                  | Default    |
+============================+=========+==============================================+============+
| name                       | string  | The name of the consumer set by the user.    | None       |
+----------------------------+---------+----------------------------------------------+------------+
| url                        | string  | The url for the user or service using the    | None       |
|                            |         | container.                                   |            |
+----------------------------+---------+----------------------------------------------+------------+

Request:
********

.. code-block:: json

    POST {container_ref}/consumers
    Headers:
        X-Project-Id: {project_id}

    Content:
    {
        "name": "ConsumerName",
        "url": "ConsumerURL"
    }


Response:
*********

.. code-block:: json

    200 OK

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


HTTP Status Codes
*****************

+------+-----------------------------------------------------------------------------+
| Code | Description                                                                 |
+======+=============================================================================+
| 200  | OK                                                                          |
+------+-----------------------------------------------------------------------------+
| 401  | Invalid X-Auth-Token or the token doesn't have permissions to this resource |
+------+-----------------------------------------------------------------------------+
| 404  | Not Found                                                                   |
+------+-----------------------------------------------------------------------------+
