'''

@author: deepseek.com

Django не показывает ошибку SMTP, а вылетает в 500

'''
from arm.tools.first import err
from django.core.mail.backends.smtp import EmailBackend


class SafeSMTPEmailBackend(EmailBackend):

    def send_messages(self, email_messages):
        try:
            return super().send_messages(email_messages)
        except Exception as ex:
            err(f"SMTP Error: {ex}", cat='smtp')
            return 0
