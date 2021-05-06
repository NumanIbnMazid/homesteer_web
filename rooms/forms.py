from django import forms
from .models import Room, ManagerialSetting
import re

class RoomCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RoomCreateForm, self).__init__(*args, **kwargs)
        self.fields['title']        = forms.CharField(max_length=20,
            widget=forms.TextInput()
        )
        self.fields['description']  = forms.CharField(required=False, max_length=100,
            widget=forms.Textarea(attrs={'rows': 2, 'cols': 2}))
        self.fields['title'].help_text = "Names have power. Keep it meaningful"
        self.fields['description'].help_text = "Keep some information that represents the room"

    class Meta:
        model   = Room
        fields  = ['title', 'description']

    def clean_title(self):
        title   = self.cleaned_data.get('title')
        qs      = Room.objects.filter(title__iexact=title)
        if qs.exists():
            raise forms.ValidationError('This title is already taken ! Please try another one.')
        if not title == None :
            allowed_chars   = re.match(r'^[0-9A-Za-z-_@.]+$', title)
            length          = len(title)

            if not allowed_chars:
                raise forms.ValidationError('Please remove any special characters or spaces. Only Alpha Numeric values and "-", "@", ".", "_" are allowed!')
            if length > 30:
                raise forms.ValidationError('Maximum 30 characters allowed !')
        return title


class RoomUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RoomUpdateForm, self).__init__(*args, **kwargs)
        self.fields['title']        = forms.CharField(max_length=30,
            widget=forms.TextInput()
        )
        self.fields['description']  = forms.CharField(required=False, max_length=100,
            widget=forms.Textarea(attrs={'rows': 2, 'cols': 2}))
        self.fields['title'].help_text = "Names have power. Keep it meaningful"
        self.fields['privacy'].help_text = "Changing privacy from Public to Secret will disallow other users to find your room by search"
        self.fields['description'].help_text = "Keep some information that represents the room"

    class Meta:
        model   = Room
        fields  = ['title', 'privacy', 'description']

    def clean_title(self):
        title_instance = self.instance.title
        title   = self.cleaned_data.get('title')
        qs      = Room.objects.filter(title__iexact=title)
        if title != title_instance and qs.exists():
            raise forms.ValidationError('This title is already taken ! Please try another one.')
        if not title == None :
            allowed_chars   = re.match(r'^[0-9A-Za-z-_@.]+$', title)
            length          = len(title)

            if not allowed_chars:
                raise forms.ValidationError('Please remove any special characters or spaces. Only Alpha Numeric values and "-", "@", ".", "_" are allowed!')
            if length > 30:
                raise forms.ValidationError('Maximum 30 characters allowed !')
        return title


class ManagerialSettingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ManagerialSettingForm, self).__init__(*args, **kwargs)
        self.fields['shopping_type'].help_text = "<span class='text-success'>USAGE:</span> Select 'ROOM MANAGER DEPENDENT SHOPPING' if only room manager is responsible for shopping or select 'INDIVIDUAL MEMBER DEPENDENT SHOPPING' if all the members of the room are responsible for shopping"

    class Meta:
        model   = ManagerialSetting
        fields  = ['shopping_type']
