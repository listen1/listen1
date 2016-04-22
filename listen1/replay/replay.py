# coding=utf-8
'''
Basic Network Library.
'''
import logging
import os.path
import sys
import urllib
import urllib2

import StringIO
import gzip


logger = logging.getLogger('listenone.' + __name__)


########################################
# network
########################################
def chunk_report(bytes_so_far, chunk_size, total_size):
    percent = float(bytes_so_far) / total_size
    percent = round(percent * 100, 2)
    sys.stdout.write(
        "Downloaded %d of %d bytes (%0.2f%%)\r" %
        (bytes_so_far, total_size, percent))

    if bytes_so_far >= total_size:
        sys.stdout.write('\n')


def chunk_read(response, chunk_size=8192, report_hook=None):
    total_size = response.info().getheader('Content-Length').strip()
    total_size = int(total_size)
    bytes_so_far = 0

    total = ''
    while 1:
        chunk = response.read(chunk_size)
        bytes_so_far += len(chunk)

        if not chunk:
            break
        total += chunk
        if report_hook:
            report_hook(bytes_so_far, chunk_size, total_size)
    return total


def h(
        url, v=None, progress=False, extra_headers={},
        post_handler=None, return_post=False):
    '''
    base http request
    progress: show progress information
    need_auth: need douban account login
    '''
    logger.debug('fetching url:' + url)
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) ' + \
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86' + \
        ' Safari/537.36'
    headers = {'User-Agent': user_agent}
    headers.update(extra_headers)

    data = urllib.urlencode(v) if v else None
    req = urllib2.Request(url, data, headers)
    response = urllib2.urlopen(req)
    if progress:
        result = chunk_read(response, report_hook=chunk_report)
    else:
        result = response.read()
    if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO.StringIO(result)
        f = gzip.GzipFile(fileobj=buf)
        result = f.read()
    if post_handler:
        post_result = post_handler(response, result)
        if return_post:
            return post_result
    return result


def w(url, path, overwrite=False):
    '''
    write file from url to path
    use_cache: use file if already exists
    '''
    if os.path.isfile(path) and not overwrite:
        return
    c = h(url, progress=True)
    with open(path, 'wb') as f:
        f.write(c)
