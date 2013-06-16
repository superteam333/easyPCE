from django import forms

class ChangeFavForm(forms.Form):
    dept = forms.CharField(max_length=10)
    number = forms.CharField(max_length=10)
    isFav = forms.BooleanField(required=True)
	user = forms.CharField(max_length=100)
