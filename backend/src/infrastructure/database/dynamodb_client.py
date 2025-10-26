"""
Infrastructure層: DynamoDB接続設定
"""
import os
import boto3
from botocore.exceptions import ClientError


class DynamoDBClient:
    """DynamoDBクライアントのシングルトン"""

    _instance = None
    _resource = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_resource(self):
        """DynamoDBリソースを取得"""
        if self._resource is None:
            endpoint_url = os.getenv("DYNAMODB_ENDPOINT", "http://localhost:8001")

            self._resource = boto3.resource(
                'dynamodb',
                endpoint_url=endpoint_url,
                region_name=os.getenv("AWS_DEFAULT_REGION", "ap-northeast-1"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "dummy"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "dummy")
            )

        return self._resource

    def create_todos_table(self):
        """TODOテーブルを作成"""
        dynamodb = self.get_resource()
        table_name = "Todos"

        try:
            # 既存のテーブルを取得
            table = dynamodb.Table(table_name)
            table.load()
            print(f"テーブル '{table_name}' は既に存在します。")
            return table
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # テーブルが存在しない場合は作成
                print(f"テーブル '{table_name}' を作成中...")
                table = dynamodb.create_table(
                    TableName=table_name,
                    KeySchema=[
                        {
                            'AttributeName': 'id',
                            'KeyType': 'HASH'
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'id',
                            'AttributeType': 'S'
                        }
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )

                # テーブルが作成されるまで待機
                table.wait_until_exists()
                print(f"テーブル '{table_name}' が作成されました。")
                return table
            else:
                raise

    def get_table(self, table_name: str):
        """テーブルを取得"""
        dynamodb = self.get_resource()
        return dynamodb.Table(table_name)
