from database_client import dynamo
from definitions import return_values
from util import data_util
import hashlib
import os
import hmac

# User_DAO Manager User Crud operations.
class User_DAO:
    def __init__(self,user_table_name):
        self.table_name = user_table_name
        self.db_instance = dynamo.Dynamo_instance()
    
    def validate_user(self, user): 
        if 'name' not in user or 'password' not in user :
            return False
        if not isinstance(user['name'], str) or not isinstance(user['password'], str):
            return False
        return True

    def encode_password(self,password, salt=None):
        if salt is None:
            salt = os.urandom(16)
        rounds = 100000
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, rounds)
        return {
            'hash': 'sha256',
            'salt': salt,
            'rounds': rounds,
            'hashed': hashed,
        }

    # create the table for users
    # return values:
    # TABLE_ALREADY_EXISTS
    # TIME_OUT
    # SUCCESS
    def create_user_table(self):
        if dynamo.check_table_existence(self.table_name):
            return return_values.TABLE_ALREADY_EXISTS
        table_params = {
            'TableName': self.table_name,
            'KeySchema': [
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'id', 'AttributeType': 'S'}
            ],
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            } 
        }
        try:
            self.db_instance.client.create_table(**table_params)
        except Exception as e:
            return str(e)
        return dynamo.wait_table_creation(self.table_name)
        
    
    #Create an user 
    # return values:
    # TABLE_NOT_FOUND
    # TIME_OUT
    # SUCCESS
    def create_user(self,user_param):

        if not dynamo.check_table_existence(self.table_name):
            return return_values.TABLE_NOT_FOUND
        if not self.validate_user(user_param):
            return return_values.INVALID_INPUT_DATA
        id = data_util.create_hash(user_param['name'])

        password_fields = self.encode_password(user_param['password'])

        item = {
            'id':{'S':id},
            'name':{'S':user_param['name']},
            'password':{'S':user_param['password']},
            'hash':{'B':password_fields['hash']},
            'salt':{'B':password_fields['salt']},
            'rounds':{'N':str(password_fields['rounds'])},
            'hashed':{'B':password_fields['hashed']},
        }

        try:
            self.db_instance.client.put_item(
                TableName = self.table_name,
                Item = item
            )
        except Exception as e:
            return str(e)
        return id
        
    # Read an user 
    # return values:
    # The user data
    # TABLE_NOT_FOUND
    # INVALID_INPUT_DATA
    def read_user(self,user_id):
        if not dynamo.check_table_existence(self.table_name):
            return return_values.TABLE_NOT_FOUND
        if not user_id:
            return return_values.INVALID_INPUT_DATA
        try:
            response = self.db_instance.client.get_item(
                    TableName = self.table_name,
                    Key = {'id': {'S': user_id}}
            )
            if 'Item' in response:
                return response['Item']
            else:
                return return_values.USER_NOT_FOUND
        except Exception as e:
            return str(e)    

    #Wait for an iten to exist with given values
    #Useful for checking update operation
    #returns True or False
    def wait_item_status(self, user_id, expected_values):
        max_retries = 10  
        retries = 0
        while retries < max_retries:
            updated_item = self.db_instance.client.get_item(TableName=self.table_name, Key={"id": {"S": user_id}})
            if 'Item' in updated_item:
                mapped_values = {
                    'name': updated_item['Item']['name']['S'],
                    'password': updated_item['Item']['password']['S']
                    }
                if mapped_values == expected_values:
                    return True 
            time.sleep(5)
            retries += 1
        return False

    # Update  user 
    # return values:
    # TABLE_NOT_FOUND
    # INVALID_INPUT_DATA
    # user_NOT_FOUND
    # SUCCESS
    def update_user(self,user_id,user_param):
        if not dynamo.check_table_existence(self.table_name):
            return return_values.TABLE_NOT_FOUND
        if not self.validate_user(user_param) or not user_id:
            return return_values.INVALID_INPUT_DATA
    
        try:
            update_expression = "SET #n = :new_name, #p = :new_password"
            expression_attribute_names = {"#n": "name", "#p": "password"}
            expression_attribute_values = {
                ":new_name": {"S": user_param['name']},
                ":new_password": {"S": user_param['password']}
            }
            self.db_instance.client.update_item(
                TableName=self.table_name,
                Key={"id": {"S": user_id}},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
            )
            if self.wait_item_status(user_id,user_param):
                print("item status confirmed")
                return return_values.SUCCESS
            else:
                print("item status NOT confirmed")
                return return_values.ERROR + ": Update not successfull"
        except Exception as e:
            return return_values.ERROR +" : "+ str(e)

    # delete an user 
    # return values:
    # TABLE_NOT_FOUND
    # INVALID_INPUT_DATA
    # SUCCESS
    def delete_user(self,user_id):
        if not dynamo.check_table_existence(self.table_name):
            return return_values.TABLE_NOT_FOUND
        if not user_id:
            return return_values.INVALID_INPUT_DATA
        try:
            response = self.db_instance.client.delete_item(
                    TableName = self.table_name,
                    Key = {'id': {'S': user_id}}
            )
            return return_values.SUCCESS
        except Exception as e:
            return str(e)    
    
    def user_login(self, username, password):
        id = data_util.create_hash(username)
        try:
            response = self.db_instance.client.get_item(
                    TableName = self.table_name,
                    Key = {'id': {'S': id}}
            )
            if 'Item' in response:
                user = response['Item']
                password_fields = {
                    'hash': user['hash']['B'],
                    'salt': user['salt']['B'],
                    'rounds': user['rounds']['N'],
                    'hashed': user['hashed']['B'],
                }
                hashed = self.encode_password(password, password_fields['salt'])
                if hashed['hashed'] == password_fields['hashed']:
                    return return_values.SUCCESS
                else:
                    return return_values.INVALID_INPUT_DATA
            else:
                return return_values.USER_NOT_FOUND
        except Exception as e:
            return str(e)
