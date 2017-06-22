# -*- coding: utf-8 -*-


def joinPath(split, arrStr):
    result = ''
    flat=False
    for str in arrStr:
        if flat:
            result+=split
        result += str
        flat=True
    return result
