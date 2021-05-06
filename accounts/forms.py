from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
import re

class CustomSignupForm(SignupForm):  
    def signup(self, request, user):
        user.save()
        userprofile, created = self.get_or_create(user=user)
        user.userprofile.save()

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

class UserProfileUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # magic 
        self.user = kwargs['instance'].user
        user_kwargs = kwargs.copy()
        user_kwargs['instance'] = self.user
        self.uf = UserForm(*args, **user_kwargs)
        # magic end 

        super(UserProfileUpdateForm, self).__init__(*args, **kwargs)

        self.fields.update(self.uf.fields)
        self.initial.update(self.uf.initial)
        
        self.fields['first_name']   = forms.CharField(required=False,
            widget=forms.TextInput(attrs={'placeholder': 'Enter your first name'}))
        self.fields['last_name']    = forms.CharField(required=False,
            widget=forms.TextInput(attrs={'placeholder': 'Enter your last name'}))
        self.fields['contact']      = forms.CharField(required=False, min_length=14, max_length=14,
            help_text='Phone number must be valid and start with +880',
            widget=forms.TextInput(attrs={'placeholder': 'Ex: +8801000000000'}))
        self.fields['address']      = forms.CharField(required=False,
            widget=forms.TextInput(attrs={'placeholder': 'Enter your address'}))
        self.fields['facebook']     = forms.CharField(required=False,
            widget=forms.TextInput(attrs={'placeholder': 'Enter your facebook profile link'}))
        self.fields['linkedin']     = forms.CharField(required=False,
            widget=forms.TextInput(attrs={'placeholder': 'Enter your linkedin profile link'}))
        self.fields['website']      = forms.CharField(required=False,
            widget=forms.TextInput(attrs={'placeholder': 'Enter your website link'}))
        self.fields['about']        = forms.CharField(required=False,
            widget=forms.Textarea(attrs={'rows': 2, 'cols': 2, 'placeholder': 'Enter more about you'}))
        # define fields order if needed
        self.fields.keyOrder = (
            'first_name',
            'last_name',
            'gender',
            'contact',
            'address',
            'facebook',
            'linkedin',
            'website',
            'image',
            'about',
        )

    class Meta:
        model = UserProfile
        exclude = ['user', 'slug', 'user_type']

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if first_name != '' :
            allowed_char    = re.match(r'^[A-Za-z.,\- ]+$', first_name)
            length          = len(first_name)
            if length > 15:
                raise forms.ValidationError("Maximum 15 characters allowed !")
            if not allowed_char:
                raise forms.ValidationError("Please Enter Valid Name (Only Alpha values allowed, Ex:Abc) !")
        return first_name
    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if last_name != '' :
            allowed_char    = re.match(r'^[A-Za-z.,\- ]+$', last_name)
            length          = len(last_name)
            if length > 20:
                raise forms.ValidationError("Maximum 20 characters allowed !")
            if not allowed_char:
                raise forms.ValidationError("Please Enter Valid Name (Only Alpha values allowed, Ex:Abc) !")
        return last_name

    def clean_contact(self):
        contact = self.cleaned_data.get("contact")
        if contact != '' :
            appears_special = contact.count('+')
            country_code    = '+880'
            starts_with_code= contact.startswith(country_code)
            allowed_char    = re.match(r'^[0-9+]+$', contact)
            length          = len(contact)
            
            if not allowed_char or not starts_with_code or appears_special > 1 or length < 11 :
                raise forms.ValidationError("Must be valid phone number and start with (+880).</br> Ex: +8801000000000")
        return contact

    def save(self, *args, **kwargs):
        self.uf.save(*args, **kwargs)
        return super(UserProfileUpdateForm, self).save(*args, **kwargs)