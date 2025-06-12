'''

@author: deepseek.com

Django не показывает ошибку SMTP, а вылетает в 500

'''
from arm.tools.first import snd, err

from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail.message import sanitize_address


class SafeSMTPEmailBackend(EmailBackend):

    def _send(self, email_message):
        """Add snd() and err()"""
        if not email_message.recipients():
            return False
        encoding = email_message.encoding or settings.DEFAULT_CHARSET
        from_email = sanitize_address(email_message.from_email, encoding)
        recipients = [sanitize_address(addr, encoding) for addr in email_message.recipients()]
        message = email_message.message()
        try:
            self.connection.sendmail(from_email, recipients, message.as_bytes(linesep="\r\n"))
            snd(f'"{email_message.subject[:50]}" {";".join(recipients)}', cat='smtp')
            return True
        except Exception as ex:
            err(f"SMTP Error: {ex}", cat='smtp')
            return False

