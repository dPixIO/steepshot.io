from django import forms

from dpix_io.core.models import Subscribe, Investors


class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscribe
        fields = '__all__'


class InvestorsForms(forms.ModelForm):
    description = forms.CharField(required=False, widget=forms.Textarea(
        attrs={'placeholder': 'Why do you want to invest in dPix(optional)?'}))

    class Meta:
        model = Investors
        fields = '__all__'
