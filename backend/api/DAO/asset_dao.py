from database_client import dynamo
from definitions import return_values
from util import data_util
import time

# Asset_DAO Manager Asset Crud operations.
class Asset_DAO:
    def __init__(self,asset_table_name):
        self.table_name = asset_table_name
        self.db_instance = dynamo.Dynamo_instance()
    
    def validate_asset(self, asset):
        required_fields = ['name','description','url'] 
        if not all(field in asset for field in required_fields):
            return False
        if not all(isinstance(asset[field], str) for field in required_fields):
            return False
        return True


    # create the table for assets
    # return values:
    # TABLE_ALREADY_EXISTS
    # TIME_OUT
    # SUCCESS
    def create_asset_table(self):
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
        
    
    #Create an asset 
    # return values:
    # TABLE_NOT_FOUND
    # TIME_OUT
    # SUCCESS
    def create_asset(self,asset_param):
        if not dynamo.check_table_existence(self.table_name):
            return return_values.TABLE_NOT_FOUND
        if not self.validate_asset(asset_param):
            return return_values.INVALID_INPUT_DATA
        id = data_util.create_hash(asset_param['name'])
        item = {
            'id':{'S':id},
            'name':{'S':asset_param['name']},
            'description':{'S':asset_param['description']},
            'url':{'S':asset_param['url']}
        }
        try:
            self.db_instance.client.put_item(
                TableName = self.table_name,
                Item = item
            )
        except Exception as e:
            return str(e)
        return id
        
    # Read an asset 
    # return values:
    # The asset data
    # TABLE_NOT_FOUND
    # INVALID_INPUT_DATA
    def read_asset(self,asset_id):
        if not dynamo.check_table_existence(self.table_name):
            return return_values.TABLE_NOT_FOUND
        if not asset_id:
            return return_values.INVALID_INPUT_DATA
        try:
            response = self.db_instance.client.get_item(
                    TableName = self.table_name,
                    Key = {'id': {'S': asset_id}}
            )
            if 'Item' in response:
                return response['Item']
            else:
                return return_values.asset_NOT_FOUND
        except Exception as e:
            return str(e)    

    #Wait for an iten to exist with given values
    #Useful for checking update operation
    #returns True or False
    def wait_item_status(self, asset_id, expected_values):
        max_retries = 10  
        retries = 0
        while retries < max_retries:
            updated_item = self.db_instance.client.get_item(TableName=self.table_name, Key={"id": {"S": asset_id}})
            if 'Item' in updated_item:
                mapped_values = {
                    'name': updated_item['Item']['name']['S'],
                    'description': updated_item['Item']['description']['S'],
                    'url': updated_item['Item']['url']['S']
                    }
                if mapped_values == expected_values:
                    return True 
            time.sleep(5)
            retries += 1
        return False

    # Update  asset 
    # return values:
    # TABLE_NOT_FOUND
    # INVALID_INPUT_DATA
    # asset_NOT_FOUND
    # SUCCESS
    def update_asset(self,asset_id,asset_param):
        if not dynamo.check_table_existence(self.table_name):
            return return_values.TABLE_NOT_FOUND
        if not self.validate_asset(asset_param) or not asset_id:
            return return_values.INVALID_INPUT_DATA
    
        try:
            update_expression = "SET #n = :new_name, #d = :new_description,#u = :new_url"
            expression_attribute_names = {"#n": "name", "#d": "description", "#u":"url"}
            expression_attribute_values = {
                ":new_name": {"S": asset_param['name']},
                ":new_description": {"S": asset_param['description']},
                ":new_url": {"S": asset_param['url']},
            }
            self.db_instance.client.update_item(
                TableName=self.table_name,
                Key={"id": {"S": asset_id}},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
            )
            if self.wait_item_status(asset_id,asset_param):
                return return_values.SUCCESS
            else:
                return return_values.ERROR + ": Update not successfull"
        except Exception as e:
            return return_values.ERROR +" : "+ str(e)

    # delete an asset 
    # return values:
    # TABLE_NOT_FOUND
    # INVALID_INPUT_DATA
    # SUCCESS
    def delete_asset(self,asset_id):
        if not dynamo.check_table_existence(self.table_name):
            return return_values.TABLE_NOT_FOUND
        if not asset_id:
            return return_values.INVALID_INPUT_DATA
        try:
            response = self.db_instance.client.delete_item(
                    TableName = self.table_name,
                    Key = {'id': {'S': asset_id}}
            )
            return return_values.SUCCESS
        except Exception as e:
            return str(e)    
