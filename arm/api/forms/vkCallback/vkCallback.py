'''
Created on 2024

@author: aon24
'''
from arm.tools.first import snd, err
from arm.tools.DC import DC, well, toWell, config
from arm.api.forms.formTools import style, _div, _btnD, _lc, _field
from arm.api.forms.classPage import Page
from arm.api.forms.toolbars import toolbar
from arm.settings import ALLOWED_HOSTS
from arm.tools.common import sndErr
from arm.tools.httpMisc import nvResponse
from arm.tools.dbToolkit.Book import allFromDB

import requests
import json
import uuid
import traceback

# *** *** ***
'''
Для каждого мероприятия д.б. создан свой альбом.
Для сессий признак
'''


class vkCallback(Page):
    '''
    in 'etc' _a('VK: обновить доступ', href=url, target='_blank')
    where url = 'https://id.vk.com/authorize?redirect_uri=https://{ALLOWED_HOSTS[0]}/api/vkcallback/&..'

    doGet: {..., 'vkcallback': (None, vkCallback),}
    vkCallback return PageOrDoc(mode=new, form=vkCallback)
    '''

    def __init__(self, request):
        self.form = getattr(self, '__module__', '').rpartition('.')[2]
        self.jsCssUrl = f'/api/jsv?forms/{self.form}/{self.form}.js'
        self.title = 'VK-api'
        self.noCaching = True

        super().__init__(request)

    # ***

    @sndErr
    def getData(self, dcUK):
        if dcUK.cmd == 'verify':
            try:
                # 1. загружаем базу в словари
                log = '1. загружаем базу в словари ***********\n'
                allDocs = {}  # словарь для перезаписи документов(что найти старый док и его обновить)
                for doc in allFromDB('VK'):
                    if doc.stmpl_map:
                        allDocs['stmpl_map'] = doc
                    elif doc.stmpl_id_or_cf:  # 'coomon', 'staff' or stmpl.id
                        allDocs[doc.stmpl_id_or_cf] = doc
                log += f'All: {len(allDocs)}\n'

                # 2. Сравниваем карту шаблонов stmpl_map
                log += '\n\n2. Сравниваем карту шаблонов stmpl_map\n'
                # словарь, где ключ - stmpl.id, value - ключ('coomon', 'staff' или stmpl.id или None)
                newStmplMap = compareStmplMap(allDocs)
                log += f'{"будем обновлять" if newStmplMap else "равны"}\n'

                # 3. отбираем пользователей с vk.id
                log += '\n\n3. отбираем пользователей с vk.id\n'
                staffsVKID, common = set(), set()
                students = []
                for profile in well('profiles').values():
                    if profile.status == 'active' and profile.vk:
                        if not any([profile.role == x for x in ['студент', 'гость', 'участник', 'выпускник']]):
                            common.add(profile.vk)  # Формруем новые списки 'common' и staff'
                            staffsVKID.add(profile.vk)
                            log += f'staffs: {profile.full_name}\n'
                        if 'студент' in profile.role:
                            students.append(profile)
                            common.add(profile.vk)
                            log += f'студент: {profile.full_name}\n'
                log += f'\nстудентов: {len(students)}, сотрудников: {len(staffsVKID)}\n'

                # 4. Актуализируем список друзей 'common' и 'staff'
                log += '\n\n4. Актуализируем список друзей "common" и "staff"\n'
                rc = updateVkListId(allDocs, 'common', sorted(common))  # session-free access
                log += f'common: {"eq" if rc == 1 else "updated" if rc == 2 else "ERROR ---------"}\n'
                rc = updateVkListId(allDocs, 'staff', sorted(staffsVKID))  # staff only
                log += f'staff: {"eq" if rc == 1 else "updated" if rc == 2 else "ERROR ---------"}\n'

                # 5. отбираем шаблоны, где есть видео из конткта c ограниченным видео
                log += '\n\n5. отбираем шаблоны, где есть видео из VK c ограниченным доступом\n'
                vkVideo = []
                vkVideoStmpId = ['common', 'staff', 'stmpl_map']  # for delete from DB
                for stm in well('sessionTmpl_nve', 'all'):
                    if stm.restrict == '1' and stm.VIDEOLIST and stm.VIDEOLIST[0] == '[':  # lection
                        vList = json.loads(stm.VIDEOLIST)
                        for vl in vList:
                            if vl.get('platform') == 'VK':
                                vkVideo.append(stm)
                                vkVideoStmpId.append(stm.id)
                                log += f'''{stm.nvevent}-{stm.title}: {vl.get('name')}\n'''
                                break

                log += f'Всего шаблонов  {len(vkVideo)}\n'

                # 6. Актуализируем списки пользователей с доступом к шаблонам c ограниченным видео
                log += '\n\n6. Актуализируем списки пользователей с доступом к шаблонам c видео из VK\n'
                for stm in vkVideo:
                    log += f'\n*** 6.1. Альбом: {stm.id} *** {stm.title}\n'
                    setStud = set()
                    for profile in students:  # сканируем всеx студентов, у которых  есть vk.id
                        for sst in well('sessionSt_idPr', profile.id):  # все сессии этого студня
                            if sst.ALLOW_S and sst.VIDEO_S:  # есть разрешение на доуступ к сессии и к видео
                                sgr = well('sessionGr_Id', sst.sessionGr_Id)
                                if sgr.sessionTmpl_Id == stm.id:  # нам нужна сессия с конкретным шаблоном
                                    setStud.add(profile.vk)
                        gr = well('groups_groupId', sgr.nvGroup_id)
                        log += f'{gr.title}. {profile.full_name}. VK-id:{profile.vk}\n'
                    # 6.2. Обновляем список пользователей для доступа к альбому
                    log += '\n*** 6.2. Обновляем список для доступа к альбому\n'
                    rc = updateVkListId(allDocs, stm.pk, sorted(staffsVKID | setStud))  # добавляем всеx сотрудников, у которых  есть vk.id
                    log += f'{stm.pk}: {"eq" if rc == 1 else "updated" if rc == 2 else "error"}\n'

                # 7. Удаляем из базы и ВК неактуальные списки
                log += '\n\n7. Удаляем из базы и ВК неактуальные списки\n'
                for id_or_cf, doc in allDocs.items():
                    if id_or_cf not in vkVideoStmpId:  # сессию удалили или перевели в категорию 'staff'
                        if vk_api_deleteList(id_or_cf):
                            log += f'vk_id_list "{id_or_cf}" deleted\n'
                            dcUK = DC(dbAlias='VK', unid=doc.unid)
                            dcUK.doc = doc
                            doc.old_stmpl_id_or_cf = doc.stmpl_id_or_cf
                            doc.stmpl_id_or_cf = ''
                            dcUK.save()
                        else:
                            log += f'ERROR --------- in vk_api_deleteList({id_or_cf})\n'

                # 8. Обновляем альбомы
                if newStmplMap:
                    log += '\n\n8. Обновляем альбомы\n'
                    if updateAlbums(allDocs, newStmplMap):
                        log += 'updateAlbums OK\n'
                    else:
                        log += 'ERROR --------- updateAlbums\n'
            except:
                e = traceback.format_exc()
                log += f'\n*****************\n{e}'
                err(f'{e}', cat='vkCallback')
            return nvResponse(log)
        else:
            return f'Server error. cmd: {dcUK.cmd}'

    # *** *** ***

    def page(self, dcUK):
        body = _div(**style(height='100%', overflow='auto', textAlign='center'),
            children=[
                _div(**style(width=300, margin='auto'), name='err', children=[
                    _lc('Ошибка авторизации'),
                    _field('err', 'fd', **style(display='block', width=300, margin='10px auto', color='red')),
                    _btnD('Выйти из системы и войти через ВК', 'logout'),
                ]),
                _div(**style(width=300, margin='auto'), name='gut', children=[
                    _lc('Вы успешно авторизованы в ВК'),
                    _btnD('Проверить допуск к материалам', 'verify', **style(margin='10px auto')),
                    # *labField('token', 'token', 'tx')
                ]),
                _div(**style(width=600, margin='auto'), name='gut', children=[
                    _field('log', 'tx', readOnly=1, br=1)
                ]),
        ])

        return self.docPage([body], tool=[toolbar.close_])

    # *** *** ***

    def queryOpen(self, r):

        if r.dcUK.device_id:
#            dcUK.doc.token = getAccesToken(dcUK)
            # dcUK.doc.log = getAccesToken(dcUK)
            r.dcUK.doc.log = str(dcUK)
        else:
            r.dcUK.doc.err = f'not dcUK.device_id'

# *** *** ***


def getAccesToken(dcUK):

    def _err(s):
        dcUK.doc.err = s
        err(s, cat='vkCallback')

    url = "https://id.vk.comq/oauth2/auth"

    data = '&'.join([
        'grant_type=authorization_code',
        f'''code_verifier={well('code_verifier')}''',
        f'redirect_uri=https://{ALLOWED_HOSTS[0]}/api/vkcallback/',
        f'code={dcUK.code}',
        f'client_id={config.vk_adm_id}',
        f'device_id={dcUK.device_id}',
        f'scope=friends',
        f'state={dcUK.state}'
    ]).encode()

    headers = {"Content-Type": "application/x-www-form-urlencoded", }

    try:
        response = requests.post(url, data=data, headers=headers)

        # Проверяем статус ответа
        response.raise_for_status()

        # Обрабатываем успешный ответ
        if response.status_code == 200:
            result = DC(response.json())
            if result.error:
                return _err(f'status_code=200\nERROR: {result.error}\nERROR_DESCRIPTION: {result.ERROR_DESCRIPTION}')

            dcUK.doc.err = f'status_code=200: {result}'
            toWell(result, 'vkToken')
            return f'DC-gut: {result}'

            # return vk_api.VkApi(
            #     token=result.ACCESS_TOKEN,
            #     app_id=vk_adm_id,
            #     # app_id=vk_app_id,
            #     # client_secret=vk_client_secret,
            #     api_version='5.199',
            # ).get_api()

        else:
            return _err(f'Ошибка: {response.status_code}\n{response.text}')
    except requests.exceptions.RequestException as e:
        return _err(f"Произошла ошибка при отправке запроса\n{e}")


# *** *** ***

def compareStmplMap(allDocs):
    newMap = {}
    for stm in well('sessionTmpl_nve', 'all'):
        newMap[stm.id] = None
        if stm.VIDEOLIST and stm.VIDEOLIST[0] == '[':
            vList = json.loads(stm.VIDEOLIST)
            for vl in vList:
                if vl.get('platform') == 'VK':
                    if not stm.restrict:  # session
                        newMap[stm.id] = 'common'
                    elif stm.restrict == '1':  # lection
                        newMap[stm.id] = stm.id
                    else:  # staff
                        newMap[stm.id] = 'staff'
                    break
    try:
        oldMap = allDocs['stmpl_map'].stmpl_map
        if oldMap == json.dumps(newMap, sort_keys=True):
            return None
    except Exception as ex:
        err(f'json.dumps in compareStmplMap: {ex}', cat='form:vkCallback')

    return newMap
    
# *** *** ***


def updateAlbums(allDocs, newMap):
    if vk_api_updateAlbums(newMap):
        snd('stmpl_map updated', cat='vkCallback')
        doc = allDocs.get('stmpl_map', DC(unid=uuid.uuid4().hex))
        dcUK = DC(dbAlias='VK', unid=doc.unid)
        dcUK.doc = DC(stmpl_map=json.dumps(newMap, sort_keys=True))
        return dcUK.save()

# *** *** ***


def updateVkListId(allDocs, idOrCF, newList):
    doc = allDocs.get(idOrCF, DC(unid=uuid.uuid4().hex))
    new_vk_id_list = json.dumps(newList)
    if new_vk_id_list == doc.vk_id_list:
        return 1

    if vk_api_ChangeIdList(idOrCF, newList):
        snd(f'vk_id_list "{idOrCF}" updated', cat='vkCallback')
        dcUK = DC(dbAlias='VK', unid=doc.unid)
        dcUK.doc = DC(stmpl_id_or_cf=idOrCF, vk_id_list=new_vk_id_list)
        dcUK.save()
        return 2

    return 0

# *** *** ***


def vk_api_ChangeIdList(idOrCF, newList):
    return True


def vk_api_deleteList(idOrCF):
    return True


def vk_api_updateAlbums(newMap):
    return True


# *** *** ***
def vk_comm_on(vk):
    return 'vk_comm_on'
