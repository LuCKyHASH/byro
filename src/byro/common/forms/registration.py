from django import forms
from django.utils.translation import ugettext_lazy as _

from byro.common.models import Configuration
from byro.members.models import Member


class RegistrationConfigForm(forms.Form):
    member__number = forms.IntegerField(required=False, label=_('Membership number/ID'))
    member__name = forms.IntegerField(required=False, label=_('Name'))
    member__address = forms.IntegerField(required=False, label=_('Address'))
    member__email = forms.IntegerField(required=False, label=_('E-Mail'))
    membership__start = forms.IntegerField(required=False, label=_('Join date'))
    membership__amount = forms.IntegerField(required=False, label=_('Membership fee'))
    membership__interval = forms.IntegerField(required=False, label=_('Payment interval'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for profile in Member.profile_classes:
            for field in profile._meta.fields:
                if field.name not in ('id', 'member'):
                    self.fields[f'{profile.__name__}__{field.name}'] = forms.IntegerField(required=False, label=f'{field.verbose_name or field.name} ({profile.__name__})')
        config = Configuration.get_solo().registration_form or []
        for entry in config:
            field = self.fields.get(entry['name'])
            if field:
                field.initial = entry['position']

    def clean(self):
        ret = super().clean()
        values = [value for value in self.cleaned_data.values() if value is not None]
        if not len(list(values)) == len(set(values)):
            raise forms.ValidationError('Every position must be unique!')
        return ret

    def save(self):
        data = [
            {
                'position': value,
                'name': key,
            }
            for key, value in self.cleaned_data.items()
        ]
        config = Configuration.get_solo()
        config.registration_form = list(data)
        config.save()
