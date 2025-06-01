from tester import Tester
import json

tester = Tester()

def main(tester):
    
    # 1: Login
    print('Login...')
    email = 'john.doe+10@intuitus.ai'
    password = 'Banana123'
    access_token = tester.get_access_token(email, password)
    print(f'Access token: {access_token[:20]}...\n\n')

    # 2: Create warehouse
    print('Create warehouse...')
    name = 'Test Warehouse'
    description = 'Test Description'
    warehouse = tester.create_warehouse(name, description, access_token)
    print(f'Warehouse:\n{json.dumps(warehouse, indent=4)}\n\n')
    warehouse_id = warehouse['id']

    # 3: Get warehouse
    print('Get warehouse...')
    warehouse = tester.get_warehouse(warehouse_id, access_token)
    print(f'Warehouse:\n{json.dumps(warehouse, indent=4)}\n\n')

    # 4: Create dataset
    print('Create dataset...')
    name = 'Test Dataset'
    description = 'Test Description'
    data = b"id,name,value\n1,test,100\n2,test2,200"
    dataset = tester.create_dataset(warehouse_id, name, description, access_token, data)
    print(f'Dataset Created:\n{json.dumps(dataset, indent=4)}\n\n')

    # 5: Query warehouse
    print('Query warehouse...')
    result = tester.query_warehouse(warehouse_id, access_token)
    print(f'Result:\n{json.dumps(result, indent=4)}\n\n')

    # 6: Get dataset
    # print('Get dataset...')
    # dataset = tester.get_dataset(dataset['id'], access_token)
    # print(f'Dataset:\n{json.dumps(dataset, indent=4)}\n\n')

    # 7: Get datasets
    # print('Get datasets...')
    # datasets = tester.get_datasets(warehouse_id, access_token)
    # print(f'Datasets ({len(datasets)}):\n{json.dumps(datasets, indent=4)}\n\n')

    # 8: Create another dataset
    print('Create another dataset...')
    name = 'Test Dataset 2'
    description = 'Test Description 2'
    data = b"id,name,value\n1,test,600\n2,test2,700"
    dataset = tester.create_dataset(warehouse_id, name, description, access_token, data)
    print(f'Dataset Created:\n{json.dumps(dataset, indent=4)}\n\n')

    # 9: Query warehouse
    print('Query warehouse...')
    result = tester.query_warehouse(warehouse_id, access_token)
    print(f'Result:\n{json.dumps(result, indent=4)}\n\n')

    # 10: Update dataset
    print('Update dataset...')
    data = b"id,name,value\n1,test,600\n2,test2,1000"
    dataset = tester.update_dataset(dataset['id'], access_token, data)
    print(f'Dataset Updated:\n{json.dumps(dataset, indent=4)}\n\n')

    # 9: Query warehouse
    print('Query warehouse...')
    result = tester.query_warehouse(warehouse_id, access_token)
    print(f'Result:\n{json.dumps(result, indent=4)}\n\n')

    # 11: Get dataset
    print('Get dataset...')
    dataset = tester.get_dataset(dataset['id'], access_token)
    print(f'Dataset:\n{json.dumps(dataset, indent=4)}\n\n')

    # 12: Get warehouse
    print('Get warehouse...')
    warehouse = tester.get_warehouse(warehouse_id, access_token)
    print(f'Warehouse:\n{json.dumps(warehouse, indent=4)}\n\n')

    # 13: Delete dataset
    print('Delete dataset...')
    tester.delete_dataset(dataset['id'], access_token)
    print('Dataset deleted\n\n')

    # 14: Get Deleted Dataset
    print('Get Deleted Dataset...')
    try:
        dataset = tester.get_dataset(dataset['id'], access_token)
        print(f'Dataset:\n{json.dumps(dataset, indent=4)}\n\n')
    except Exception as e:
        print(f'Error: {e}\n\n')

    # 15: Query warehouse
    print('Query warehouse...')
    result = tester.query_warehouse(warehouse_id, access_token)
    print(f'Result:\n{json.dumps(result, indent=4)}\n\n')

main(tester)