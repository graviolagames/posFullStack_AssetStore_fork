import pytest
from controllers import user_controller 
import boto3

user_table_name = "TestUserTable"

class TestUserController:
    def _delete_table(self):
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(user_table_name)
        if table != None:
            table.delete()

    def setup_module(module):
        self._delete_table()

    def teardown_method(self):
        self._delete_table()

    #User_controller must create a table that should be accessible by boto3
    def test_create_user_table(self):
        user_controller.create_user_table(user_table_name)
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(user_table_name)
        assert table.table_status == "ACTIVE"
    

