import pytest
from DAO import user_dao as dao
from util import data_util
from definitions import return_values
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
    
    #User_DAO must read an existing user
    def test_read_user(self):
        print('Entering test_read_user')
        table = self._get_table()
        if table:
            user_param = {
                            'name': 'Fran da Silva Sauro',
                            'password': 'mypass'
                        }
            user_id = data_util.create_hash(user_param['name'])
            user_item = {
                'id': user_id,
                'name': user_param['name'],
                'password': user_param['password']
            }
            table.put_item(Item=user_item)
            time.sleep(self._SLEEP)

            response = self._dao.read_user(user_id)
            
            assert response == {
                'id': {'S': user_id},
                'name': {'S': user_param['name']},
                'password': {'S': user_param['password']}
            }
        else:
            print("Test skipped (User Table not found)")    

    #User_DAO must delete an existing user
    def test_delete_user(self):
        print('Entering test_delete_user')
        table = self._get_table()
        if table:
            user_param = {
                            'name': 'Sr. Richfield',
                            'password': 'TheBo$$'
                        }
            user_id = data_util.create_hash(user_param['name'])
            user_item = {
                'id': user_id,
                'name': user_param['name'],
                'password': user_param['password']
            }
            table.put_item(Item=user_item)
            time.sleep(self._SLEEP)

            result = self._dao.delete_user(user_id)

            assert result == return_values.SUCCESS
            response = table.get_item(Key={'id':user_id})
            assert 'Item' not in response
        else:
            printf("Test skipped (User table not found)")

    def teardown_class(self):
        print('Entering teardown_class')
        self._delete_table()

