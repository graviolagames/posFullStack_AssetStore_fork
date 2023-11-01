from database_client import dynamo
from definitions import return_values
from util import data_util

class ExampleAssetDAO(DAO):
    def __init__(self,table_name):
        super().__init__(table_name)

    #[IMPLEMENTATION]
    # Create id for a item
    def create_item_id(self,item_param):
        return data_util.create_hash(item_param['name']) 

    #[IMPLEMENTATION]
    # Format item for writing operations 
    #Must be implemented by derivative class
    def format_new_item(self,item_id,item_param):
        item = {
            'id':{'S':item_id},
            'name':{'S':item_param['name']},
            'description':{'S':item_param['description']},
            'url':{'S':item_param['url']}
        }
        return item

    #[IMPLEMENTATION] 
    #Format item from reading operations    
    def format_item_from_reading(self,read_item_data)
        return  {
                    'name': read_item_data['Item']['name']['S'],
                    'description': read_item_data['Item']['description']['S'],
                    'url': read_item_data['Item']['url']['S']
                }
        return item_param

    #[IMPLEMENTATION] 
    #Create update expressions
    #Must return update expressions for update operations 
    def create_update_expression(self,item_param):
        expression = update_expression.UpdateExpression(
            "SET #n = :new_name, #d = :new_description,#u = :new_url",
            {"#n": "name", "#d": "description", "#u":"url"},
            {
                ":new_name": {"S": item_param['name']},
                ":new_description": {"S": item_param['description']},
                ":new_url": {"S": item_param['url']},
            }
        )
        return expression
        


    #[IMPLEMENTATION] 
    #Validate item
    #Returns True or false
    def validate_item(self, item):
        field_names = ['name','description','url']
        if not all(field in item for field in field_names):
            return False
        if not all(isinstance(item[field], str) for field in field_names):
            return False
        return True
        
    