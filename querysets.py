from mongoengine import *
from mongoengine.queryset.visitor import Q

class GuidingLandsQuery(QuerySet):

    def get_cards(self, gl_type):
        if gl_type == 'forest':
            return self.filter(Q(levels__forest__gte=6) & Q(available=True))
        elif gl_type == 'wildspire':
            return self.filter(Q(levels__wildspire__gte=6) & Q(available=True))
        elif gl_type == 'coral':
            return self.filter(Q(levels__coral__gte=6) & Q(available=True))
        elif gl_type == 'rotted':
            return self.filter(Q(levels__rotted__gte=6) & Q(available=True))
        elif gl_type == 'volcanic':
            return self.filter(Q(levels__volcanic__gte=6) & Q(available=True))
        elif gl_type == 'tundra':
            return self.filter(Q(levels__tundra__gte=6) & Q(available=True))
        else:
            return False