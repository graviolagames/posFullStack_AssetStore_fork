from database_client import dynamo
from definitions import return_values
class User_DAO:
    def __init__(self,user_table_name):
        self.table_name = user_table_name
        self.db_instance = dynamo.Dynamo_instance()
    
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
        self.db_instance.client.create_table(**table_params)
        return dynamo.wait_table_creation(self.table_name)

    #Creat an user 
    # return values:
    # TABLE_NOT_FOUND
    # TIME_OUT
    # SUCCESS
    """
    def create_user(table_name):
        if not dynamo.check_table_existence(table_name):
            return return_values.TABLE_NOT_FOUND
    """ 
    
