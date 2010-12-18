"""
A module implementing the Family Tree version 2 API module

Main class: FamilyTreeV2, meant to be mixed-in to the FamilySearch class
"""

try:
    import json
except ImportError:
    import simplejson as json

class FamilyTreeV2(object):

    """
    A mix-in implementing the Family Tree version 2 endpoints
    """

    def __init__(self):
        """Set up the URLs for this FamilyTreeV2 object."""
        familytree_base = self.base + '/familytree/v2/'
        self.person_url = familytree_base + 'person'
        self.pedigree_url = familytree_base + 'pedigree'
        self.search_url = familytree_base + 'search'
        self.match_url = familytree_base + 'match'

    def person(self, person_id=None, options={}, **kw_options):
        """
        Get a representation of a person or list of persons from the family tree.
        """
        if isinstance(person_id, list):
            person_id = ",".join(person_id)
        elif person_id == 'me':
            person_id = None
        url = self.person_url
        if person_id:
            url = self._add_subpath(url, person_id)
        if options or kw_options:
            url = self._add_query_params(url, options, **kw_options)
        response = json.load(self._request(url))['persons']
        if len(response) == 1:
            return response[0]
        else:
            return response

    def pedigree(self, person_id=None, options={}, **kw_options):
        """
        Get a pedigree for the given person or list of persons from the family tree.
        """
        if isinstance(person_id, list):
            person_id = ",".join(person_id)
        elif person_id == 'me':
            person_id = None
        url = self.pedigree_url
        if person_id:
            url = self._add_subpath(url, person_id)
        if options or kw_options:
            url = self._add_query_params(url, options, **kw_options)
        response = json.load(self._request(url))['pedigrees']
        if len(response) == 1:
            return response[0]
        else:
            return response

    def search(self, options={}, **kw_options):
        """
        Search for persons in the family tree.

        This method only supports GET parameters, not an XML payload.
        """
        url = self.search_url
        if options or kw_options:
            url = self._add_query_params(url, options, **kw_options)
        return json.load(self._request(url))['searches']

    def match(self, person_id=None, options={}, **kw_options):
        """
        Search for possible duplicates in the family tree.

        This method only supports GET parameters, not an XML payload.
        """
        if isinstance(person_id, list):
            person_id = ",".join(person_id)
        url = self.match_url
        if person_id:
            url = self._add_subpath(url, person_id)
        if options or kw_options:
            url = self._add_query_params(url, options, **kw_options)
        return json.load(self._request(url))['matches']

from . import FamilySearch
FamilySearch.__bases__ += (FamilyTreeV2,)
