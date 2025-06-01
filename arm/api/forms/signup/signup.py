'''
Created on 2025

@author: aon24
'''
from arm.api.forms.formTools import style, _div, _form, _input, _teg, _btnD, _field, _a, _br
from arm.api.forms.classPage import Page
from arm.tools.DC import config

from django.middleware.csrf import get_token


class signup(Page):
    title = 'Sova'
    _VIEW_ = 1
    noCaching = True

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = f'/api/jsv?forms/{self.form}/{self.form}.js'

        super().__init__(request)

    # ***

    def page(self, request):
        body = _div(
            **style(fontSize=40),
            children=[
                _div(**style(padding=5),
                  children=[
                    _div('Введите номер телефона:'),
                    _div(**style(display='flex', justifyContent='space-evenly', alignItems='center'),
                      children=[
                        _field('phone', 'phone', noBtn=1, autoFocus=True, **style(width=190, fontSize=20)),
                        _btnD('Продолжить', 'proceed',
                              **style(height=40, padding=10, fontSize=24, margin='auto'))
                    ])
                ]),
                _form(
                    id='signup', name='signup',
                    **style(border='0 solid #fff', borderTopWidth=2, width='100%', textAlign='left'),
                    method='post', action='/api/signup/', children=[
                    _div(children=[_input(type="hidden",
                        name="csrfmiddlewaretoken",
                        value=f'{get_token(request)}'
                    )]),

                    _div(children=[
                        _div('Логин:'),
                        _input(**style(fontSize=35, width='calc(100% - 10px)', paddingLeft=5),
                            type="text",
                            name="username",
                            required=True,
                            placeholder="Логин пользователя",
                            autoComplete="username",
                            minLength="1",
                            maxLength="50",
                            id='id_login',
                        )
                    ]),
                    _div(**style(marginTop=20), children=[
                        _div('Пароль:'),
                        _input(**style(fontSize=35, width='calc(100% - 10px)', paddingLeft=5),
                            type="password",
                            name="password1",
                            required=True,
                            placeholder="Пароль",
                            autoComplete="new-password",
                            minLength=1,
                        )
                    ]),
                    _div(children=[
                        _div('Пароль (еще раз):'),
                        _input(**style(fontSize=35, width='calc(100% - 10px)', paddingLeft=5),
                            type="password",
                            name="password2",
                            required=True,
                            placeholder="Пароль (еще раз)",
                            autoComplete="new-password",
                            minLength=1,
                        )
                    ]),

                    _div(children=[
                        _div('Адрес эл. почты:', **style(fontSize=30, marginTop=20)),
                        _input(**style(font='normal 30px/2 Courier', width='calc(100% - 10px)', paddingLeft=5),
                            type="text",
                            name="email",
                            required=True,
                            placeholder="Адрес эл. почты",
                            autoComplete="email",
                            id='email',
                        )
                    ]),

                        _div(**style(lineHeight='10px'), children=[
                            _input(type="checkbox", id="scales", name="scales", required=True),
                            _teg('label', 'согласие на обработку персональных данных', **style(fontSize=20), htmlFor="scales")
                    ]),
                    _input(type="hidden", name="first_name", id="first_name"),  # И.О.
                    _input(type="hidden", name="last_name", id="last_name"),  # phone

                    _div(**style(textAlign='center', padding='15px 0', border='0 solid #fff', borderBottomWidth=2), children=[

                        _btnD('Отправить', 'submit', f'signup',
                            **style(width=170, height=50, padding=10, fontSize=24, margin='auto'),
                        ),

                        # _input(**style(border=0, height=50, padding=10, fontSize=24, margin='auto'),
                        #        className='rsvTop', type="submit", form='signup'), +7(884) 729-09-99
                    ]),

                    _div(**style(lineHeight='12px', textAlign='center', padding=10, border='0 solid #fff', borderBottomWidth=2), children=[
                    _a('Политика в отношении обработки персональных данных',
                       **style(fontSize=20), target='_blank',
                       href='/static/personal-policy.html'),
                    ]),
                    _div(**style(lineHeight='12px', textAlign='center', padding=10, border='0 solid #fff', borderBottomWidth=2), children=[
                    _a('Согласие на обработку персональных данных',
                       **style(fontSize=20), target='_blank',
                       href='/static/personalData.html'),
                    ]),
                    _div(**style(lineHeight='12px', textAlign='center', padding=10), children=[
                    _a('Пользовательское соглашение',
                       **style(fontSize=20), target='_blank',
                       href='/static/user-agreement.html'),
                    ]),
                ]),  # end form

        ])

        st = {
            'margin': 'auto',
            'height': '100%',
            'overflow': 'auto',
            'backgroundImage': 'url(/static/image/nvbgGold.jpeg)',
            'backgroundSize': '100% 100%'
        }
        return _div(focus='auto', style=st,
            children=[
                _teg('fieldset',
                  **style(width='90%', margin='auto',
                        background='linear-gradient(0deg, #ffffff20, #ffffffff)',
                        paddingTop=3, border='3px solid #fff'),
                  children=[
                    _teg('legend', f'\xa0 {config.orgName} \xa0', **style(borderRadius='50%', background='#fff', fontSize=24, textAlign='center')),
                    body
                ])
            ])
        
    # *** *** ***

