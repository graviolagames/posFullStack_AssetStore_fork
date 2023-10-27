import boto3
import time
from definitions import return_values

class Dynamo_instance:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance=super(Dynamo_instance,cls).__new__(cls)
            cls._instance.init_client()
        return cls._instance

    def init_client(self):
        self.client = boto3.client('dynamodb')

# Returns True or False according with a table existence
def check_table_existence(table_name):
    try:
        db_instance = Dynamo_instance()
        existing_tables = db_instance.client.list_tables()
        if table_name in existing_tables['TableNames']:
            return True 
        return False
    except Exception as e:
        print("Error check_table_existence"+str(e))
        return False

# Returns table status
def get_table_status(table_name):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        if table != None:
            return table.table_status
        return return_values.TABLE_NOT_FOUND
    except Exception as e:
        print("Error get_table_status"+str(e))
        return return_values.ERROR

# Wait for a table to get the ACTIVE state
# Return values: 
#    TABLE_NOT_FOUND
#    TIME_OUT
#    SUCCESS
def wait_table_active(table_name):
    timeout = 10
    sleep = 2
    start_time = time.time()
    status = get_table_status(table_name) 
    if status ==  return_values.TABLE_NOT_FOUND:
        return status
    while status != "ACTIVE" :
        time.sleep(sleep)
        if time.time() - start_time > timeout:
            return return_values.TIME_OUT
        status = get_table_status(table_name) 
    return return_values.SUCCESS

# Wait for table to be created and ACTIVE
# Return values: 
#    TIME_OUT
#    SUCCESS
def wait_table_creation(table_name):
    timeout = 10
    sleep = 2
    start_time = time.time()
    while not check_table_existence(table_name):
        time.sleep(sleep)
        if time.time() - start_time > timeout:
            return return_values.TIME_OUT
    return wait_table_active(table_name)