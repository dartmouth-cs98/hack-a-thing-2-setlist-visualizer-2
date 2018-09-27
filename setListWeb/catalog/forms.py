from django import forms

class SearchForm(forms.Form):
	artist = forms.CharField()
	unique_artist_url = forms.CharField()
	url_start = forms.CharField()
	url_stop = forms.CharField()
