import pytest
from DAO import asset_dao as dao
from util import data_util
from definitions import return_values
import boto3
import time

class TestAssetDAO:
    _SLEEP = 10
    _asset_table_name = "TestAssetTable"
    _dao = None

    @classmethod
    def _delete_table(cls):
        print('Entering _delete_table')
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(cls._asset_table_name)
        if table:
            table.delete()
            print("Table deleted")
            time.sleep(cls._SLEEP)
        print('Table was not deleted (Not found)')

    @classmethod
    def _get_table(cls):
        print('Entering _get_table')
        dynamodb = boto3.resource("dynamodb")
        response =  dynamodb.Table(cls._asset_table_name)
        return response

    @classmethod    
    def _get_table_status(cls):
        print('Entering _get_table_status')
        table = cls._get_table()
        if table:
            return table.table_status
        return return_values.TABLE_NOT_FOUND

    @classmethod
    def _get_table_item(cls,item_id):
        print('Entering _get_table_item')
        table = cls._get_table()
        if table:
            return table.get_item(
                Key={
                    'id':item_id
                }
            )
        return return_values.TABLE_NOT_FOUND
        
    
    #asset_DAO must create a table that should be accessible by boto3
    def setup_class(self):
        self._dao = dao.Asset_DAO(self._asset_table_name)
        print('Entering setup_class')
        ret_value = self._dao.create_asset_table()
        print('create_asset_table: '+ ret_value)
        table_status = self._get_table_status() 
        assert table_status == "ACTIVE",f'Error: asset table is suposed to be active'
    
        
    #asset_DAO must create item on asset table
    def test_create_asset(self):
        print('Entering test_create_asset')
        asset_param = {'name': 'Medieval Tileset',
                      'description': 'A packet containing medieval themed tilesets for 2D RPG Games',
                      'url': 'http://www.archive.com/63482/medievaltiles.zip'}
        id = self._dao.create_asset(asset_param)
        print('expected item id as response. Received ' + id)
        time.sleep(self._SLEEP)
        response = self._get_table_item(id)
        response_item = response['Item']
        assert response_item["name"] == asset_param["name"],f'Error testing created asset. name diverges'
        assert response_item["description"] == asset_param["description"],f'Error testing created asset. description diverges'
        assert response_item["url"] == asset_param["url"],f'Error testing created asset. url diverges'
    
    #asset_DAO must read an existing asset
    def test_read_asset(self):
        print('Entering test_read_asset')
        table = self._get_table()
        if table:
            asset_param = {
                            'name': 'Cyberpunk 3d characters',
                            'description': 'Packet with cyberpunk themed character 3d models (Male and female with animations)',
                            'url': 'http://www.archive.com/32684/CP_Characters.zip'
                        }
            asset_id = data_util.create_hash(asset_param['name'])
            asset_item = {
                'id': asset_id,
                'name': asset_param['name'],
                'description': asset_param['description'], 
                'url':asset_param['url']
            }
            table.put_item(Item=asset_item)
            time.sleep(self._SLEEP)

            response = self._dao.read_asset(asset_id)
            
            assert response == {
                'id': {'S': asset_id},
                'name': {'S': asset_param['name']},
                'description': {'S': asset_param['description']},
                'url': {'S': asset_param['url']}
            },f'Error reading asset. Incorrect response'
        else:
            print("Test skipped (asset Table not found)")    

    #asset_DAO must update an existing asset
    def test_update_asset(self):
        print('Entering test_update_asset')
        table = self._get_table()
        if table:
            asset_param = {
                'name':'2D nature textures',
                'description': 'Set of realistic textures for nature (wildlife) anbient',
                'url':'http://www.archive.com/68758850/nature_textures.zip'
            }
            asset_id = data_util.create_hash(asset_param['name'])
            asset_item = {
                'id': asset_id,
                'name': asset_param['name'],
                'description': asset_param['description'],
                'url': asset_param['url']
            }
            table.put_item(Item=asset_item)
            time.sleep(self._SLEEP)
            
            updated_name = '2D city textures'
            updated_description = 'Set of realistic textures for urban locations'
            updated_url = 'http://www.archive.com/68758850/urban_textures.zip'

            result = self._dao.update_asset(asset_id,asset_param)
            assert result == return_values.SUCCESS,f'Error testing asset update. Incorrect response'
            response = table.get_item(Key={'id': asset_id})
            updated_item = response.get('Item', {})
            assert updated_item.get('name', {}).get('S') == updated_name, f'asset name not properly updated '
            assert updated_item.get('description', {}).get('S') == updated_password, f'asset description not properly updated'
            assert updated_item.get('url', {}).get('S') == updated_password, f'asset url not properly updated'
            
        else:
            print("Test skipped (asset Table not found)")

    #asset_DAO must delete an existing asset
    def test_delete_asset(self):
        print('Entering test_delete_asset')
        table = self._get_table()
        if table:
            asset_param = {
                            'name': 'Spaceship sprites',
                            'description': '2D top down spaceship sprites',
                            'url':'http://www.archive.com/68758sfs850/2dSpaceships.zip'
                        }
            asset_id = data_util.create_hash(asset_param['name'])
            asset_item = {
                'id': asset_id,
                'name': asset_param['name'],
                'description': asset_param['description'],
                'url': asset_param['url'],
            }
            table.put_item(Item=asset_item)
            time.sleep(self._SLEEP)

            result = self._dao.delete_asset(asset_id)

            assert result == return_values.SUCCESS,f'Error testing delete asset. Incorrect response'
            response = table.get_item(Key={'id':asset_id})
            assert 'Item' not in response,f'Error testing delete asset. Bad response'
        else:
            printf("Test skipped (asset table not found)")

    def teardown_class(self):
        print('Entering teardown_class')
        self._delete_table()

