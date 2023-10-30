import boto3
from botocore.client import BaseClient
import pytest
from database_client import dynamo

class TestDynamoInstance:

    # Dynamo_instance should return a valid boto3 instance 
    def test_boto3_client(self):
        instance = dynamo.Dynamo_instance()
        assert instance.client is not None
        assert isinstance(instance.client,BaseClient)
        
    # Dynamo_instace should behave as a singleton object, returning a unique instance
    def test_singleton_instance(self):
        instance1 = dynamo.Dynamo_instance()
        instance2 = dynamo.Dynamo_instance()
        assert instance1.client is instance2.client

    

