import pytest
from controllers import user_controller 
import boto3
import time
user_table_name = "TestUserTable"

class TestUserController:
    _SLEEP = 10
    _dao = user_controller.User_DAO(user_table_name)

    def _delete_table(self):
        print('_delete_table')
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(user_table_name)
        if table != None:
            table.delete()
            print("Table deleted")
            time.sleep(self._SLEEP)

    def _get_table(self):
        print('Entering _get_table')
        dynamodb = boto3.resource("dynamodb")
        return dynamodb.Table(user_table_name)
        
    def _get_table_status(self):
        print('Entering _get_table_status')
        table = self._get_table()
        return table.table_status

    def _get_table_item(self,item_id):
        print('Entering _get_table_item')
        table = _get_table()
        return table.get_item(
            key={
                'id':item_id
            }
        )
    
    #User_controller must create a table that should be accessible by boto3
    @pytest.fixture(scope='module', autouse=True)
    def setup_module_fixture(self):
        print('Entering setup_module_fixture')
        ret_value = self._dao.create_user_table()
        print('create_user_table: '+ ret_value)
        assert self._get_table_status() == "ACTIVE"
    

    def teardown_module(self):
        print('Entering teardown_module')
        self._delete_table()

    def test_dummy(self):
        print('Entering test_dummy')

    """
    #User_controller must create item on user table
    def test_create_user():
        user_param = {'name': 'Dino da Silva Sauro',
                      'senha': '123456'}
        userid = self._dao.create_user(user_param)
        time.sleep(self._SLEEP)
        assert self._get_table_item(user_id) == user_param
    """
        
