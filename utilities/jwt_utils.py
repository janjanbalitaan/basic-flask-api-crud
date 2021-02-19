@jwt.unauthorized_loader
def unauthorized_callback(callback):
    return {
        'status': 'error',
        'message': 'The request authorization has invalid bearer token to enter kaysiao application premises.'
    }, 401

@jwt.expired_token_loader
def expired_token_callback(callback):
    return {
        'status': 'error',
        'message': 'The bearer token has already expired. Please try to login again.'
    }, 401

@jwt.invalid_token_loader
def invalid_token_callback(callback):
    return {
        'status': 'error',
        'message': 'The request authorization has invalid bearer token to enter kaysiao application premises.'
    }, 401

@jwt.needs_fresh_token_loader
def fresh_token_callback(callback):
    return {
        'status': 'error',
        'message': 'The request authorization has invalid bearer token to enter kaysiao application premises.'
    }, 401

@jwt.needs_fresh_token_loader
def fresh_token_callback(callback):
    return {
        'status': 'error',
        'message': 'The bearer token has been revoked. Please try to login again.'
    }, 401

@jwt.user_loader_error_loader
def user_loader_error_callback(callback):
    return {
        'status': 'error',
        'message': 'The request authorization has invalid bearer token to enter kaysiao application premises.'
    }, 401

@jwt.claims_verification_failed_loader
def claim_verification_error_callback(callback):
    return {
        'status': 'error',
        'message': 'The request authorization has invalid bearer token to enter kaysiao application premises.'
    }, 401