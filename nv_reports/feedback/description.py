# -*- coding: utf-8 -*-

'''
Created on 14 mar 2018

@author: aon
'''
from arm.tools.DC import well


def reportList(dt1, dt2):
    return [
        dict(
            module='modules.fbByFio',
            title='SU 1. Обратная связь по фамилиям',
            firstList=[
                'SU 1.1 Кураторы',
                'SU 1.2 Преподаватели',
            ],
            addList=[v for k, v in well('eventsByCode').items() if k in ['1', 'L', 'CL']] + ['Все'],
            dt1=dt1,
            dt2=dt2,
            quarter=None,  # True: show label "задать квартал в качестве периода" + qartButton
            comment='SU 1.1-1.2. Сводные таблицы по фамилиям.',
        ),

        # dict(
        #     module='modules.dynamo',
        #     title='SU 1. Динамика за 2 периода',
        #     firstList=[
        #         'Сравнительные данные',
        #         'Ф 3.Д. Отчет + документы для проверки',
        #     ],
        #     dt1='', dt2='',
        #     diff=True,  # показать даты прошлого периода и кнопку переноса дат
        #     dt3='', dt4='',
        #     comment='Формы 3. Ежеквартальный отчет',
        # ),
        #
        # dict(
        #     module='F4.main',
        #     title='Персональный контроль. Студент.',
        #     firstList=[
        #         'Посещаемость',
        #         'Оплата',
        #         'Успеваемость',
        #     ],
        #     who='/api/well?clues=студент2',
        #     dt1_label='по состоянию на',
        #     dt1=dt2,
        #     comment='Формы 3. Ежеквартальный отчет для АИС «Регион»',
        # ),
        #
        # dict(
        #     module='F3.main',
        #     title='Персональный контроль. Преподаватель.',
        #     firstList=[
        #         'Оценки (рейтинг)',
        #     ],
        #     addList=[
        #         'Общий',
        #         '1. Насколько понятно',
        #         '2. Удовлетворены объемом теории',
        #         '3. Сопровождение обучения',
        #     ],
        #     who='/api/well?clues=преподаватель2',
        #     dt1=dt1,
        #     dt2=dt2,
        # ),

    ]
