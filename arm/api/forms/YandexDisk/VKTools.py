'''
Created on 2024

@author: aon24
'''

from arm.tools.DC import DC, well, config
from arm.tools.first import snd, err
from arm.tools.loadWell import loadWell
from arm.tools.common import sndErr

import vk_api

# *** *** ***

api_version = '5.199'


@sndErr
def getVideoUrlVK(dcUK):
    stempl = well('sessionTmpl_id', dcUK.id)
    vk = vk_api.VkApi(app_id=config.vk_adm_id, token=config.vk_adm_token, api_version=api_version).get_api()
    videos = vk.video.get(owner_id=-config.vk_group_id, album_id=stempl.VK_ALBUM_ID).get('items', [])

    for item in videos:
        if str(item['id']) == dcUK.video_id:
            return item['player']

    err(f'getVideoUrl not found. ID="{dcUK.id}" video_id="{dcUK.video_id}"', cat='VK-error')
    return f'File "{dcUK.file}" not found'

# *** *** ***


@sndErr
def makeVideoVK(dcUK):
    stempl = well('sessionTmpl_id', dcUK.id)
    vk = vk_api.VkApi(app_id=config.vk_adm_id, token=config.vk_adm_token, api_version=api_version).get_api()
    videos = vk.video.get(owner_id=-config.vk_group_id, album_id=stempl.VK_ALBUM_ID).get('items', [])

    dirInfo = []
    for item in videos:
        it = {}
        it['platform'] = 'VK'
        it['name'] = stempl.alias
        it['url'] = item['title']
        it['video_id'] = item['id']
        it['image'] = item['image'][0]['url']
        dirInfo.append(it)

    return dirInfo

# ***


@sndErr
def createAlbums(m):
    vk = vk_api.VkApi(app_id=config.vk_adm_id, token=config.vk_adm_token, api_version=api_version).get_api()

    for stm in well('sessionTmpl_nve', 'all'):  # все шаблоны
        if stm.alias and stm.nvEvent:
            vk_album = f'{stm.nvEvent}. {stm.alias}'[:40]  # 1. Коммуникативная компетентность
            album = None
            for a in vk.video.getAlbums(owner_id=-config.vk_group_id)['items']:
                if a['title'] == vk_album:
                    album = a
                    break
            if album and str(album['id']) == stm.vk_album_id:  # альбом есть, прописан
                m.log += f'''\nalbum already exists. vk_album_id: {a['id']} for "{vk_album}"'''
                continue

            if album:  # альбом есть, но не прописан (напр. создан вручную или из Я-диска)
                stm.vk_album_id = album['id']
                m.log += f'''\nrefresh vk_album_id: {stm.vk_album_id} for "{vk_album}"'''
            else:  # альбома нет
                a = vk.video.addAlbum(group_id=config.vk_group_id, title=vk_album, privacy='members')
                stm.vk_album_id = a['album_id']
                m.log += f'''\nalbum created vk_album_id: {stm.vk_album_id} for "{vk_album}"'''

            dc = DC(dbAlias='nv_SessionTmpl', unid=stm.id, fullName='VK_createAlbums')
            dc.doc = stm
            dc.save()

    snd(m.log, cat='VK_createAlbums')
    loadWell('YandexDisk')

# *** *** ***

def _err(s):
    # err(s, cat='Y-error')
    raise Exception(s)

# *** *** ***


@sndErr
def y_makeFolder(y, path, sil=None):
    pass
    # ***
