import pytest
from controllers import user_controller 
import boto3
import time
user_table_name = "TestUserTable"

class TestUserController:
    _SLEEP = 10
    def _delete_table(self):
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(user_table_name)
        if table != None:
            table.delete()
            time.sleep(self._SLEEP)

    def _get_table(self):
        dynamodb = boto3.resource("dynamodb")
        return dynamodb.Table(user_table_name)
        
    def _get_table_status(self):
        table = self._get_table()
        return table.table_status

    def _get_table_item(self,item_id):
        table = _get_table()
        return table.get_item(
            key={
                'id':item_id
            }
        )
        
    def setup_module(module):
        self._delete_table()

    def teardown_method(self):
        self._delete_table()

    """
    @pytest.fixture
    def create_table():
        dao = user_controller.User_DAO(user_table_name)
        dao.create_user_table()
    """

    #User_controller must create a table that should be accessible by boto3
    def test_create_user_table(self):
        dao = user_controller.User_DAO(user_table_name)
        ret_value = dao.create_user_table()
        print(ret_value)
        assert self._get_table_status() == "ACTIVE"

    """
    #User_controller must create item on user table
    def test_create_user(create_table):
        user_param = {'name': 'Dino da Silva Sauro',
                      'senha': '123456'}
        userid = user_controller.create_user(user_param)
        time.sleep(self._SLEEP)
        assert self._get_table_item(user_id) == user_param
    """
        
