from django.shortcuts import render

from .models import Book, Author, BookInstance, Genre

# Authenticated user view to see books on loan belonging to them 
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

# Import generic to implement class based views 

from django.views import generic

# Create your views here.

def index(request):
    """View function for home page of site."""

    # Genrate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default. 
    num_authors = Author.objects.count()

    num_genres = Genre.objects.count()

    num_titles_with_specific_word = Book.objects.filter(title__contains='the').count()

    # Added code - session information to track num_visits 
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_titles_with_specific_word': num_titles_with_specific_word,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'catalog/index.html', context=context)

## Class based views 

class BookListView(generic.ListView):
    model = Book

    paginate_by = 10

class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author

    paginate_by = 5

class AuthorDetailView(generic.DetailView):
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan due to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return(
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )

class LoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan for all users, librarian view only"""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    permission_required = 'catalog.can_mark_returned'

    def get_queryset(self):
        return(
            BookInstance.objects.filter(status__exact='o')
            .order_by('due_back')
        )
