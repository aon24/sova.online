'''
Created on 12025

@author: aon24
'''
from arm.tools.DC import well
from arm.api.forms.formTools import style, _div, _btnEdit, gridStyle, _btnView


def paymentsList(dcUK):
    payList = []
    for pay in well('payments_profile', dcUK.showLK_id or dcUK._profilePK):
        ch = pay.cash[:1].upper()
        date = _div(f"{pay.D('pay_date')}\n{ch}: {pay.summa}",
                    className='mCell', s2=1, br=1, **style(color='#036'))
        if pay.t1:
            t12 = f'{pay.D("t1")} - {pay.D("t2")}' if pay.t2 else pay.D('t1')
        else:
            t12 = ''
        btnV = _btnView('previewArm', f'form=Payment&dbAlias=nv_Payment&unid={pay.id}&mode=preview&title=Оплата')
        title = _div(f"{pay.PURPOSE}\n{t12}",
                     className='mCell', s2=1, br=1, **style(letterSpacing=1))
        row = _div(**gridStyle('90px 1fr 33px', border='0 solid #aaa', borderBottomWidth=1),
                   children=[date, title, btnV])

        payList.append(row)

    return payList

# *** *** ***


def analyst(dcUK):
    # getView()
    return _div('')


def reportList(dcUK):
    mainDocs = []
    ids = []
    dbAlias = 'nv_reports_Report'
    dba = dcUK.dba

    for m in well(dba):
        if m.form != 'report':
            continue

        pk = m.id

        if dcUK.title not in ['Все собранные отчеты', m.title]:
            continue

        ids.append(pk)
        title = _div(f"{m.docNo}. {m.title}\n{m.starting_time} => {m.end_time}",
                     className='mCell', s2=1, br=1,
                     **style(width='100%', paddingLeft=2, letterSpacing=1))

        btnV = _btnEdit('cmdEdit', f'unid={pk}&dbAlias={dbAlias}&form=report')

        row = _div(**style(display='grid', placeItems='center start', gridTemplateColumns='1fr auto'),
                   children=[title, btnV])
        mainDocs.append([pk, row])

    refsDocs = {}
    for o in well(dba):
        if o.form != 'html' or o.ref not in ids:
            continue

        refsDocs[o.ref] = refsDocs.get(o.ref, [])
        refsDocs[o.ref].append([o.id, _div(o.title or '-', className='rCell', **style(marginLeft=20, width='100%'))])

    return {'mainDocs': mainDocs, 'refsDocs': refsDocs}

    
