'''
Created on 2025

@author: aon24
'''
from arm.tools.DC import well, config
from arm.api.forms.formTools import style, _div, _btnD, _a, _form, _input, labelc, _button, _teg
from arm.api.forms.classPage import Page
from arm.tools.common import cleanPhone
from arm.tools.httpMisc import nvResponse

from django.middleware.csrf import get_token


class login(Page):
    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = f'/api/jsv?forms/{self.form}/{self.form}.js'
        self.title = 'Sova'
        self.noCaching = True

        super().__init__(request)


    # ***

    def getData(self, dcUK):
        if dcUK.cmd == 'checkPhone':
            phone = cleanPhone(dcUK.phone)
            prof = well('profilesByPhone', phone)
            if prof:
                if prof.user_id:
                    return 'exist'
                return f'{prof.email.partition(",")[0]}|{prof.full_name.partition(" ")[2]}'
            else:
                return 'not found'
        else:
            return nvResponse(f'Invalid cmd {dcUK.cmd}', 400)

    # ***

    def page(self, request):
        body = [
            _form(
                id='login',
                **style(width='100%', textAlign='left'),
                method='post', action='/accounts/login/', children=[
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
                        autoFocus=True,
                        id='l',
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
                        _button('Войти', 'submit', f'login', className='rsvTop',
                            **style(width=150, height=50, padding=10, fontSize=24, margin='auto'),
                        )
                ]),

            ]),  # end form

            labelc('Неверный логин / пароль', name='err', **style(fontSize=18, color='red')),

            _div(**style(fontSize=30, textAlign='center', marginTop=20),
                children=[
                    _a('Забыли пароль?', href='/accounts/password/reset/')
            ]),

            _div(**style(padding=15, border='0 solid #fff', borderTopWidth=2, margin=10),
                children=[
                    _div(**style(height=50, display='flex', justifyContent='space-evenly'), children=[
                        _btnD('Зарегистрироваться', 'reg', **style(height=50, padding=10, fontSize=24))  # className='btnArm',
                    ])
            ]),
        ]

        st = {
            'margin': 'auto',
            'height': '100vh',
            'overflow': 'auto',
            'paddingTop': 50,
            'backgroundImage': 'url("/static/images/nvbg.jpeg")',
            'backgroundSize': '100% 100%'
        }
        return _div(className='bg52', focus='auto', style=st, children=[
            _div(**style(margin='auto', fontSize=40, width='90%', maxWidth=500), children=[
                _teg('fieldset',
                    **style(
                            backgroundImage='url("/static/images/nvbgGreen.jpeg")',
                            backgroundSize='100% 100%',
                            border='3px solid #fff'),
                    children=[
                        _teg('legend', f'\xa0 {config.orgName} \xa0', **style(margin='auto', borderRadius=5, background='#fff', fontSize=24, textAlign='center')),
                        *body
                ])
            ])
        ])

    # *** *** ***

    def queryOpen(self, r):
        r.dcUK.doc.err_fd = r.dcUK.error

