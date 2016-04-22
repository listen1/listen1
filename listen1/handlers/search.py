# coding=utf8
import logging

from handlers.base import BaseHandler

from replay import get_provider_list

logger = logging.getLogger('listenone.' + __name__)


class SearchHandler(BaseHandler):
    def get(self):
        source = self.get_argument('source', '0')
        keywords = self.get_argument('keywords', '')
        result = dict(result=[])
        if keywords == '':
            self.write(result)

        provider_list = get_provider_list()

        index = int(source)
        if index >= 0 and index < len(provider_list):
            provider = provider_list[index]
            track_list = provider.search_track(keywords)
        else:
            track_list = []

        result = dict(result=track_list)
        self.write(result)
