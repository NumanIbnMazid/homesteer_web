from django import forms
from .models import Membership

class MemberUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MemberUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model   = Membership
        fields  = ['role']