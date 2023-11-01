from database_client import dynamo
from definitions import return_values
from util import data_util
from DAO import update_expression

class DAO:
    field_names = [] #Stores the table field names
                     
    def __init__(self,table_name):
        self.table_name = table_name
        self.db_instance = dynamo.Dynamo_instance()
        #A derivative class must set field names.
        #Example:
       

    #Create id for a item
    #Must be implemented by derivative class
    def create_item_id(self,item_param):
        #Example: 
        #return data_util.create_hash(item_param['name']) 
        return None

    #Format item for writing operations 
    #Must be implemented by derivative class
    def format_item_for_writing(self,item_id,item_param):
        #Example: 
        #return {
        #    'id':{'S':item_id},
        #    'name':{'S':item_param['name']},
        #    'description':{'S':item_param['description']},
        #    'url':{'S':item_param['url']}
        #}
        return item_param

    #format item from reading operations    
    #Must be implemented by derivative class
    def format_item_from_reading(self,read_item_data)
        #Example: 
        #return  {
        #            'name': read_item_data['Item']['name']['S'],
        #            'description': read_item_data['Item']['description']['S'],
        #            'url': read_item_data['Item']['url']['S']
        #        }
        return item_param

    #Create update expressions
    #Must be implemented by derivative class
    #Must return update expressions for update operations 
    def create_update_expression(self,item_param):
        #Example:
        #expression = update_expression.UpdateExpression(
        #    "SET #n = :new_name, #d = :new_description,#u = :new_url",
        #    {"#n": "name", "#d": "description", "#u":"url"},
        #    {
        #        ":new_name": {"S": item_param['name']},
        #        ":new_description": {"S": item_param['description']},
        #        ":new_url": {"S": item_param['url']},
        #    }
        #)
        #return expression
        return None

    # Validate item
    #Must be implemented by derivative class
    #Must returns True or false
    def validate_item(self, item):
        #Example:
        #field_names = ['name','description','url']
        #if not all(field in item for field in field_names):
        #    return False
        #if not all(isinstance(item[field], str) for field in field_names):
        #    return False
        #return True
        return False

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
    def create_item(self,item_param):
        if not dynamo.check_table_existence(self.table_name):
            return return_values.TABLE_NOT_FOUND
        if not self.validate_item(item_param):
            return return_values.INVALID_INPUT_DATA
        id = self.create_item_id(item_param)
        item = self.format_item_for_writing(id,item_param)
        try:
            self.db_instance.client.put_item(
                TableName = self.table_name,
                Item = item
            )
        except Exception as e:
            return str(e)
        return id
        
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
                mapped_values = self.format_item_for_writing(item_id,item)
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
    def update_item(self,item_id,item_param):
        if not dynamo.check_table_existence(self.table_name):
            return return_values.TABLE_NOT_FOUND
        if not self.validate_item(item_param) or not item_id:
            return return_values.INVALID_INPUT_DATA
    
        try:
            expression = self.create_update_expression(item_param)
            self.db_instance.client.update_item(
                TableName=self.table_name,
                Key={"id": {"S": item_id}},
                UpdateExpression=expression.expression,
                ExpressionAttributeNames=expression.attribute_names,
                ExpressionAttributeValues=expression.attribute_values,
            )
            if self.wait_item_status(item_id,item_param):
                return return_values.SUCCESS
            else:
                return return_values.ERROR + ": Update not successfull"
        except Exception as e:
            return return_values.ERROR +" : "+ str(e)


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
    
