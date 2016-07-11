from django.conf import settings
from rest_framework import generics
from rest_framework import response
from rest_framework import status

from diamm.helpers.solr_pagination import SolrPaginator, SolrResultException
from diamm.models.data.search import Search


class SearchView(generics.GenericAPIView):
    template_name = "website/search/search.jinja2"

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', None)
        filters = {}
        sorts = {}

        if not query:
            return response.Response({})

        type_query = request.GET.get('type', None)

        # Saves recent searches in the user session
        if 'search_history' in request.session and request.session['search_history']['user'] != request.user.email \
                or 'search_history' not in request.session:
            user = None if not request.user.is_authenticated() else request.user.email
            request.session['search_history'] = {'user': user, 'searches': []}
        search = {'query': query, 'type': type_query, 'url': request.build_absolute_uri(), 'saved': False}
        if search not in request.session['search_history']['searches']:
            request.session['search_history']['searches'] = [search] + request.session['search_history']['searches'][:9]
            request.session.modified = True

        if not type_query or type_query == "all":
            filters.update({
                '{!tag=type}type': settings.SOLR['SEARCH_TYPES']
            })
        elif type_query and type_query in settings.SOLR['SEARCH_TYPES']:
            filters.update({
                '{!tag=type}type': type_query
            })
        elif type_query and type_query == "sources_with_images":
            filters.update({
                '{!tag=type}type': 'source',
                '{!tag=type}public_images_b': True
            })
        # else ignore any invalid type filter settings...

        try:
            page_num = int(request.GET.get('page', 1))
        except ValueError:
            page_num = 1

        try:
            paginator = SolrPaginator(query, filters, sorts, request)
            page = paginator.page(page_num)
        except SolrResultException as e:
            # We assume that an exception raised by Solr is the result of a bad request by the client,
            #  so we bubble up a 400 with a message about why it went wrong.
            return response.Response({'message': repr(e)}, status=status.HTTP_400_BAD_REQUEST)

        return response.Response(page.get_paginated_response())

class SaveSearch(generics.CreateAPIView):
    template_name = "rest_framework/api.html"

    def post(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return response.Response(status=status.HTTP_401_UNAUTHORIZED)
        if not request.POST.get('query'):
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
        if request.POST.get('save') == "True":
            search = Search(
                    user = request.user,
                    query = request.POST.get('query'),
                    query_type = request.POST.get('query_type'))
            search.save()
        else:
            search = Search.objects.get(
                    user=request.user,
                    query=request.POST.get('query'),
                    query_type=request.POST.get('query_type'))
            search.delete()
        return response.Response(status=status.HTTP_202_ACCEPTED)
