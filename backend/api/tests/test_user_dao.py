import pytest
from DAO import user_dao as dao
import boto3
import time

class TestUserDAO:
    _SLEEP = 10
    _user_table_name = "TestUserTable"
    _dao = None

    @classmethod
    def _delete_table(cls):
        print('Entering _delete_table')
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(cls._user_table_name)
        if table:
            table.delete()
            print("Table deleted")
            time.sleep(cls._SLEEP)
        print('Table was not deleted (Not found)')

    @classmethod
    def _get_table(cls):
        print('Entering _get_table')
        dynamodb = boto3.resource("dynamodb")
        response =  dynamodb.Table(cls._user_table_name)
        return response

    @classmethod    
    def _get_table_status(cls):
        print('Entering _get_table_status')
        table = cls._get_table()
        if table:
            return table.table_status
        return return_values.TABLE_NOT_FOUND

    @classmethod
    def _get_table_item(cls,item_id):
        print('Entering _get_table_item')
        table = cls._get_table()
        if table:
            return table.get_item(
                Key={
                    'id':item_id
                }
            )
        return return_values.TABLE_NOT_FOUND
        
    
    #User_DAO must create a table that should be accessible by boto3
    def setup_class(self):
        self._dao = dao.User_DAO(self._user_table_name)
        print('Entering setup_class')
        ret_value = self._dao.create_user_table()
        print('create_user_table: '+ ret_value)
        table_status = self._get_table_status() 
        assert table_status == "ACTIVE"
    
        
    #User_DAO must create item on user table
    def test_create_user(self):
        print('Entering test_create_user')
        user_param = {'name': 'Dino da Silva Sauro',
                      'password': '123456'}
        id = self._dao.create_user(user_param)
        print('expected item id as response. Received ' + id)
        time.sleep(self._SLEEP)
        response = self._get_table_item(id)
        response_item = response['Item']
        assert response_item["name"] == user_param["name"]
        assert response_item["password"] == user_param["password"]
    
    def teardown_class(self):
        print('Entering teardown_class')
        self._delete_table()

