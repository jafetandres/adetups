from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet


class MyModelMixin(object):

    def q_for_search_word(self, word):
        return Q(socio__usuario__nombres__icontains=word) | Q(garante__usuario__nombres__icontains=word) | \
               Q(clasecredito__descripcion__icontains=word)

    def q_for_search(self, search):
        q = Q()
        if search:
            searches = search.split()
            for word in searches:
                q = q & self.q_for_search_word(word)
        return q

    def filter_on_search(self, search):
        return self.filter(self.q_for_search(search))


class MyModelQuerySet(QuerySet, MyModelMixin):
    pass


class MyModelManager(models.Manager, MyModelMixin):

    def get_queryset(self):
        return MyModelQuerySet(self.model, using=self._db)


class SocioMixin(object):
    def q_for_search_word(self, word):
        return Q(usuario__nombres__icontains=word) | Q(usuario__apellidos__icontains=word) | \
        Q(usuario__username__icontains=word)

    def q_for_search(self, search):
        q = Q()
        if search:
            searches = search.split()
            for word in searches:
                q = q & self.q_for_search_word(word)
        return q

    def filter_on_search(self, search):
        return self.filter(self.q_for_search(search))


class SocioQuerySet(QuerySet, SocioMixin):
    pass


class SocioManager(models.Manager, SocioMixin):

    def get_queryset(self):
        return SocioQuerySet(self.model, using=self._db)
