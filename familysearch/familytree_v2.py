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
        """
        Set up the URLs for this FamilyTreeV2 object.
        """
        self.familytree_base = self.base + '/familytree/v2/'

    def _remove_nones(self, arg):
        """
        Remove all None values from a nested dict structure.

        This method exists because the FamilySearch API returns all attributes
        in a JSON response, with empty values set to null instead of being
        hidden from the response.

        """
        if isinstance(arg, dict):
            return dict([(k, self._remove_nones(v)) for (k, v) in arg.iteritems() if v is not None])
        elif isinstance(arg, list):
            return [self._remove_nones(i) for i in arg if i is not None]
        else:
            return arg

    def person(self, person_id=None, options={}, **kw_options):
        """
        Get a representation of a person or list of persons from the family tree.
        """
        if isinstance(person_id, list):
            person_id = ",".join(person_id)
        elif person_id == 'me':
            person_id = None
        url = self.familytree_base + 'person'
        if person_id:
            url = self._add_subpath(url, person_id)
        if options or kw_options:
            url = self._add_query_params(url, options, **kw_options)
        response = json.load(self._request(url))['persons']
        response = self._remove_nones(response)
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
        url = self.familytree_base + 'pedigree'
        if person_id:
            url = self._add_subpath(url, person_id)
        if options or kw_options:
            url = self._add_query_params(url, options, **kw_options)
        response = json.load(self._request(url))['pedigrees']
        response = self._remove_nones(response)
        if len(response) == 1:
            return response[0]
        else:
            return response

    def search(self, options={}, **kw_options):
        """
        Search for persons in the family tree.

        This method only supports GET parameters, not an XML payload.
        """
        url = self.familytree_base + 'search'
        if options or kw_options:
            url = self._add_query_params(url, options, **kw_options)
        return self._remove_nones(json.load(self._request(url))['searches'])

    def match(self, person_id=None, options={}, **kw_options):
        """
        Search for possible duplicates in the family tree.

        This method only supports GET parameters, not an XML payload.
        """
        if isinstance(person_id, list):
            person_id = ",".join(person_id)
        url = self.familytree_base + 'match'
        if person_id:
            url = self._add_subpath(url, person_id)
        if options or kw_options:
            url = self._add_query_params(url, options, **kw_options)
        return self._remove_nones(json.load(self._request(url))['matches'])

from . import FamilySearch
FamilySearch.__bases__ += (FamilyTreeV2,)
