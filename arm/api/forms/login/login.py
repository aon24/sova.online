'''
Created on 2025

@author: aon24
'''
from arm.tools.DC import well, toWell, config
from arm.api.forms.formTools import style, _div, _btnD, _a, _form, _input, _teg
from arm.api.forms.classPage import Page
from arm.tools.common import generate_cv_code, cleanPhone
from arm.settings import ALLOWED_HOSTS
from arm.tools.httpMisc import nvResponse

from django.middleware.csrf import get_token

import uuid
import re


class login(Page):
    def __init__(self, form):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = f'/api/jsv?forms/{self.form}/{self.form}.js'
        self.title = 'Sova'
        self.noCaching = True

        super().__init__(form)


    # ***

    def getData(self, dcUK):
        if dcUK.cmd == 'checkPhone':
            phone = cleanPhone(dcUK.phone)
            prof = well('profilesByPhone', phone)
            if prof:
                if prof.user_id:
                    return 'exist'
                return f'{prof.email.partition(",")[0]}|{(prof.full_name + " ").partition(" ")[2]}'
            else:
                return 'not found'
        else:
            return nvResponse(f'Invalid cmd {dcUK.cmd}', 400)

    # ***

    def page(self, request):
        url = 'https://id.vk.com/authorize'
        state = uuid.uuid4().hex
        toWell(state, 'vkState')

        param = '&'.join([
            f'response_type=code',
            f'client_id={config.vk_app_id}',
            f'redirect_uri=https://{ALLOWED_HOSTS[0]}/api/vkcallback/',
            f'state={state}',
            f'code_challenge={generate_cv_code()}',  # возвращает code_challenge и сохраняет toWell(code_verifier, 'code_verifier')
            f'code_challenge_method=s256',
            'scope=friends groups',
        ])
        vkAuth = f'{url}?{param}'

        body = [
            _form(
                id='login',
                **style(width='100%', textAlign='left'),
                method='post', action="/accounts/login/", children=[
                _div(children=[_input(type="hidden",
                    name="csrfmiddlewaretoken",
                    value=f'{get_token(request)}'
                )]),
                _div(children=[
                    _div('Логин'),
                    _input(**style(fontSize=40, width='calc(100% - 10px)'),
                        type="text",
                        name="login",
                        required=True,
                        placeholder="Логин пользователя",
                        autoComplete="username",
                        autoFocus=True
                    )
                ]),
                _div(children=[
                    _div('Пароль'),
                    _input(**style(fontSize=40, width='calc(100% - 10px)'),
                        type="password",
                        name="password",
                        required=True,
                        id="password",
                        placeholder="Пароль",
                        autoComplete="password",
                    )
                ]),
                _div(**style(textAlign='center', padding='15px 0 25px 0'),
                    children=[
                        _input(**style(border=0, height=50, padding=10, fontSize=24, margin='auto'),
                            className='rsvTop', value='Войти', type="submit", form='login'
                        )
                ]),

            ]),  # end form

            _div(**style(fontSize=30, textAlign='center', marginTop=30),
                children=[
                    _a('Забыли пароль?', href='/accounts/password/reset/')
            ]),

            _div(**style(padding=15, border='0 solid #fff', borderTopWidth=2, margin=10),
                children=[
                    # _div('Первый раз?', **style(fontSize=30)),
                    _div(**style(height=50, display='flex', justifyContent='space-evenly'), children=[
                        _btnD('Зарегистрироваться', 'reg', **style(height=50, padding=10, fontSize=24))  # className='btnArm',
                    ])
            ]),
        ]  # end body
                #
                # _div(**style(border='0 solid #aaa', borderTopWidth=2, textAlign='center', display='flex', justifyContent='space-evenly', padding='10px 0', marginTop=20),
                #     children=[
                #         _a('', href=vkAuth,  # '/accounts/vk/login/',
                #             **style(display='block', width=60, height=60,
                #                 backgroundSize='contain', backgroundRepeat='no-repeat', backgroundImage='url(/static/images/icons8-vk-60.png)')),
                #         _a('Я', href='/accounts/yandex/login/',
                #             **style(display='block', height=60, width=60,
                #                 font='normal 40px/1.5 Times',
                #                 backgroundColor='#F8604A',
                #                 borderRadius='50%',
                #                 color='white',
                #                 textDecoration='none',
                #             )),
                #
                # ]),

        st = {
            'margin': 'auto',
            'height': '100vh',
            'overflow': 'auto',
            'paddingTop': 50,
            'backgroundImage': 'url(/static/images/nvbg.jpeg)',
            'backgroundSize': '100% 100%'
        }
        return _div(className='bg52', focus='auto', style=st, children=[
            _div(**style(margin='auto', fontSize=40, width='90%', maxWidth=500), children=[
                _teg('fieldset',
                    **style(
                            backgroundImage='url(/static/images/nvbgGreen.jpeg)',
                            backgroundSize='100% 100%',
                            border='3px solid #fff'),
                    children=[
                        _teg('legend', f'\xa0 {config.orgName} \xa0', **style(borderRadius=5, background='#fff', fontSize=24, textAlign='center')),
                        *body
                ])
            ])
        ])
    # *** *** ***

    # def queryOpen(self, request):
    #     request.dcUK.doc.phone = '+7(921) 571-73-98'

