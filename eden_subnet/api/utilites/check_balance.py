from loguru import logger


def check_balance(values, balance_type):
    balance_value = 0
    try:
        balance_value = values[balance_type]
    except Exception as e:
        logger.error(e)
    return balance_value