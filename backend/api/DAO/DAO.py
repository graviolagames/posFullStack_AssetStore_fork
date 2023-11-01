from database_client import dynamo
from definitions import return_values
from util import data_util

class DAO:
    def __init__(self,table_name):
        self.table_name = table_name
        self.db_instance = dynamo.Dynamo_instance()

    # create DynamoDB table
    # return values:
    # TABLE_ALREADY_EXISTS
    # TIME_OUT
    # SUCCESS
    def create_table(self):
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
    
    #Create item 
    # return values:
    # TABLE_NOT_FOUND
    # TIME_OUT
    # SUCCESS
    #[TODO]

    # Read an item 
    # return values:
    # The item data
    # TABLE_NOT_FOUND
    # INVALID_INPUT_DATA
    def read_ITEM(self,item_id):
        if not dynamo.check_table_existence(self.table_name):
            return return_values.TABLE_NOT_FOUND
        if not item_id:
            return return_values.INVALID_INPUT_DATA
        try:
            response = self.db_instance.client.get_item(
                    TableName = self.table_name,
                    Key = {'id': {'S': item_id}}
            )
            if 'Item' in response:
                return response['Item']
            else:
                return return_values.ITEM_NOT_FOUND
        except Exception as e:
            return str(e)
    
    #Wait for an iten to exist with given values
    #Useful for checking update operation
    #returns True or False
    def wait_item_status(self, item_id, expected_values):
        max_retries = 10  
        retries = 0
        while retries < max_retries:
            item = self.db_instance.client.get_item(TableName=self.table_name, Key={"id": {"S": item_id}})
            if 'Item' in item:
                mapped_values = {
                    'name': item['Item']['name']['S'],
                    'password': item['Item']['password']['S']
                    }
                if mapped_values == expected_values:
                    return True 
            time.sleep(5)
            retries += 1
        return False

    # Update  item 
    # return values:
    # TABLE_NOT_FOUND
    # INVALID_INPUT_DATA
    # ITEM_NOT_FOUND
    # SUCCESS
    #[TODO]

    # delete an item 
    # return values:
    # TABLE_NOT_FOUND
    # INVALID_INPUT_DATA
    # SUCCESS
    def delete_item(self,item_id):
        if not dynamo.check_table_existence(self.table_name):
            return return_values.TABLE_NOT_FOUND
        if not item_id:
            return return_values.INVALID_INPUT_DATA
        try:
            response = self.db_instance.client.delete_item(
                    TableName = self.table_name,
                    Key = {'id': {'S': item_id}}
            )
            return return_values.SUCCESS
        except Exception as e:
            return str(e)    
    
