# -*- coding: utf-8 -*-
'''
Created on 2023

@author: aon24
'''

from arm.tools.DC import well
from arm.tools.first import err
from ..formTools import _fileShow, style, _div, _btnD, _field, _tab, label, labField  # , labelc, _span
from ..classPage import Page
from ..toolbars import toolbar

# from django.contrib.auth.hashers import make_password
# from django.contrib.auth import authenticate
# from django.contrib.auth.models import User
# from django.http import HttpResponse

import json

# *** *** ***


class Profile(Page):

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js']
        self.title = 'Профайл'
        self.dbAlias = 'nv_Profile'
        super().__init__(request)

    # *** *** ***

    # def putData(self, dcUK, buf):
        # try:
        #     if dcUK.cmd == 'testUser':
        #         ls = buf.split('¤')  # buf = 'pk¤oldPass'
        #         pk = ls[0]
        #         if not (pk == dcUK._profilePK or dcUK._staff):
        #             err(f'Permission denied: {dcUK.fullName}', cat=self.form)
        #             return HttpResponse(f'Permission denied: {dcUK.fullName}')
        #
        #         prof = well('profiles', pk)
        #
        #         user = User.objects.get(id=prof.user)
        #         if authenticate(username=user.username, password=ls[1]):
        #             return HttpResponse('OK')
        #         return HttpResponse('Password wrong')
        #
        #     elif dcUK.cmd == 'changeUser':
        #         ls = buf.split('¤')
        #         pk, login, pw = ls
        #         prof = well('profiles', pk)
        #         ln, fn = (prof.full_name + ' ').split(' ')[:2]
        #         user = None
        #         if prof.user:
        #             try:
        #                 user = User.objects.get(id=prof.user)
        #             except User.DoesNotExist:
        #                 pass
        #
        #         if user:
        #             user.username = login
        #             user.password = make_password(pw)
        #             user.save()
        #             act = 'change'
        #         else:
        #             user = User.objects.create(
        #                 username=login,
        #                 password=make_password(pw),
        #                 is_staff=False,
        #                 is_active=True,
        #                 first_name=fn,
        #                 last_name=ln,
        #                 email=prof.email,
        #             )
        #             prof.user = user.id
        #             dc = DC(dbAlias='nv_Profile', unid=prof.id)
        #             dc.doc = prof
        #             if dc.save():
        #                 act = 'registration'
        #             else:
        #                 act = 'Error by saved Profile'
        #         snd(f'{prof.full_name} <=> {login} ({act})', cat='users')
        #         return HttpResponse('OK')
        #     else:
        #         err(f'Unknown cmd: {dcUK.cmd}', cat=self.form)
        #         return HttpResponse(f'PutData for {self.form}. Unknown cmd: {dcUK.cmd}')
        #
        # except Exception as ex:
        #     err(f'PutData (cmd={dcUK.cmd}):{ex}', cat=self.form)
        #     return HttpResponse(f'PutData for {self.form}(cmd={dcUK.cmd}): {ex}')

    # *** *** ***

    def page(self, request):
        tMain = _div(className='tabBodyInner', children=[

            _div(**style(textAlign='center'), children=[
                # _span('Роли ', className='label', **style(display='inline-block')),
                _field('role', 'lbmd', well('role'), **style(display='inline-block', textAlign='left', width=150), placeholder='список'),

                _field('status', 'lbsd', self.status,
                    **style(display='inline-block', width=120, float='right', textAlign='left'),
                    alias=1, placeholder='список',
                ),
                # _span('Статус ', className='label', **style(float='right')),

            ]),
            *labField('ФИО', 'full_name', 'tx'),
            *labField('Спецализация', 'post', 'tx'),
            *labField('телефон', 'phone', 'phone'),
            *labField('e-mail', 'email', 'openLink'),
            *labField('WhatsApp', 'WhatsApp', 'openLink'),
            *labField('telegram', 'telegram', 'openLink'),
            *labField('vk', 'vk', 'openLink'),
            *labField('instagram', 'instagram', 'openLink'),
            *labField('twitter', 'twitter', 'openLink'),
            *labField('facebook', 'facebook', 'openLink'),
            label(),
        ])
        tGroup = _div(className='tabBodyInner', children=[
            *labField('Группы студента', 'student_groups', 'lbmd', '/api/well?clues=allGroups', common=1, name='st_gr'),
            *labField('Группы, в которых он куратор', 'curator_groups', 'lbmd', '/api/well?clues=allGroups', name='cur_gr'),
            # *labField('Группы, в которых преподаватель ведет занятия', 'lector_groups', 'lbmd', '/api/well?clues=allGroups', name='lec_gr'),
            _btnD('платежи', 'payList', **style(width=100, margin='10px auto')),
            _field('curators_FD', 'fd', br=1),
        ])

        genderList = ['мужчина', 'женщина', 'кварцвинил']
        tPerDa = _div(className='tabBodyInner', children=[
            *labField('Дата рождения', 'date_birth', 'dt'),
            *labField('Адрес', 'address', 'tx'),
            *labField('Паспорт', 'passport', 'tx'),
            *labField('Приветствие', 'hello', 'tx'),
            *labField('Пол', 'gender', 'lbsd', genderList),
            # *labField('Ознакомительный семинар', 'invite', 'tx'),
            # *labField('Дата озн. семинара', 'DATE_INVITE', 'dt'),
            *labField('Комментарий', 'notes', 'tx'),

            # _div(name='createUser', **style(margin=10, paddingTop=10, border='0 solid #048', borderTopWidth=1), children=[
            #     labelc('У пользователя нет логина'),
            #     _btnD('Зарегистрировать', 'addUser', **style(width=220, margin='auto')),
            # ]),
            # _div(name='changeUser', **style(margin=10, paddingTop=10, border='0 solid #048', borderTopWidth=1, textAlign='center'), children=[
            #     _span('login: '),
            #     _field('username', 'fd', **style(font='bold 15px Courier', color='#048')),
            #     _btnD('Изменить логин/пароль', 'changeUser', **style(width=220, margin='10px auto')),
            # ]),
        ])
        tPhoto = _div(className='tabBodyInner', children=[
            _div(**style(height='100%', display='grid', gridTemplateRows='1fr auto'), children=[
                _field('photo', 'json', withoutDiv=1, fd=1),
                _fileShow('FILES1_', wl='40mm', label='фото '),
            ])
        ])

        tMore = _div(className='tabBodyInner', children=[
            *labField('Тренинги', 'training', 'lbmd', [], **style(margin=5)),
            *labField('Фестивали', 'fest', 'lbmd', []),
            *labField('Озн.семинар', 'invite', 'lbmd', []),  # '/api/well?clues=invite'),
        ])

        # ***

        tabs = [('Контакты', tMain, 85),
                ('Персон', tPerDa),
                ('Фото', tPhoto, 65),
                ('Группы', tGroup, 70),
                ('Доп', tMore, 60),
        ]

        profile = _tab(width=70, tabs=tabs)  # width - width of headeritem

        hide = [_field(fi, 'fd', fd=1, **style(display='none')) for fi in ['tls', 'fls', 'ils']]

        return self.docPage([profile, *hide], request.dcUK.mode == 'read' and [toolbar.close_])

# *** *** ***

    def queryOpen(self, dcUK):
        if not (dcUK._staff or 'куратор' in dcUK.role):
            dcUK.mode = 'read'

        doc = dcUK.doc

        if dcUK.mode == 'new':
            doc.status = 'active'
            doc.invite = dcUK.invite
            doc.info = dcUK.info
            doc.role = dcUK.role
            doc.STUDENT_GROUPS = dcUK.group.rpartition('|')[0]  # 2024-2/День|76|active

        # elif doc.user:
        #     try:
        #         user = User.objects.get(pk=doc.user)
        #         doc.username = user.username
        #     except Exception as ex:
        #         err(f'queryOpen: get(pk={doc.user})\n{ex}', cat=self.form)
        #         doc.username = f'ERROR: {ex}'

        curators = ''
        for gr in doc.STUDENT_GROUPS.split('\n'):
            if gr:
                grTitle, _, grId = gr.partition('|')
                group = well('groups_groupId', grId)
                curators += f'\n<<C+{grTitle}>> => куратор <<B+{(group and group.curator.partition("|")[0]) or "-"}>>'
        doc.curators_FD = curators

        if doc.FILES1_:
            try:
                js = json.loads(doc.FILES1_)

                pho = _div(**style(
                    backgroundSize='auto 100%',
                    backgroundImage=f'url(/api/xImage?path={js[0]["path"]})',
                    backgroundRepeat='no-repeat'
                    ),
                    children=[
                        _div(doc.full_name, **style(
                            # bottom=10,
                            width='100%',
                            textAlign='center',
                            color='#ffffff',
                            font='bold 20px Arial',
                            textShadow='2px 2px 5px #004488, -2px -2px 5px #004488'
                        ))
                    ])
            except:
                err('json.loads', 'profile-photo')
                pho = _div(doc.full_name)
        else:
            pho = _div(doc.full_name)

        doc.photo = json.dumps([pho], ensure_ascii=False)

        if doc.training not in well('training'):
            doc.tls = ('\n'.join(well('training')) + '\n' + doc.training).strip()
        else:
            doc.tls = '\n'.join(well('training'))

        if doc.fest not in well('fest'):
            doc.fls = ('\n'.join(well('fest')) + '\n' + doc.fest).strip()
        else:
            doc.fls = '\n'.join(well('fest'))

        if doc.invite not in well('invite'):
            doc.ils = ('\n'.join(well('invite')) + '\n' + doc.invite).strip()
        else:
            doc.ils = '\n'.join(well('invite'))

# *** *** ***
    def querySave(self, dcUK):
        return True

