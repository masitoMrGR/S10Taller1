import boto3
import json

def lambda_handler(event, context):
    print(event)
    # Entrada (json)
    body = event['body']
    tenant_id = body['tenant_id']
    producto_id = body['producto_id']
    # Todo lo que no sea clave se considera "dato a modificar"
    datos = {}
    for campo in body:
        if campo != 'tenant_id' and campo != 'producto_id':
            datos[campo] = body[campo]

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

    if len(datos) == 0:
        return {
            'statusCode': 400,
            'body': 'No se enviaron datos a modificar'
        }

    # Proceso
    # Arma: SET #c0 = :v0, #c1 = :v1, ...
    update_expression = 'SET '
    nombres = {}
    valores = {}
    i = 0
    for campo in datos:
        if i > 0:
            update_expression += ', '
        update_expression += '#c' + str(i) + ' = :v' + str(i)
        nombres['#c' + str(i)] = campo
        valores[':v' + str(i)] = datos[campo]
        i += 1

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_productos')
    try:
        response = table.update_item(
            Key={
                'tenant_id': tenant_id,
                'producto_id': producto_id
            },
            UpdateExpression=update_expression,
            ExpressionAttributeNames=nombres,
            ExpressionAttributeValues=valores,
            ConditionExpression='attribute_exists(producto_id)',
            ReturnValues='ALL_NEW'
        )
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return {
            'statusCode': 404,
            'body': 'Producto no existe'
        }
    producto = json.loads(json.dumps(response['Attributes'], default=str))

    # Salida (json)
    return {
        'statusCode': 200,
        'producto': producto
    }
