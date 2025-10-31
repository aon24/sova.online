'''
Created on 2020.

@author: aon
'''
from arm.api.forms.formTools import style, _div, _field, _btnD, labell, gridStyle, labelc
from arm.api.forms.classPage import Page
from arm.tools.DC import well
from arm.api.forms.toolbars import toolbar
from arm.tools.first import err
from arm.tools.common import today

import json
import importlib
import traceback

# *** *** ***


class arm_review(Page):
    '''
    Форма для показа сводки (быстрый отчет) в ЛК студента или куратора
    Todo: сделать для преподавателя
    '''
    _VIEW_ = 1  # чтобы не пытался сохпанить
    openMax = _btnD('ОТКРЫТЬ СВОДКУ', 'openMax', select=1, className='btnClose')

    def __init__(self, request):
        self.title = 'colors'
        self.path, _, self.form = getattr(self, '__module__', '').rpartition('.')
        self.module_rw = 'curator_rw'
        self.jsCssUrlEdit = ['/api/jsv?forms/arm_review/review.css', f'/api/jsv?forms/{self.form}/{self.form}.js']
        self.moduleList = [
            'Допуск|allow_s',
            'Был|was_s',
            'Оплата|pay_s',
            'Обр.св.|os_s',
            'Эссе|esse_s',
            'К-т|consultant_s']
        super().__init__(request)

    # ***

    def getData(self, dcUK):
        if dcUK.cmd == 'startJob':
            path = f'{self.path}.{dcUK.module or self.module_rw}'
            try:
                mmm = importlib.import_module(path)
                importlib.reload(mmm)
                review = mmm.main(dcUK)
                data = [_div(**style(display='grid', gridTemplateRows='auto 1fr'), children=[
                            _div(className='toolbar', children=[self.openMax]),
                            _div(**style(textAlign='center', overflow='auto', height='100%'), className='arm_review', children=[review]),  # body
                            ])
                        ]
            except Exception as ex:
                s = f'{dcUK.form}-{dcUK.cmd}. Module:"{path}"\n{ex}\n{traceback.format_exc()}'
                data = [_div(s, br=1, s2=1)]
                err(s, cat='arm.getData')

        elif dcUK.cmd == 'getStudentList':
            if not (dcUK._staff or 'куратор' in dcUK._role):
                data = '""'
            else:
                stedentList = set()
                for sgr in well('sessionsGr_GrId', dcUK.nvGroup):
                    sstArr = well('sessionSt_sgrId', sgr.id)
                    for sst in sstArr:
                        dcProfile = well('profiles', sst.pref)
                        if dcProfile:
                            fullName = dcProfile.full_name
                            stedentList.add(f'{fullName}|{sst.pref}')
                        else:
                            err(f'Профайл {sst.pref} удален', cat='arm_view.getStudentList')
                data = sorted(list(stedentList))
        else:
            s = f'invalid cmd: {dcUK.form}-{dcUK.cmd}'
            err(s, cat='arm.getData')
            data = [f'{s}']
        return json.dumps(data, ensure_ascii=False)
    # ***

    def page(self, request):
        band = _field('jobName', 'band', self.moduleList, name='group', sel=-1, recalcText=1, **style(margin='auto'), className='radioBand')

        # dt1 = datetime.now().replace(day=1).date() - relativedelta(months=2)
        return self.docPage([
            _div(className='color-head',
                 **style(display='grid', gridTemplateRows='auto 1fr auto', padding='2px 0', maxHeight='100%', textAlign='center'),
                 children=[
                    _div(children=[
                        _field('grTitle_FD', 'fd', name='group', className='htmlHelp', **style(border='none'), s2=1),
                        _div('<<C+Студент>>', name='student', **style(border='none'), className='htmlHelp'),
                        _field('student', 'lbsd', [], name='student', className='htmlHelp', **style(width=250, background='#fff')),
                        _field('student3_FD', 'fd', name='student3', className='htmlHelp', **style(border='none')),
                        _div('Выберите сводку и фильтр',
                             name='group', **style(border='none'), className='htmlHelp', br=1),
                        labelc('Выберите фильтр', name='student'),
                        labelc('Выберите фильтр', name='student3'),
                        band,
                        _div('Фильтр', **style(border='none'), name='group', className='htmlHelp'),
                        _field('filter', 'band',
                               ['Все|All', 'Сесс|Sess', 'Практ|Pr', 'Лекции|L'], sel=-1, recalcText=1, **style(margin='auto'), className='radioBand'),
                        _div(**gridStyle('auto auto', width=300, margin='auto'), children=[
                            labell('Начало периода'),
                            labell('Конец периода')
                        ]),

                        _div(**gridStyle('auto auto', width=300, margin='auto'),
                             children=[
                                _field('dt1', 'dt'),
                                _field('dt2', 'dt', xValue=today('-'))
                                ]),
                    ]),
                    _div(**style(background='#fff', border='2px solid #ccc'), children=[
                        _field('result', 'json'),
                        ]),
                    ])
            ], tool=[toolbar.close_])

    # *** *** ***
    def queryOpen(self, r):
        dcUK = r.dcUK

        doc = dcUK.doc
        doc.studentMode = dcUK.studentMode
        if dcUK.studentMode == '3':
            doc.student3_FD = dcUK.fullName
            doc.student3 = f'{dcUK.fullName}|{dcUK._profilePK}'
            group = well('profiles', dcUK._profilePK).STUDENT_GROUPS.partition('\n')[0]
            doc.nvGroup = group.partition('|')[2]
        else:
            doc.nvGroup = dcUK.nvGroup.partition('-')[0]

        doc.grTitle_FD = f" Группа {well('groups_groupId', doc.nvGroup).title}"

    # *** *** ***
