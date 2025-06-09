'''
Created on 2025

@author: aon24
'''
from arm.api.forms.formTools import style, _div, _form, _input, _button
from django.middleware.csrf import get_token
import json

# *** *** ***


def login2d_fd(request):
    return [
        _form(
            id='login',
            method='post', action='/accounts/login/', children=[
            _div(children=[_input(type="hidden",
                name="csrfmiddlewaretoken",
                value=f'{get_token(request)}'
            )]),
            _div(**style(fontSize=20, width='80%', margin=15), children=[
                _div('Логин'),
                _input(**style(fontSize=20, width='100%'),
                    id="login2d",
                    type="text",
                    name="login",
                    required=True,
                )
            ]),
            _div(**style(fontSize=20, width='80%', marginLeft=15), children=[
                _div('Пароль'),
                _input(**style(fontSize=20, width='100%'),
                    type="password",
                    name="password",
                    id="password",
                    required=True,
                )
            ]),
            _div(**style(textAlign='center', padding='15px 0 25px 0'),
                children=[
                    _button('Войти', 'submit', f'login', className='rsvTop',
                        **style(width=150, height=50, padding=10, fontSize=24, margin='auto'),
                    )
            ]),
    
        ]),  # end form
    ]

# *** *** ***

def getField(xName, request):
    if xName == 'login2d_fd':
        return json.dumps(login2d_fd(request), ensure_ascii=False)
    else:
        return ''





