def wei_to_ether(wei):
    return 1.0 * wei / 10**18


def ether_to_wei(ether):
    return ether * 10**18


def hex_to_dec(x):
    return int(x, 16)


def clean_hex(d):
    return hex(d).rstrip('L')