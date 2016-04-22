# coding=utf8
import netease
import qq
import xiami
import douban


def get_provider_by_name(source):
    if source == 'netease':
        return netease
    if source == 'xiami':
        return xiami
    if source == 'qq':
        return qq
    if source == 'douban':
        return douban


def get_provider(item_id):
    provider_item = item_id.split('_')[0]
    if provider_item.startswith('ne'):
        return netease
    if provider_item.startswith('xm'):
        return xiami
    if provider_item.startswith('qq'):
        return qq
    if provider_item.startswith('db'):
        return douban


def get_provider_list():
    return [netease, xiami, qq, douban]
