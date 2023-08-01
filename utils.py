def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def split(l, n):
    return list(chunks(l, n))


def cells_on_row(row): 
    return row[0] if len(row) > 0 else None