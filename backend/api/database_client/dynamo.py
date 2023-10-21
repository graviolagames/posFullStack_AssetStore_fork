import boto3
class Dynamo_instance:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance=super(Dynamo_instance,cls).__new__(cls)
            cls._instance.init_client()
        return cls._instance

    def init_client(self):
        self.client = boto3.client('dynamodb')