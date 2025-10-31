'''
Created on 2025

@author: aon24
'''
from arm.api.forms.formTools import style, _div, _btnD
from arm.tools.DC import well

# *** *** ***


def sstButtons(sst, sgr, curator=''):
    if sst.pay_s:
        pay_s = ' fv2yes'
    else:
        pay_s = ''

        if sst.form == 'SessionGr':
            return _div('информация', **style(width=120), className='btnIcon mBtn fv2 fv2yes', title='общая группа'),

        begin = sgr.DATE_BEGIN  # only year-mounth
        for pay in well('payments_profile', sst.pref):
            if pay.sstId == sst.id and pay.SUMMA:
                pay_s = ' fv2yes'
                break
            elif pay.t1 == begin and pay.SUMMA:
                pay_s = ' fv2yes'
                break

    try:  # feedback
        if well('profiles', sst.pref).user:
            if any([sst[x] for x in sst.keys() if x.startswith('ASSLEC')]):
                bf = ' fv2yes'
            else:
                bf = ''
            btnFB = _div('ОС', className=f'btnIcon mBtn fv2{bf}', title='обратная связь')

        else:  # ×
            btnFB = _div('❌', **style(color='red', width=30, textAlign='center'), title='не зарегистрировался')
    except Exception:
        btnFB = _div('ER', **style(color='red', width=30, textAlign='center'), title='сбой профайла')

    if sst.was_s:
        was = _btnD('✔️', curator and "setField", f'was_s|{sst.id}|1', className='btnIcon mBtn fv2 fv2yes', title='был на занятии')
    else:
        was = _btnD('-', curator and "setField", f'was_s|{sst.id}|', className='btnIcon mBtn fv2', title='пропустил')

    pay = None
    if sgr.nvEvent.startswith('P'):  # Практикум
        b4 = _btnD('К', curator and "setField", f'consultant_s|{sst.id}|{sst.consultant_s}',
                   className=f'btnIcon mBtn fv2{sst.consultant_s and " fv2yes"}', title='консультант')
        pay = _div('\xa0', className='btnEmpty')
    elif sgr.nvEvent == '1':
        b4 = _btnD('Э', 'setField', f'esse_s|{sst.id}|{sst.esse_s}', className=f'btnIcon mBtn fv2R{sst.esse_s and " fv2yesR"}', title='эссе')
    else:
        b4 = _div('\xa0', className='btnEmpty')

    pay = pay or _btnD('Р', curator and "newPay", f'{sgr.id}|{sst.id}|{sst.pref}', className=f'btnIcon mBtn fv2{pay_s}', title='оплата')

    return [
        pay,
        _btnD('Д', curator and "setField", f'allow_s|{sst.id}|{sst.allow_s}', className=f'btnIcon mBtn fv2{sst.allow_s and " fv2yes"}', title='допуск'),
        was,  # visited
        b4,
        btnFB if sgr.nvEvent == '1' else _div('\xa0', className='btnEmpty'),  # feedback
    ]
