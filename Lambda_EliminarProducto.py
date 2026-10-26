import boto3
import json

def lambda_handler(event, context):
    print(event)
    # Entrada (json)
    body = event['body']
    tenant_id = body['tenant_id']
    producto_id = body['producto_id']

    # Inicio - Proteger el Lambda
    token = event['headers']['Authorization']
    lambda_client = boto3.client('lambda')
    payload_string = '{ "token": "' + token +  '" }'
    invoke_response = lambda_client.invoke(FunctionName="ValidarTokenAcceso",
                                           InvocationType='RequestResponse',
                                           Payload = payload_string)
    response = json.loads(invoke_response['Payload'].read())
    print(response)
    if response['statusCode'] == 403:
        return {
            'statusCode' : 403,
            'status' : 'Forbidden - Acceso No Autorizado'
        }
    # Fin - Proteger el Lambda

    # Proceso
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_productos')
    response = table.delete_item(
        Key={
            'tenant_id': tenant_id,
            'producto_id': producto_id
        },
        ReturnValues='ALL_OLD'
    )
    if 'Attributes' not in response:
        return {
            'statusCode': 404,
            'body': 'Producto no existe'
        }
    producto = json.loads(json.dumps(response['Attributes'], default=str))

    # Salida (json)
    return {
        'statusCode': 200,
        'body': 'Producto eliminado',
        'producto': producto
    }
