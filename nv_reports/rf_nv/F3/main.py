from arm.tools.DC import DCC
from arm.api.forms.formTools import labField, style, label, _div, _field, gridStyle, docTitle

import time

def main(rpc):
    dcls = []
    for k, v in rpc.items():
        dc = DCC()
        dc.js = 'F3/f3.js'
        dc.css = 'F3/f3.css'
        dc.main = _div(**gridStyle('100px 1fr'), children=[
                    label(k),
                    _div(v)
                ])
        dcls.append(dc)
    return dcls
