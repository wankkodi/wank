# Internet tools
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# re
import re

# JSON
import json


class Brightcove(object):
    player_js_template = 'https://players.brightcove.net/{aid}/{pid}_default/index.js'
    video_fetch_url = 'https://secure.brightcove.com/services/mobile/streaming/index/master.m3u8'
    video_fetch_url2_template = 'https://edge.api.brightcove.com/playback/v1/accounts/{aid}/videos/{vid}'
    video_playlist_template = 'https://edge.api.brightcove.com/playback/v1/accounts/{aid}/playlists/{pid}'
    live_video_request_url_template = 'https://edge.api.brightcove.com/playback/v1/accounts/{uid}/videos/{ref}'
    live_video_params_template = 'https://players.brightcove.net/{uid}/{lpid}_default/index.js'

    def __init__(self, session=None, user_agent=None):
        if session is not None:
            self.session = session
        else:
            retries = 3
            backoff_factor = 0.3
            status_forcelist = (500, 502, 504)

            self.session = requests.session()
            retry = Retry(
                total=retries,
                read=retries,
                connect=retries,
                backoff_factor=backoff_factor,
                status_forcelist=status_forcelist,
            )
            adapter = HTTPAdapter(max_retries=retry)
            self.session.mount('http://', adapter)
            self.session.mount('https://', adapter)

        self.user_agent = user_agent

    def fetch_live_video_raw_data(self, live_url, referer, bref):
        """
        Fetches live video raw data.
        :return:
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Referer': referer,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        req = self.session.get(live_url, headers=headers)
        uid = re.findall(r'(?:accountID: \')(.*?)(?:\')', req.text)
        assert len(uid) == 1
        live_player_id = re.findall(r'(?:livePlayerID: \')(.*?)(?:\')', req.text)
        assert len(live_player_id) == 1
        live_show_link = self.live_video_request_url_template.format(uid=uid[0], ref=bref)
        params_show_link = self.live_video_params_template.format(uid=uid[0], lpid=live_player_id[0])

        req = self.session.get(params_show_link)
        assert req.ok
        params = re.findall(r'(?:initPlugin\([\n ].*\'catalog\'[\n ]*, )({.*?})(?:[\n ]*\);)', req.text,
                            flags=re.DOTALL)
        if len(params) == 0:
            return []
        params = json.loads(params[0])

        headers = {
            'Access-Control-Request-Headers': 'accept',
            'Access-Control-Request-Method': 'GET',
            'Cache-Control': 'max-age=0',
            # 'Origin': self.base_url,
            'Referer': live_url,
            'Sec-Fetch-Mode': 'cors',
            'User-Agent': self.user_agent
        }
        req = self.session.options(live_show_link, headers=headers)
        assert req.ok
        headers = {
            'Accept': 'application/json;pk={pk}'.format(pk=params['policyKey']),
            # 'Origin': self.base_url,
            'Referer': live_url,
            'Sec-Fetch-Mode': 'cors',
            'User-Agent': self.user_agent
        }
        req = self.session.get(live_show_link, headers=headers)
        assert req.ok
        return req.json()

    def get_video_links(self, vid, secure):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            # 'Referer': self.shows_url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'User-Agent': self.user_agent
        }
        params = {u'videoId': vid, u'secure': secure}
        new_req = self.session.get(self.video_fetch_url, params=params, headers=headers)
        return new_req.text

    def get_video_links_alt(self, account_id, player_id, referer, video_id):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            # 'Referer': self.shows_url,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'User-Agent': self.user_agent
        }
        js_url = self.player_js_template.format(aid=account_id, pid=player_id)
        js_req = self.session.get(js_url, headers=headers)
        catalog_data = re.findall(r'(?:\'catalog\'\n *, )({.*})(?:\n)', js_req.text)
        if len(catalog_data) == 0:
            return []
        catalog_data = json.loads(catalog_data[0])
        headers = {
            'Accept': 'application/json;pk={pk}'.format(pk=catalog_data['policyKey']),
            # 'Origin': self.base_url,
            'Referer': referer,
            'Sec-Fetch-Mode': 'cors',
            'User-Agent': self.user_agent
        }
        new_url = \
            self.video_fetch_url2_template.format(aid=account_id,
                                                  vid=video_id)
        new_req = self.session.get(new_url, headers=headers)
        new_data = new_req.json()
        return new_data
