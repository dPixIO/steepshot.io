from django import forms

from steepshot_io.core.models import Subscribe


class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscribe
        fields = '__all__'
