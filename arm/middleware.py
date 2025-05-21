from arm.tools.DC import DC, DCC, well
from arm.tools.first import snd, err
from arm.tools.common import cleanPhone

from django.contrib.auth import logout
from django.shortcuts import redirect
from allauth.socialaccount.models import SocialAccount
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
    # query = "code=90f5eb3def9744e314&state=OdMG1ewZPtoHFCwi" for VK

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

        # ***

        account = SocialAccount.objects.filter(user=user, provider=provider).first()
        if not account:
            return err(f'not account for user={user}, provider={provider}', cat='login')
        
        dc = DCC(account.extra_data)

        # *** VK
        if provider == 'vk':
            prof = well('profilesForVK', dc.screen_name) or well('profilesForVK', str(dc.id))  # в поле "ВК" должна быть указана страница пользователя
            if prof:
                refresh(prof, vk_user_id=dc.id, user=user.id)
                snd(f'VK:{prof.full_name} ({ip})', cat='login')
                return

            if dc.mobile_phone:
                phone = cleanPhone(dc.mobile_phone)
                prof = well('profilesByPhone', phone)
                if prof:
                    refresh(prof, vk_user_id=dc.id, user=user.id, mobile_phone=phone)
                    snd(f'VK:{prof.full_name} (phone:{phone}) {ip}', cat='login')
                    return

            if dc.home_phone:
                phone = cleanPhone(dc.home_phone)
                prof = well('profilesByPhone', phone)
                if prof:
                    refresh(prof, vk_user_id=dc.id, user=user.id, home_phone=phone)
                    snd(f'VK:{prof.full_name} (phone:{phone}) {ip}', cat='login')
                    return

            if dc.email:
                prof = well('profilesByEmail', dc.email.lower())
                if prof:
                    refresh(prof, vk_user_id=dc.id, user=user.id)
                    snd(f'VK:{prof.full_name} (e-mail:{dc.mail}) {ip}', cat='login')
                    return

            if user.is_staff:
                snd(f'VK+:{user.username} ({ip})', cat='login')

            else:
                s = f'{dc.screen_name} ({dc.first_name} {dc.last_name})'
                err(f'{provider} => Profile not found for {provider}: {s} {ip}', cat='login')

            return

        # *** Y
        if provider == 'yandex':
            # account.extra_data = {
            # "id": "9903215219", "login": "tor11",
            # "client_id": "dde5d986ce7f47325d8",
            # "default_email": "tor11@yandex.ru",
            # "emails": ["tor11@yandex.ru"],
            # "default_phone": {"id": 31315783, "number": "+7911111111111"},
            # "psuid": "1.AAyEAQ.ykifcJ...9kQ.Bd...2MoQ5-A"
            # }

            phone = dc.default_phone and dc.default_phone.get('number')
            for mail in dc.emails:
                prof = well('profilesByEmail', mail.lower())
                if prof:
                    refresh(prof, y_user_id=dc.id, phone=prof.phone or phone, user=user.id)
                    return snd(f'Y:{prof.FULL_NAME} (e-mail:{mail}) {ip}', cat='login')

            if phone:
                phone = cleanPhone(phone)
                prof = well('profilesByPhone', phone)
                if prof:
                    em = dc.emails and dc.emails[0]  # user has many emails
                    refresh(prof, y_user_id=dc.id, user=user.id, email=prof.email or em, phone=phone)
                    return snd(f'Y:{prof.FULL_NAME} (phone:{phone}) {ip}', cat='login')

            elif user.is_staff:
                snd(f'Y+:{user.username} ({ip})', cat='login')

            err(f'Y: emails: "{dc.emails}" phone: {phone} not found. {ip}', cat='login')
            return

        # *** G
        if provider == 'google':
            # account.extra_data = {
            #     "iss": "https://accounts.google.com",
            #     "azp": "2qq..7rf.apps.googleusercontent.com",
            #     "aud": "2qq..7rf.apps.googleusercontent.com",
            #     "sub": "11331056",
            #     "email": "stor@gmail.com",
            #     "email_verified": true,
            #     "at_hash": "qF06VMcbXcwRA",
            #     "name": "\u0410\...0439 \u..043e\u0432",
            #     "picture": "https://lh3.googleusercontent.com/a/AC...Iyqaow=s96-c",
            #     "given_name": "\u0410\...35\u0439",
            #     "family_name": "\u041d\u0...\u0432", "iat": 132362100,
            #     "exp": 1700000700
            # }
            prof = well('profilesByEmail', dc.email.lower())
            if prof:
                return snd(f'G:{prof.FULL_NAME} (e-mail:{mail}) {ip}', cat='login')

            elif user.is_staff:
                return snd(f'G+:{user.username} ({ip})', cat='login')

            err(f'G: email: "{dc.email}" not found. {ip}', cat='login')
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
        # print(f"MobileMW: **************PATH_INFO={request.META['PATH_INFO']}")
        # print(f"MobileMW: ************** QUERY_STRING={unquote(request.META['QUERY_STRING'])}")

        path = request.META.get('PATH_INFO').strip()
        if path.endswith('/'):  # м.б "api/key?param" , а м.б. "api/key/?param"
            path = path[:-1]
        path = path.rpartition('/')[2]  # path = key

        query = unquote(request.META['QUERY_STRING']) or 'form=arm'

        if '?' in query:
            query = query.rpartition('?')[2]

        ua = parse(request.META.get('HTTP_USER_AGENT', ''))
        request.dcUK = DC(
            _userAgent=(ua.is_mobile and 'mobile') or (ua.is_pc and 'pc') or (ua.is_tablet and 'tablet') or 'unknown',
            _path=path,
            _query=query,
            _method=request.method
        )
        dcUK = request.dcUK
        for p in query.split('&'):
            if '=' in p:
                l, _, r = p.partition('=')
                dcUK[l.strip()] = r.strip().replace('џ', '?')

        user = request.user
        if not user.is_authenticated:
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
        elif dcUK._staff:
            dcUK.fullName = request.user.first_name
        else:
            logout(request)
            return redirect('/')

        return self.get_response(request)

# *** *** ***

