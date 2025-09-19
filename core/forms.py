from django import forms
from django.contrib.auth.password_validation import validate_password
from django.forms import BooleanField, ModelMultipleChoiceField


class BaseForm(forms.Form):
    error_css_class = 'error'
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if not (isinstance(self.fields[field], BooleanField) or isinstance(self.fields[field], ModelMultipleChoiceField)):
                if hasattr(self.fields[field].widget, 'attrs'):
                    self.fields[field].widget.attrs.update({'class': 'w3-input w3-border'})
                    self.fields[field].error_messages = {'required': 'This field is necessary!'}


class PasswordResetForm(BaseForm):
    password = forms.CharField(label='New Password', widget=forms.PasswordInput)
    re_password = forms.CharField(label='New Password  (Confirm)', widget=forms.PasswordInput)

    def clean_re_password(self):
        if self.data['password'] == self.cleaned_data['re_password']:
            v = validate_password(password=self.cleaned_data['re_password'])
            if not v:
                return self.cleaned_data['re_password']
        else:
            raise forms.ValidationError('The two password fields do not match')