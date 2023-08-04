def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def split(l, n):
    return list(chunks(l, n))


def value_to_float(x):
    if type(x) == float or type(x) == int:
        return x
    if 'K' in x:
        if len(x) > 1:
            return float(x.replace('K', '')) * 10**3
        return 10**3
    if 'M' in x:
        if len(x) > 1:
            return float(x.replace('M', '')) * 10**6
        return 10**6
    if 'B' in x:
        if len(x) > 1:
            return float(x.replace('B', '')) * 10**9
        return 10**9
    return float(x)
