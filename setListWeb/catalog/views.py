from django.shortcuts import render
from django.http import HttpResponseRedirect
from catalog.forms import SearchForm
from setListWeb.visualizeSongsWeb import scrape

# Create your views here.
#from catalog.models import Book, Author, BookInstance, Genre

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    #num_books = Book.objects.all().count()
    #num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    #num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    #num_authors = Author.objects.count()

    #context = {
        #'num_books': num_books,
        #'num_instances': num_instances,
        #'num_instances_available': num_instances_available,
        #'num_authors': num_authors,
    #}

    # Render the HTML template index.html with the data in the context variable
    # TODO: Add context

    if request.method == 'POST':
        search_form = SearchForm(request.POST)

        if search_form.is_valid():
            #TODO: something something here for HttpResponse
            artist = ""
            unique = search_form.cleaned_data['unique_artist_url']
            url_start = search_form.cleaned_data['url_start']
            url_stop = search_form.cleaned_data['url_stop']

            scrape(artist, unique, url_start, url_stop)

            return HttpResponseRedirect('output')

    else:
        search_form = SearchForm()

    context = {
        'form': search_form,
    }

    return render(request, 'index.html', context)


def output(request):

    return render(request, 'output.html')

def tutorial(request):
    return render(request, 'tutorial.html')
