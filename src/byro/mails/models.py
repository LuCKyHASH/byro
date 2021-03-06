from copy import deepcopy

from django.db import models
from django.utils.timezone import now
from django.utils.translation import override, ugettext_lazy as _
from i18nfield.fields import I18nCharField, I18nTextField

from byro.common.models.auditable import Auditable
from byro.mails.send import SendMailException


class MailTemplate(Auditable, models.Model):

    subject = I18nCharField(
        max_length=200,
        verbose_name=_('Subject'),
    )
    text = I18nTextField(
        verbose_name=_('Text'),
    )
    bcc = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_('BCC'),
        help_text=_('Enter comma separated addresses. Will receive a blind copy of every mail sent from this template. This may be a LOT!'),
    )

    def to_mail(self, email, locale=None, context=None, skip_queue=False):
        with override(locale):
            context = context or dict()
            try:
                subject = str(self.subject).format(**context)
                text = str(self.text).format(**context)
            except KeyError as e:
                raise SendMailException(f'Experienced KeyError when rendering Text: {str(e)}')

            mail = EMail(
                to=email,
                reply_to=self.reply_to,
                bcc=self.bcc,
                subject=subject,
                text=text,
            )
            if skip_queue:
                mail.send()
            else:
                mail.save()
        return mail


class EMail(Auditable, models.Model):
    to = models.CharField(
        max_length=1000,
        verbose_name=_('To'),
        help_text=_('One email address or several addresses separated by commas.'),
    )
    reply_to = models.CharField(
        max_length=1000,
        null=True, blank=True,
        verbose_name=_('Reply-To'),
    )
    cc = models.CharField(
        max_length=1000,
        null=True, blank=True,
        verbose_name=_('CC'),
        help_text=_('One email address or several addresses separated by commas.'),
    )
    bcc = models.CharField(
        max_length=1000,
        null=True, blank=True,
        verbose_name=_('BCC'),
        help_text=_('One email address or several addresses separated by commas.'),
    )
    subject = models.CharField(
        max_length=200,
        verbose_name=_('Subject'),
    )
    text = models.TextField(verbose_name=_('Text'))
    sent = models.DateTimeField(null=True, blank=True, verbose_name=_('Sent at'))

    def send(self):
        if self.sent:
            raise Exception('This mail has been sent already. It cannot be sent again.')

        from byro.mails.send import mail_send_task
        mail_send_task.apply_async(
            kwargs={
                'to': self.to.split(','),
                'subject': self.subject,
                'body': self.text,
                'sender': self.reply_to,
                'cc': (self.cc or '').split(','),
                'bcc': (self.bcc or '').split(','),
            }
        )

        self.sent = now()
        self.save()

    def copy_to_draft(self):
        new_mail = deepcopy(self)
        new_mail.pk = None
        new_mail.sent = None
        new_mail.save()
        return new_mail
