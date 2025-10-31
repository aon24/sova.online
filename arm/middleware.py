from arm.tools.DC import DC, well, config
from arm.tools.first import snd, err
from arm.tools.common import cleanPhone

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from urllib.parse import unquote
from user_agents import parse

# todo: где в оаут2 есть сигнал для проверки емайл. Сделать блэклист


def refresh(prof, **kv):
    f = False
    for k, v in kv.items():
        if v and prof[k].lower() != str(v).lower():
            prof[k] = v
            f = True
    if f:
        dc = DC(dbAlias='nv_Profile', unid=prof.id, _superUser=1)
        dc.doc = prof
        if not dc.save():
            err('Save "user" to profile error', cat='afterLogin')


@receiver(user_logged_in)
def afterLogin(sender, request, user, **kwargs):
    # path = "/accounts/<provider>/login/callback/" for social network
    # path = "/accounts/login/" for login/password

    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip:
        ip = ip.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    try:
        path = request.META.get("PATH_INFO", '')
        ls = (path + '//').split('/')
        provider = ls[2] or ls[1]

        if provider in ['login', 'signup']:
            prof = well('profByUserId', str(user.id))
            if prof:
                return snd(f'DJ:{prof.FULL_NAME} ({ip})', cat=provider)
            if user.is_staff:
                return snd(f'DJ+:{user.username} ({ip})', cat=provider)

            if user.first_name:
                phone = cleanPhone(user.last_name)
                prof = well('profilesByPhone', phone)
                if prof:
                    if prof.email:
                        if prof.email.lower() != user.email.lower():
                            prof.email = f'{user.email}, {prof.email}'
                    else:
                        prof.email = user.email
                    refresh(prof, user=user.id)
                    return snd(f'{prof.full_name} (phone:{phone}) {ip}', cat=provider)

            err(f'provider: {path}', cat=provider)
            return

        else:
            err(f'provider "{provider}" not found. Path="{path}". {ip}', cat='login')

    except Exception as ex:
        err(f'{ex} {ip}', cat=f'{provider}_account_Exception')
        return
    

@receiver(user_logged_out)
def user_logged_out(sender, request, user, **kwargs):
    if user:
        prof = well('profByUserId', str(user.id))
        fullName = prof and prof.FULL_NAME
        snd(fullName or user.username, cat='logoff')

# *** *** ***


class MobileMW(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # print(f"MobileMW: ************** url: {unquote(request.path)}?{unquote(request.META['QUERY_STRING'])}")

        user = request.user

        path = request.path
        if path.startswith('/admin') and not (user and user.is_superuser):
            request.path = ''
            request.dcUK = DC()
            return self.get_response(request)

        if path.endswith('/'):  # м.б "api/key?param" , а м.б. "api/key/?param"
            path = path[:-1]
        path = path.rpartition('/')[2]  # path = key

        query = unquote(request.META['QUERY_STRING'])

        if '?' in query:
            query = query.rpartition('?')[2]

        ua = parse(request.META.get('HTTP_USER_AGENT', ''))
        request.dcUK = DC(
            _userAgent=(ua.is_mobile and 'mobile') or (ua.is_pc and 'pc') or (ua.is_tablet and 'tablet') or 'unknown',
            _path=path,
            _query=query,
        )
        dcUK = request.dcUK

        for p in query.split('&'):
            if '=' in p:
                l, _, r = p.partition('=')
                dcUK[l.strip()] = r.strip()

        if not user.is_authenticated:
            if config.DEMO_MODE:
                from django.middleware.csrf import get_token
                get_token(request)
            return self.get_response(request)

        dcUK._superUser = user.is_superuser
        dcUK._staff = user.is_staff

        prof = well('profByUserId', str(user.id))

        if prof:
            dcUK._role = ''  # отсекаем лишнии роли
            if 'куратор' in prof.role:
                dcUK._role = 'куратор'
            if 'преподаватель' in prof.role:
                dcUK._role += 'преподаватель'

            dcUK._role = dcUK._role or ('студент' in prof.role and 'студент')

            dcUK._profilePK = prof.id
            dcUK.fullName = prof.full_name
            dcUK._cssTheme = prof.cssTheme
        elif dcUK._staff:
            dcUK.fullName = request.user.first_name
        else:
            logout(request)
            return redirect('/')

        return self.get_response(request)

# *** *** ***

