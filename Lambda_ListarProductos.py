import boto3
import json
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    print(event)
    # Entrada (json)
    body = event['body']
    tenant_id = body['tenant_id']

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
    response = table.query(
        KeyConditionExpression=Key('tenant_id').eq(tenant_id)
    )
    items = response['Items']
    # Convierte Decimal (numeros de DynamoDB) para que se pueda devolver como JSON
    items = json.loads(json.dumps(items, default=str))

    # Salida (json)
    return {
        'statusCode': 200,
        'cantidad': len(items),
        'productos': items
    }
