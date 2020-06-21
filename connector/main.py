import base64
import os
import sys

import iso8601
from google.cloud import bigquery
from google.cloud.bigquery import TableReference, DatasetReference


def pubsub_to_bq(event, context):
    try:
        pubsub_message = decode_event(event)
        payload = create_payload(pubsub_message, context)
        send_to_bq(
            dataset=os.environ['dataset'],
            table=os.environ['table'],
            payload=payload
        )
    except Exception as e:
        print(repr(e))


def decode_event(event):
    return base64.b64decode(event['data']).decode('utf-8')


def create_payload(message, context):
    return {
        "payload": message,
        "event_id": context.event_id,
        "timestamp": iso8601.parse_date(context.timestamp),
        "resource_name": context.resource['name']
    }


def send_to_bq(dataset, table, payload):
    bigquery_client = bigquery.Client(project='theo-home')
    table_ref = TableReference(
        dataset_ref=DatasetReference(dataset_id=dataset, project='theo-home'),
        table_id=table,
    )
    table = bigquery_client.get_table(table_ref)
    errors = bigquery_client.insert_rows(table, [payload])
    if errors:
        print(errors, file=sys.stderr)
        raise RuntimeError(errors)
