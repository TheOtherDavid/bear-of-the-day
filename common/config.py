import os

def verify_environment():
    """
    Verify environment variables. If a required environment variable is not set, raise an exception.
    """
    variables = {
        'DEBUG_MODE': os.getenv('DEBUG_MODE', 'False'),
        'AWS_BUCKET_NAME': os.getenv('AWS_BUCKET_NAME'),
        'RECIPIENTS': os.getenv('RECIPIENTS'),
        'OPENAI_API_KEY': os.getenv['OPENAI_API_KEY'],
        'SENDER_EMAIL': os.getenv['SENDER_EMAIL'],
        'SENDER_PASS': os.getenv['SENDER_PASS']
        # add any other environment variables you need here
    }

    for var_name, value in variables.items():
        if value is None:
            raise Exception(f'Missing required environment variable: {var_name}')

    return variables