from database_client import dynamo

# create the table for users
def create_user_table(table_name):
    if dynamo.check_table_existence(table_name):
        return False
    db_instance = dynamo.Dynamo_instance()
    table_params = {
        'TableName': table_name,
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
    db_instance.client.create_table(**table_params)
    return dynamo.wait_table_creation(table_name)
