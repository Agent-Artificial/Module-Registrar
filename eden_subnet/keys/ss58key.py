from communex.compat.key import Ss58Address


def get_ss58_key(keyname: str):
    return Ss58Address(keyname)


    