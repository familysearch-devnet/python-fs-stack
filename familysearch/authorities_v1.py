"""
A module implementing the Authorities version 1 API module

Main class: AuthoritiesV1, meant to be mixed-in to the FamilySearch class
"""

try:
    import json
except ImportError:
    import simplejson as json

class AuthoritiesV1(object):

    """
    A mix-in implementing the Authorities version 1 endpoints
    """

    def __init__(self):
        """
        Set up the URLs for this AuthoritiesV1 object.
        """
        self.authorities_base = self.base + '/authorities/v1/'

    def place(self, place_id=None, options={}, **kw_options):
        """
        Get an authoritative representation of a place or list of places from FamilySearch.
        """
        if isinstance(place_id, list):
            place_id = ','.join(map(str, place_id))
        url = self.authorities_base + 'place'
        if place_id:
            url = self._add_subpath(url, str(place_id))
        if options or kw_options:
            url = self._add_query_params(url, options, **kw_options)
        response = json.load(self._request(url))['places']['place']
        response = self._remove_nones(response)
        if len(response) == 1:
            return response[0]
        else:
            return response

    def name(self, name=None, options={}, **kw_options):
        """
        Get an authoritative representation of a name or list of names from FamilySearch.
        """
        url = self.authorities_base + 'name'
        if name:
            kw_options['name'] = name
        if options or kw_options:
            url = self._add_query_params(url, options, **kw_options)
        response = json.load(self._request(url))['names']['name']
        response = self._remove_nones(response)
        if len(response) == 1:
            return response[0]
        else:
            return response

    def date(self, date=None, options={}, **kw_options):
        """
        Get an authoritative representation of a date or list of dates from FamilySearch.
        """
        url = self.authorities_base + 'date'
        if date:
            kw_options['date'] = date
        if options or kw_options:
            url = self._add_query_params(url, options, **kw_options)
        response = json.load(self._request(url))['dates']['date']
        response = self._remove_nones(response)
        if len(response) == 1:
            return response[0]
        else:
            return response

    def culture(self, culture_id=None, options={}, **kw_options):
        """
        Get an authoritative representation of a culture or list of cultures used by FamilySearch.
        """
        if isinstance(culture_id, list):
            culture_id = ','.join(map(str, culture_id))
        url = self.authorities_base + 'culture'
        if culture_id:
            url = self._add_subpath(url, str(culture_id))
        if options or kw_options:
            url = self._add_query_params(url, options, **kw_options)
        response = json.load(self._request(url))['cultures']
        response = self._remove_nones(response)
        if len(response) == 1:
            return response[0]
        else:
            return response

from . import FamilySearch
FamilySearch.__bases__ += (AuthoritiesV1,)
