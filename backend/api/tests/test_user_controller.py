import pytest
from controllers import user_controller 
import boto3

user_table_name = "TestUserTable"

class TestUserController:
    #User_controller must create a table that should be accessible by boto3
    def test_create_user_table(self):
        user_controller.create_user_table(user_table_name)
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(user_table_name)
        assert table.table_status == "ACTIVE"
    
    #delete the testing table
    def teardown_method(self):
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(user_table_name)
        table.delete()

