import base64
import datetime
import json
import sys
import traceback

import iso8601
from google.cloud import bigquery
from google.cloud.bigquery import TableReference, DatasetReference, Table, SchemaField
from google.cloud.bigquery.enums import SqlTypeNames

DATASET = 'raw_events'

bq_types = {
    str: SqlTypeNames.STRING,
    datetime.datetime: SqlTypeNames.DATETIME,
    float: SqlTypeNames.FLOAT,
    int: SqlTypeNames.INTEGER
}


def main(event, context):
    try:
        pubsub_to_bq(event, context)
    except Exception as e:
        print(repr(e), file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)


def pubsub_to_bq(event, context):
    print(f"CONTEXT: {context}")
    pubsub_message = decode_event(event)
    table_name, row = create_row(pubsub_message, context)
    print(f"ROW: {row}")
    send_to_bq(
        dataset=DATASET,
        table=table_name,
        row=row
    )


def decode_event(event):
    return base64.b64decode(event['data']).decode('utf-8')


def create_row(raw, context):
    """
    message type can be state or telemetry
    namespace can be hue only atm
    """
    message = json.loads(raw)
    message_type = message.get("type", "unknown")
    message_source = message.get("source", "unknown")
    table_name = f"raw_{message_type}_{message_source}"
    row = {
        "payload": raw,
        "event_id": context.event_id,
        "insertion_datetime": iso8601.parse_date(context.timestamp),
        "resource_name": context.resource['name']
    }
    return table_name, row


def send_to_bq(dataset, table, row):
    bigquery_client = bigquery.Client(project='theo-home')

    table_ref = TableReference(
        dataset_ref=DatasetReference(dataset_id=dataset, project='theo-home'),
        table_id=table,
    )

    schema = [SchemaField(name=field, field_type=bq_types[type(data)]) for field, data in row.items()]

    table = bigquery_client.create_table(
        Table(table_ref, schema=schema),
        exists_ok=True
    )

    errors = bigquery_client.insert_rows(table, [row])
    if errors:
        print(errors, file=sys.stderr)
