'''
Created on 2023

@author: aon24
'''

from arm.tools.DC import well, swell
from arm.tools.first import err
from arm.api.forms.formTools import _fileShow, style, _div, _btnD, _field, _tabNew, label, \
    labField, _span, _teg
from arm.api.forms.classPage import Page
from arm.api.forms.toolbars import toolbar

import json

# *** *** ***


class Profile(Page):
    '''
    Форма отображает документ в бд nv_c (common.sqlite) таблица nv_c_Profile
    CRM + ЛК
    форма описание профайла
    '''
    perdaFields = 'date_birth,address,passport,notes'.upper().split(',')  # perda

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js']
        self.title = 'Профайл'
        self.dbAlias = 'nv_Profile'
        super().__init__(request)

    # *** *** ***

    def page(self, request):
        fd = not ('куратор' in self._role or self._staff)
        tMain = _div(className='tabBodyInner', children=[

            _div(**style(textAlign='center'), children=[
                _span('Роли ', className='label', **style(display='inline-block')),
                _field('role', 'lbmd', swell('role'), fd=fd, **style(display='inline-block', textAlign='left', width=150), placeholder='список'),
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
            _field('status', 'lbsd', self.status, fd=fd,
                   **style(display='inline-block', width=120, float='right', textAlign='left'),
                   alias=1, placeholder='список',
                   ),
        ])
        tGroup = _div(className='tabBodyInner', children=[
            *labField('Группы пользователя', 'student_groups', 'lbmd', 'cmd=well&clues=allGroups', common=1, fd=fd),
            *labField('Группы, в которых он куратор', 'curator_groups', 'lbmd', 'cmd=well&clues=allGroups', name='cur_gr', fd=fd),
            _btnD('платежи', 'payList', **style(width=100, margin='10px auto', fd=fd)),
            _field('curators_FD', 'fd', br=1),
        ])

        genderList = ['мужчина', 'женщина', 'кварцвинил']
        tPerDa = _div(className='tabBodyInner', children=[
            *labField('Дата рождения', 'date_birth', 'dt', name='perda'),
            *labField('Адрес', 'address', 'tx', name='perda'),
            *labField('Паспорт', 'passport', 'tx', name='perda'),
            *labField('Приветствие', 'hello', 'tx'),
            *labField('Пол', 'gender', 'lbsd', genderList),
            *labField('Комментарий', 'notes', 'tx', name='perda'),
        ])
        tPhoto = _div(className='tabBodyInner', children=[
            _div(**style(height='100%', display='grid', gridTemplateRows='1fr auto'), children=[
                _field('photo', 'json', withoutDiv=1, fd=1),
                _fileShow('FILES1_', wl='40mm', label='фото '),
            ])
        ])

        tMore = _div(className='tabBodyInner', children=[
            *labField('Тренинги', 'training', 'lbmd', [], fd=fd, **style(margin=5)),
            *labField('Фестивали', 'fest', 'lbmd', [], fd=fd),
            *labField('Озн.семинар', 'invite', 'lbmd', [], fd=fd),
            _teg('hr'),
            # labelc('Разрешить новую версию'),
            # _field('cssTheme', 'band', ['Н Е Т|', 'на ПК|pc', 'на моб.|mobile', 'ПК+моб|all'],
            #     recalcText=1, **style(width='auto', margin='auto'))
        ])

        # ***

        tabs = [('Контакты', tMain, 85),
                ('Персон', self._staff and tPerDa, 70),
                ('Фото', tPhoto, 55),
                ('Группы', tGroup, 70),
                ('Доп', tMore, 50),
                ]

        return self.docPage([_tabNew('PR_Table_FD', tabs=tabs)], request.dcUK.mode == 'read' and [toolbar.close_])

# *** *** ***

    def getOldValue(self, r, fv, do):
        if r.dcUK._staff:
            return super().getOldValue(r, fv, do)
        return {k: do.get(k, '') for k in fv if do.get(k, '') != fv[k] and k not in self.perdaFields}

    def queryOpen(self, r):
        dcUK = r.dcUK
        if dcUK.dbAlias == 'nv_Profile':
            if not dcUK._staff:
                if 'куратор' not in dcUK._role:  # не офис и не куратор
                    dcUK.unid = dcUK._profilePK
                else:
                    pass

        dcUK.unid = dcUK.unid or dcUK._profilePK

        doc = dcUK.doc

        if not r.dcUK._staff:  # hide and clean perda
            for k in self.perdaFields:
                doc[k] = ''

        if dcUK.mode == 'new':
            doc.status = 'active'
            doc.invite = dcUK.invite
            doc.info = dcUK.info
            doc.role = dcUK.role
            doc.STUDENT_GROUPS = dcUK.group.rpartition('|')[0]  # 2024-2/День|76|active

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
                            width='100%',
                            textAlign='center',
                            color='#ffffff',
                            font='bold 20px Arial',
                            textShadow='2px 2px 5px #004488, -2px -2px 5px #004488'
                        ))
                    ])
            except Exception:
                err('json.loads', 'profile-photo')
                pho = _div(doc.full_name)
        else:
            pho = _div(doc.full_name)

        doc.photo = json.dumps([pho], ensure_ascii=False)

        if doc.training not in swell('training'):
            doc.tls_fd = ('\n'.join(swell('training')) + '\n' + doc.training).strip()
        else:
            doc.tls_fd = '\n'.join(swell('training'))

        if doc.fest not in swell('fest'):
            doc.fls_fd = ('\n'.join(swell('fest')) + '\n' + doc.fest).strip()
        else:
            doc.fls_fd = '\n'.join(swell('fest'))

        if doc.invite not in swell('invite'):
            doc.ils_fd = ('\n'.join(swell('invite')) + '\n' + doc.invite).strip()
        else:
            doc.ils_fd = '\n'.join(swell('invite'))

# *** *** ***
