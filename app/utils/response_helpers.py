from flask import jsonify


def success_response(message, data=None, status_code=200):
    """
    Standardize successful JSON responses.

    Args:
        message (str): Success message.
        data (dict, optional): Data to include in the response.
        status_code (int, optional): HTTP status code.

    Returns:
        tuple: Flask Response object and status code.
    """
    response = {"message": message}
    if data is not None:
        response.update(data)
    return jsonify(response), status_code


def error_response(error, status_code=400):
    """
    Standardize error JSON responses.

    Args:
        error (str or dict): Error message or details.
        status_code (int, optional): HTTP status code.

    Returns:
        tuple: Flask Response object and status code.
    """
    return jsonify({"error": error}), status_code
