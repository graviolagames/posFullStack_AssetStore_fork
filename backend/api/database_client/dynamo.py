import boto3
import time
class Dynamo_instance:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance=super(Dynamo_instance,cls).__new__(cls)
            cls._instance.init_client()
        return cls._instance

    def init_client(self):
        self.client = boto3.client('dynamodb')

def check_table_existence(table_name):
    db_instance = Dynamo_instance()
    existing_tables = db_instance.client.list_tables()
    if table_name in existing_tables['TableNames']:
        return True 
    return False

def wait_table_active(table_name):
    timeout = 10
    sleep = 2
    start_time = time.time()
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    start_time = time.time()
    while table.table_status != "ACTIVE":
        time.sleep(sleep)
        if time.time() - start_time > timeout:
            return False
    return True

def wait_table_creation(table_name):
    timeout = 10
    sleep = 2
    start_time = time.time()
    while not check_table_existence(table_name):
        time.sleep(sleep)
        if time.time() - start_time > timeout:
            return False 
    return wait_table_active(table_name)