import boto3
import log

logger = log.logger()

secret_client = boto3.client('secretsmanager')


def get_secret(secret_name: str):
    try:
        get_secret_value_response = secret_client.get_secret_value(
            SecretId=secret_name,
        )
        logger.info('Secret retrieved successfully.')
        return get_secret_value_response['SecretString']
    except Exception as e:
        logger.error(f"An unknown error occurred: {str(e)}.")
        raise
