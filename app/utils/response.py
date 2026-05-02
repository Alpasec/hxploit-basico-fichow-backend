from typing import Any, Dict

def success_response(data: Any = None, message: str = "Operation completed successfully") -> Dict[str, Any]:
    response = {
        "success": True,
        "message": message,
        "data": data if data is not None else {}
    }
    return response

def error_response(error_code: str, message: str) -> Dict[str, Any]:
    return {
        "success": False,
        "message": message,
        "error": error_code
    }
