from database_client import dynamo
from definitions import return_values
from util import data_util

# User_DAO Manager User Crup operations.
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
        item = {
            'id':{'S':id},
            'name':{'S':user_param['name']},
            'password':{'S':user_param['password']}
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

    # Update  user 
    # return values:
    # TABLE_NOT_FOUND
    # INVALID_INPUT_DATA
    # USER_NOT_FOUND
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
            response = self.db_instance.client.update_item(
                TableName=self.table_name,
                Key={"id": {"S": user_id}},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues=return_values.SUCCESS
            )
        except Exception as e:
            return return_values.ERROR + str(e)

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
