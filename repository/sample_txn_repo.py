import csv
import io

from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from pyspark.sql import SparkSession
import pandas as pd
from icgphutils.aws.dynamodb import DynamoDB
from icgphutils.log import Logger

from values.sample_txn_value import SampleTxnValueList, SampleTxnValue


class SampleTxnRepo:
    def __init__(self, config):
        self.__logger = Logger.get_logger()
        self.__table_name = config("DB_NAME")
        self.__gsi_index_name = config("GSI_INDEX_NAME")
        self.__db_client = DynamoDB(self.__table_name)
        self.__spark = SparkSession \
            .builder \
            .appName("SampleTxnRepo") \
            .getOrCreate()

    @staticmethod
    def convert_list_of_dicts_to_pandas_df(input_list: dict):
        headers = list(input_list[0].keys())
        stream = io.StringIO()
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()

        for record in input_list:
            writer.writerow(record)

        return pd.read_csv(io.StringIO(stream.getvalue()))

    def convert_pandas_df_to_spark_df(self, input_df):
        return self.__spark.createDataFrame(input_df)

    def scan(self):
        result = []
        query_kwargs = dict()
        query_kwargs["TableName"] = self.__table_name
        query_kwargs["ConsistentRead"] = False
        try:
            result = self.__db_client.scan(**query_kwargs)
            result = {"transactions": result["Items"]}
            result = SampleTxnValueList.Schema().load(result)
            result = SampleTxnValueList.Schema().dump(result)
        except Exception as e:
            self.__logger.error(e)
        return result

    def get_item(self, txn_id: str):
        keys = {"txn_id": txn_id}
        result = self.__db_client.get_item(keys)
        result = SampleTxnValue.Schema().load(result)
        result = SampleTxnValue.Schema().dump(result)
        return result

    def put_item(self, payload):
        result = True

        try:
            self.__db_client.add_item(payload, ["txn_id"])
        except ClientError as e:
            self.__logger.error(e.response.get('Error').get('Message'))
            result = False

        if result:
            self.__logger.debug(f"Saved: {payload}")

    def delete_item(self, txn_id: str):
        result = True

        keys = {
            "txn_id": txn_id,
        }

        try:
            self.__db_client.delete_item(
                keys
            )
        except ClientError as e:
            self.__logger.error(e.response.get('Error').get('Message'))
            result = False

        if result:
            self.__logger.debug(f"Deleted item with key: {keys}")

    def query(
        self, client_id, from_date_time, to_date_time
    ):
        key_condition_expression = Key("client_id").eq(client_id) & Key("business_date").between(
            from_date_time, to_date_time
        )

        query_kwargs = {
            "TableName": self.__table_name,
            "IndexName": self.__gsi_index_name,
            "KeyConditionExpression": key_condition_expression,
            "ScanIndexForward": True,
        }

        result_list = []
        last_key = None

        try:
            start_key = None
            if start_key:
                query_kwargs["ExclusiveStartKey"] = start_key
            response = self.__db_client.query(**query_kwargs)
            items = response.get("Items", [])
            result_list.extend(items)
            last_key = response.get("LastEvaluatedKey", None)
        except ClientError as e:
            self.__logger.error("DynamoDB error" + str(e))

        dict_result = {"transactions": result_list}
        return_payload = SampleTxnValueList.Schema().load(dict_result)
        return_payload = SampleTxnValueList.Schema().dump(return_payload)
        return return_payload, last_key
