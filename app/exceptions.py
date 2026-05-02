from fastapi import HTTPException, status

class CustomException(HTTPException):
    def __init__(self, status_code: int, detail: str, error_code: str):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code

def user_not_found():
    return CustomException(status.HTTP_404_NOT_FOUND, "User not found", "USER_NOT_FOUND")

def invalid_credentials():
    return CustomException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials", "INVALID_CREDENTIALS")

def user_inactive():
    return CustomException(status.HTTP_403_FORBIDDEN, "User is inactive", "USER_INACTIVE")

def unauthorized():
    return CustomException(status.HTTP_401_UNAUTHORIZED, "Could not validate credentials", "UNAUTHORIZED")

def forbidden():
    return CustomException(status.HTTP_403_FORBIDDEN, "Not enough permissions", "FORBIDDEN")

def product_not_found():
    return CustomException(status.HTTP_404_NOT_FOUND, "Product not found", "PRODUCT_NOT_FOUND")

def insufficient_stock():
    return CustomException(status.HTTP_400_BAD_REQUEST, "Insufficient stock", "INSUFFICIENT_STOCK")

def insufficient_balance():
    return CustomException(status.HTTP_400_BAD_REQUEST, "Insufficient wallet balance", "INSUFFICIENT_BALANCE")

def invalid_coupon():
    return CustomException(status.HTTP_400_BAD_REQUEST, "Invalid coupon", "INVALID_COUPON")

def empty_cart():
    return CustomException(status.HTTP_400_BAD_REQUEST, "Cart is empty", "EMPTY_CART")

def order_not_found():
    return CustomException(status.HTTP_404_NOT_FOUND, "Order not found", "ORDER_NOT_FOUND")

def transaction_not_found():
    return CustomException(status.HTTP_404_NOT_FOUND, "Transaction not found", "TRANSACTION_NOT_FOUND")
