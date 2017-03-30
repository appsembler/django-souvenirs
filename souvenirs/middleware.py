from __future__ import absolute_import, unicode_literals

from souvenirs.control import souvenez


class SouvenirsMiddleware(object):

    def process_request(self, request):
        if request.user.is_authenticated():
            souvenez(request.user)
