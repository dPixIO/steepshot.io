from django.contrib.auth.hashers import check_password
from django import forms
from django.core.exceptions import ObjectDoesNotExist


from steepshot_io.dashboard.models import DashboardUsers


class UserLoginDasboardForm(forms.ModelForm):
    def clean_password(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        try:
            user = DashboardUsers.objects.get(username=username)
        except ObjectDoesNotExist:
            raise forms.ValidationError('Incorrect Username')
        if check_password(password, user.password):
            return password
        else:
            raise forms.ValidationError('Incorrect Password')

    class Meta:
        model = DashboardUsers
        exclude = []
        widgets = {
            'password': forms.PasswordInput(),
        }
