# Internet tools
# from urllib.parse import urljoin
import requests
from .. import urljoin

# Parsing tool
# from lxml import etree
from .my_parser_wrapper import MyParser, html5lib

# User-Agent fetcher
from .user_agents import UserAgents

# Random
import random

# Time
import time

# Math
import math

# json
# import json
from .text_json_manioulations import prepare_json_from_not_formatted_text

# Regex
import re

# base 64
import base64


class ExternalSourceErrorModule(object):
    def __init__(self, site_name, url, message=None):
        self.site_name = site_name
        self.url = url
        self.message = message


class ExternalSourceError(ValueError):
    def __init__(self, request, error_module=None):
        super(ValueError, self).__init__(request)
        self.error_module = error_module


def base_n(num, b, numerals="0123456789abcdefghijklmnopqrstuvwxyz"):
    return ((num == 0) and numerals[0]) or (
            base_n(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])


class NoVideosException(ExternalSourceError):
    def __init__(self, request, error_module=None):
        super(NoVideosException, self).__init__(request)
        self.error_module = error_module

    def __str__(self):
        return repr('No videos Found for url {u}'.format(u=self.args))


class ExternalFetcher(object):
    def __init__(self, session=None, user_agent=None, parser=None, name='ExternalFetcher'):
        self.name = name
        self.session = session if session is not None else requests.session()

        if user_agent is not None:
            self.user_agents_manager = None
            self.user_agent = user_agent
        else:
            self.user_agents_manager = UserAgents()
            user_agents = self.user_agents_manager.get_latest_user_agents(num_of_pages=5, os_filter='Windows',
                                                                          common_filter='Very common')
            self.user_agent = random.choice(user_agents)[0]

        # self.parser = parser if parser is not None else \
        #     html5lib.html5parser.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("lxml"),
        #                                     namespaceHTMLElements=False)
        self.parser = MyParser(tree=html5lib.treebuilders.getTreeBuilder("etree"), namespaceHTMLElements=False) \
            if parser is None else parser

    def get_video_link_fembed(self, video_url):
        """
        Fetches very stream link
        :param video_url: very stream url
        :return:
        """
        tmp_url = 'https://www.fembed.com/api/source/{k}'.format(k=video_url.split('/')[-1])
        headers = {
            'Accept': '*/*',
            'Cache-Control': 'no-cache',
            # 'Host': self.host_name,
            'Origin': 'https://www.fembed.com',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        data = {
            'r': '',
            'd': 'www.fembed.com',
        }
        tmp_request = self.session.post(tmp_url, headers=headers, data=data)
        assert tmp_request.ok
        raw_data = tmp_request.json()

        return raw_data['data']

    def get_video_link_from_woof_tube(self, video_link):
        """
        Parses the video address from the woof tube server.
        :param video_link: Link to the video.
        :return:
        """
        video_header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            # 'Referer': new_video_data['url'],
            'Sec-Fetch-Mode': 'nested-navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_link, headers=video_header)
        tmp_tree = self.parser.parse(tmp_request.text)
        video_links = tmp_tree.xpath('.//p[@id="videolink"]/text()')
        if not tmp_request.ok or len(video_links) == 0:
            error_module = ExternalSourceErrorModule(self.name, video_links)
            raise NoVideosException(error_module.message, error_module)
        return [('https://woof.tube/gettoken/' + video_links[0] + '?mime=true'), 0]

    def get_video_link_from_protoawe(self, video_link):
        """
        Parses the video address from the protoawe server.
        :param video_link: Link to the video.
        :return:
        """
        video_header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            # 'Referer': new_video_data['url'],
            'Sec-Fetch-Mode': 'nested-navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_link, headers=video_header)
        new_video_link = re.findall(r'(?:iframeElement.src *= *\')(.*?)(?:\')', tmp_request.text)
        if not tmp_request.ok or len(new_video_link) == 0:
            error_module = ExternalSourceErrorModule(self.name, new_video_link)
            raise NoVideosException(error_module.message, error_module)

        new_video_link2 = urljoin(video_link, new_video_link[0])
        tmp_request = self.session.get(new_video_link2, headers=video_header)
        raw_data = re.findall(r'(?:window.playerConfig *= *)(.*?)(?:;)', tmp_request.text)
        if not tmp_request.ok or len(raw_data) == 0:
            error_module = ExternalSourceErrorModule(self.name, new_video_link2)
            raise NoVideosException(error_module.message, error_module)
        raw_data = prepare_json_from_not_formatted_text(raw_data[0])
        new_video_link3 = raw_data['contentProviderUrl'].replace('\\/', '/')

        video_header = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Referer': new_video_link2,
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        tmp_request = self.session.get(new_video_link3, headers=video_header)
        raw_data = tmp_request.json()
        if not tmp_request.ok or raw_data['success'] is False:
            error_module = ExternalSourceErrorModule(self.name, new_video_link)
            raise NoVideosException(error_module.message, error_module)

        return [(urljoin(new_video_link3, raw_data['data']['contentUrl']), 0)]

    def get_video_link_from_videyo_tube(self, video_link):
        """
        Parses the video address from the woof tube server.
        :param video_link: Link to the video.
        :return:
        """
        video_header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            # 'Referer': new_video_data['url'],
            'Sec-Fetch-Mode': 'nested-navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_link, headers=video_header)
        tmp_data = re.findall(r'(?:window.hola_player\()({.*?})(?:, function)', tmp_request.text, re.DOTALL)
        if not tmp_request.ok or len(tmp_data) == 0:
            error_module = ExternalSourceErrorModule(self.name, video_link)
            raise NoVideosException(error_module.message, error_module)
        res = prepare_json_from_not_formatted_text(tmp_data[0])
        return res

    def get_video_link_from_gotounlimited(self, video_link):
        """
        Parses the video address from the gotounlimited server.
        :param video_link: Link to the video.
        :return:
        """
        video_header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            # 'Referer': new_video_data['url'],
            'Sec-Fetch-Mode': 'nested-navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_link, headers=video_header)
        tmp_tree = self.parser.parse(tmp_request.text)
        raw_data = [x for x in tmp_tree.xpath('.//script') if x.text is not None and 'p,a,c,k,e,d' in x.text]
        if not tmp_request.ok or len(raw_data) == 0:
            error_module = ExternalSourceErrorModule(self.name, video_link)
            raise NoVideosException(error_module.message, error_module)
        new_raw_data = re.findall(r'(?:}\()(.*)(?:\)\))', raw_data[0].text)[0]

        var1, var2, var3, var4 = self._split_params(new_raw_data)
        var1 = var1[1:-1]
        var2 = int(var2)
        var3 = int(var3)
        if var4[-10:-5] == 'split':
            split_arg = var4[-3]
            var4 = var4[1:-12].split(split_arg)
        raw_func = self._get_info_from_packed_codding2(var1, var2, var3, var4, None, None)
        if 'sources:' in raw_func > 0:
            video_links = [(x, 0) for x in re.findall(r'(?:sources:\[")(.*?)(?:"\])', raw_func)]
        elif 'player.src' in raw_func:
            video_data = prepare_json_from_not_formatted_text(re.findall(r'(?:player\.src\()(\[.*\])(?:\))',
                                                                         raw_func)[0])
            video_links = [(x['src'], x['res']) for x in video_data]
        else:
            error_module = ExternalSourceErrorModule(self.name, tmp_request.url)
            raise NoVideosException(error_module.message, error_module)
        return video_links

    def get_video_link_from_vidlox(self, video_link, referer):
        """
        Parses the video address from the vidlox.me server.
        :param video_link: Link to the video.
        :param referer: Referer.
        :return:
        """
        video_header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            'Referer': referer,
            'Sec-Fetch-Dest': 'iframe',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_link, headers=video_header)
        tmp_data = re.findall(r'(?:Clappr.Player\()({.*?})(?:\);)', tmp_request.text, re.DOTALL)
        if not tmp_request.ok or len(tmp_data) == 0:
            error_module = ExternalSourceErrorModule(self.name, video_link)
            raise NoVideosException(error_module.message, error_module)
        raw_res = prepare_json_from_not_formatted_text(tmp_data[0])
        res = [(link, raw_res['levelSelectorConfig']['labels'][i]) for i, link in enumerate(raw_res['sources'][::-1])]
        if len(res) == 0:
            error_module = ExternalSourceErrorModule(self.name, video_link)
            raise NoVideosException(error_module.message, error_module)
        return res

    def get_video_link_from_verystream(self, video_url):
        """
        Fetches very stream link
        :param video_url: very stream url
        :return:
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_url, headers=headers)
        tmp_tree = self.parser.parse(tmp_request.text)

        source = tmp_tree.xpath('.//p[@id="videolink"]')
        if len(source) == 0:
            raise NoVideosException(video_url)
        videos = [('https://woof.tube/gettoken/' + source[0].text + '?mime=true', 0), 0]
        return videos

    def get_video_link_from_cdna(self, video_url):
        """
        Fetches stream link for cdna video.
        :param video_url: very stream url
        :return:
        """
        base_video_url_template = 'http://s{s}.cdna.tv/'
        video_subdir1 = 'p'
        video_subdir2 = 'vid/'
        video_subdir3 = '/'
        default_res = '720p'
        video_prefix_prefix = '_'
        video_suffix = '.mp4'

        server, raw_data, video_id, folder_id = self._get_video_link_from_cdna_general(video_url)
        v_put = str(folder_id) + video_subdir3 + str(video_id)
        video_urls = []
        for x in raw_data:
            video_url = (base_video_url_template.format(s=server) + video_subdir1 +
                         video_subdir2 + x[4] + video_subdir3 +
                         x[5] + video_subdir3 + v_put + video_subdir3 + video_id)
            prefix = '' if default_res == x[0] else video_prefix_prefix + x[0]
            video_url = video_url + prefix + video_suffix
            video_resolution = re.findall(r'\d+', x[0])[0]
            video_urls.append((video_url, video_resolution))

        return video_urls

    def _get_video_link_from_cdna_general(self, video_url):
        """
        Fetches stream link for cdna video.
        :param video_url: very stream url
        :return:
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        # Was taken from pornktube module (have the same engine.
        tmp_request = self.session.get(video_url, headers=headers)
        tmp_tree = self.parser.parse(tmp_request.text)
        server_data = tmp_tree.xpath('.//div[@id="player"]')

        if not tmp_request.ok or len(server_data) == 0:
            error_module = ExternalSourceErrorModule(self.name, video_url)
            raise NoVideosException(error_module.message, error_module)
        server = server_data[0].attrib['data-n']
        raw_data = [x.attrib['data-q'] for x in server_data]
        assert len(raw_data) == 1
        raw_data = [x.split(';') for x in raw_data[0].split(',')]
        # video_id = video_data['id']
        video_id = server_data[0].attrib['data-id']
        folder_id = int(1e3 * math.floor(int(video_id) / 1e3))

        return server, raw_data, video_id, folder_id

    def get_video_link_from_fapmedia(self, video_url):
        """
        Fetches stream link for cdna video.
        :param video_url: very stream url
        :return:
        """
        base_video_url_template = 'http://s{s}.fapmedia.com/'
        video_subdir2 = 'cqpvid/'
        video_subdir3 = '/'
        default_res = '720p'
        video_prefix_prefix = '_'
        video_suffix = '.mp4'
        server, raw_data, video_id, folder_id = self._get_video_link_from_cdna_general(video_url)
        v_put = str(folder_id) + video_subdir3 + str(video_id)
        video_urls = []
        for x in raw_data:
            video_url = (base_video_url_template.format(s=server) +
                         video_subdir2 + x[4] + video_subdir3 +
                         x[5] + video_subdir3 + v_put + video_subdir3 + video_id)
            prefix = '' if default_res == x[0] else video_prefix_prefix + x[0]
            video_url = video_url + prefix + video_suffix
            video_resolution = re.findall(r'\d+', x[0])[0]
            video_urls.append((video_url, video_resolution))

        return video_urls

    def get_video_link_from_full_beeg(self, video_url):
        """
        Fetches stream link for cdna video.
        :param video_url: very stream url
        :return:
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        mp3u_url = 'https://hqq.tv/player/get_md5.php'
        params = {
            'ver': 3,
            'secure': 0,
            'adb': 0,
            'v': 'L0F6SnJZc3hLMEpPR2piTnlodXNWZz09',
            'token': '',
            'gt': '0e0d41e33e3e0e1a0a1a401d22e6aaf6',
        }
        # mp3u_url = 'https://fullbeeg.com/player/embed_player.php'
        # params = {
        #     'vid': 'L0F6SnJZc3hLMEpPR2piTnlodXNWZz09',
        #     'http_referer': "https://xkeezmovies.com/video/hayli-sanders-rae-lil-black-full-scene/",
        #     'embed_from': '',
        #     'need_captcha': 1,
        #     'secure': 0,
        # }
        # Was taken from pornktube module (have the same engine.
        tmp_request = self.session.get(mp3u_url, headers=headers, params=params)
        # print('')
        # tmp_tree = self.parser.parse(tmp_request.text)
        # server = tmp_tree.xpath('.//div[@id="player"]/@data-n')[0]
        # raw_data = tmp_tree.xpath('.//div[@id="player"]/@data-q')
        # assert len(raw_data) == 1
        # raw_data = [x.split(';') for x in raw_data[0].split(',')]
        # # video_id = video_data['id']
        # video_id = tmp_tree.xpath('.//div[@id="player"]/@data-id')[0]
        # folder_id = int(1e3 * math.floor(int(video_id) / 1e3))
        # v_put = str(folder_id) + video_subdir3 + str(video_id)
        # video_urls = []
        # for x in raw_data:
        #     video_url = (base_video_url_template.format(s=server) + video_subdir1 +
        #                  video_subdir2 + x[4] + video_subdir3 +
        #                  x[5] + video_subdir3 + v_put + video_subdir3 + video_id)
        #     prefix = '' if default_res == x[0] else video_prefix_prefix + x[0]
        #     video_url = video_url + prefix + video_suffix
        #     video_urls.append((video_url, int(re.findall(r'\d+', x[0])[0])))
        #
        # video_data = sorted(video_urls, key=lambda y: int(y[1]), reverse=True)
        # video_data = [x[0] for x in video_data]
        # return video_data

    def get_video_link_from_vshare(self, video_url, referer):
        """
        Fetches stream link for cdna video.
        :param video_url: Vshare stream url.
        :param referer: Page referer.
        :return:
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            'Referer': referer,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_url, headers=headers)
        raw_data = re.findall(r'(?:eval\()(.*?)(?:\)\n)', tmp_request.text)
        assert len(raw_data) == 1
        raw_func = self._get_vshare_info(raw_data[0])

        # We prepare the data
        raw_commands = raw_func.split(';')
        assert len(raw_commands) == 5
        # Here we assume the format of the raw_function (String.fromCharCode)
        raw_codded_chars = re.findall(r'(?:=\[)([\d,]+)(?:\])', raw_commands[1])
        assert len(raw_codded_chars) == 1
        raw_codded_chars = [int(x) for x in raw_codded_chars[0].split(',')]
        const_subtract_factor = re.findall(r'\d+', raw_commands[2], re.DOTALL)
        assert len(const_subtract_factor) == 1
        const_subtract_factor = int(const_subtract_factor[0])
        res = ''.join(chr(x - const_subtract_factor) for x in raw_codded_chars)

        tree = self.parser.parse(res)
        trees = tree.xpath('.//source')
        assert len(trees) > 0
        video_links = [(x.attrib['src'], int(x.attrib['res']))
                       for x in trees if 'src' in x.attrib and 'res' in x.attrib]
        return video_links

    def get_video_link_from_fileone(self, video_url, referer):
        """
        Fetches stream link for cdna video.
        :param video_url: Vshare stream url.
        :param referer: Page referer.
        :return:
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            'Referer': referer,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_url, headers=headers)
        tmp_tree = self.parser.parse(tmp_request.text)
        video_links = tmp_tree.xpath('.//video/source')
        video_links = [(urljoin(tmp_request.url, x.attrib['src']),
                        int(re.findall(r'\d+', x.attrib['title'])[0]) if 'title' in x.attrib else 0)
                       for x in video_links if 'src' in x.attrib]
        return video_links

    def get_video_link_from_no_scam_hosting(self, video_url, referer):
        """
        Fetches stream link for cdna video.
        :param video_url: Vshare stream url.
        :param referer: Page referer.
        :return:
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            'Referer': referer,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_url, headers=headers)
        tmp_tree = self.parser.parse(tmp_request.text)
        tmp_video_links = tmp_tree.xpath('./body//div[@class="right"]/a')
        if not tmp_request.ok or len(tmp_video_links) == 0:
            error_module = ExternalSourceErrorModule(self.name, tmp_video_links)
            raise NoVideosException(error_module.message, error_module)

        video_links = []
        for video_link_data in tmp_video_links:
            resolution = int(re.findall(r'\d+', video_link_data.text)[0])
            video_link = urljoin(video_url, video_link_data.attrib['href'])
            tmp_request = self.session.get(video_link, headers=headers)
            tmp_tree = self.parser.parse(tmp_request.text)
            link = tmp_tree.xpath('.//video')
            if not tmp_request.ok or len(link) == 0:
                error_module = ExternalSourceErrorModule(self.name, video_links)
                raise NoVideosException(error_module.message, error_module)
            video_links.append((link[0].attrib['src'], resolution))
        return video_links

    def _get_vshare_info(self, raw_data):
        """
        Tries to fetch the server name
        :param raw_data: raw_data
        :return:
        """
        new_raw_data = re.findall(r'(?:}\()(\'.*)(?:\))', raw_data)
        assert len(new_raw_data) == 1
        new_raw_data = new_raw_data[0]

        var1 = re.findall(r'\'.*?\'', new_raw_data)[0]
        new_raw_data = new_raw_data.replace(var1 + ',', '')
        var1 = var1[1:-1]
        var2, var3, var4, var5, var6 = new_raw_data.split(',')
        var2 = int(var2)
        var3 = int(var3)
        var4 = re.findall(r'(?:\')(.*?)(?:\')', var4)[0].split('|')
        var5 = int(var5)
        var6 = {} if var6 == '{}' else None
        raw_func = self._get_info_from_packed_codding(var1, var2, var3, var4, var5, var6)

        return raw_func

    @staticmethod
    def _get_info_from_packed_codding(p, a, c, k, _, d):
        """
        Tries to encode the packed input.
        :return:
        """
        # Copy from yes_porn_please
        def conv(num, b):
            conv_str = "0123456789abcdefghijklmnopqrstuvwxyz"
            if num < b:
                return conv_str[num]
            else:
                return conv(num // b, b) + conv_str[num % b]

        def func1(cc, aa):
            val1 = '' if cc < aa else func1(int(cc / aa), aa)
            cc = cc % aa
            val2 = chr(cc + 29) if cc > 35 else conv(cc, 36)
            return val1 + val2

        def dummy_e(_, __):
            return '\\w+'

        e = func1
        # !''.replace(/^/,String) is True, this is tautology...
        if not str(''):
            while c:
                c -= 1
                d[e(c, a)] = k[c] or e(c, a)
            k = [lambda x: d[x[0]]]
            # e = lambda _, __: '\\w+'
            e = dummy_e
            c = 1

        while c:
            c -= 1
            if k[c]:
                p = re.sub(r'\b{f}\b'.format(f=e(c, a)), k[c], p)
        return p

    @staticmethod
    def _get_info_from_packed_codding2(p, a, c, k, _, __):
        """
        Tries to encode the packed input.
        :return:
        """
        while c:
            c -= 1
            if k[c]:
                p = re.sub(r'\b{f}\b'.format(f=base_n(c, a)), k[c], p)
        return p

    def get_video_link_from_ksplayer(self, video_url):
        """
        Fetches stream link for cdna video.
        :param video_url: very stream url
        :return:
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(video_url, headers=headers)
        raw_code = re.findall(r'(?:JuicyCodes.Run\()(.*?)(?:\))', tmp_request.text)
        if not tmp_request.ok or len(raw_code) == 0:
            error_module = ExternalSourceErrorModule(self.name, video_url)
            raise NoVideosException(error_module.message, error_module)
        raw_code = re.sub(r'" *\+ *"', '', raw_code[0])
        raw_code = re.sub(r'"', '', raw_code)
        raw_code = base64.b64decode(raw_code.encode("utf-8")).decode('utf-8')
        raw_code = re.findall(r'(?:eval\()(.*)(?:\))', raw_code)[0]
        # The structure is the same as in the vshare source...
        data = self._get_vshare_info(raw_code)
        files = re.findall(r'(?:"file": *")(.*?)(?:")', data)
        resolutions = re.findall(r'(?:"label": *")(.*?)(?:")', data)
        resolutions = [int(re.findall(r'\d+', x)[0]) for x in resolutions]
        assert len(files) == len(resolutions) and len(files) > 0
        video_links = list(zip(files, resolutions))
        return video_links

    def get_video_link_from_streamcherry(self, url):
        """
        Parses the streamcherry source and fetches the video link from there.
        :param url: URL.
        :return:
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(url, headers=headers)
        raw_data = re.findall(r'(?:srces.push\( *)({.*})(?:\);)', tmp_request.text)
        if not tmp_request.ok or len(raw_data) == 0:
            error_module = ExternalSourceErrorModule(self.name, url)
            raise NoVideosException(error_module.message, error_module)
        bitrate = int(re.findall(r'(?:bitrate:)(\d+)', raw_data[0])[0])
        raw_code = re.findall(r'(?:src:d\()(.*)(?:\))', raw_data[0])
        raw_code11 = re.findall(r'(?:\')(.*)(?:\')', raw_code[0])[0]
        raw_code12 = re.findall(r'(?:,)(\d+$)', raw_code[0])[0]

        new_raw_data = re.findall(r'(?:}\()(\'.*)(?:\)\))', tmp_request.text)
        assert len(new_raw_data) == 1
        new_raw_data = new_raw_data[0]

        var1 = re.findall(r'\'.*?(?<!\\)\'', new_raw_data)[0]
        new_raw_data = new_raw_data.replace(var1 + ',', '')
        var1 = var1[1:-1]
        var2, var3, var4, var5, var6 = new_raw_data.split(',')
        var2 = int(var2, 16)
        var3 = int(var3)
        var4 = re.findall(r'(?:\')(.*?)(?:\')', var4)[0].split('|')
        var5 = int(var5)
        var6 = {} if var6 == '{}' else None
        raw_func = self._get_info_from_packed_codding(var1, var2, var3, var4, var5, var6)
        param1, param2 = re.findall(r'(?:\d+\|)+\d', raw_func)

        res = self.streamcherry_d(raw_code11, raw_code12, param1, param2)
        return [urljoin(url, res), bitrate]

    def get_video_link_from_mixdrop(self, url):
        """
        Parses the Mixdrop source and fetches the video link from there.
        :param url: URL.
        :return:
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(url, headers=headers)

        new_raw_data = re.findall(r'(?:}\()(\'.*)(?:\)\))', tmp_request.text)
        if not tmp_request.ok or len(new_raw_data) == 0:
            error_module = ExternalSourceErrorModule(self.name, url)
            raise NoVideosException(error_module.message, error_module)
        new_raw_data = new_raw_data[0]

        var1 = re.findall(r'\'.*?(?<!\\)\'', new_raw_data)[0]
        new_raw_data = new_raw_data.replace(var1 + ',', '')
        var1 = var1[1:-1]
        var2, var3, var4, var5, var6 = new_raw_data.split(',')
        var2 = int(var2, 16)
        var3 = int(var3)
        var4 = re.findall(r'(?:\')(.*?)(?:\')', var4)[0].split('|')
        var5 = int(var5)
        var6 = {} if var6 == '{}' else None
        raw_func = self._get_info_from_packed_codding(var1, var2, var3, var4, var5, var6)
        new_url = [urljoin(url, re.findall(r'(?:MDCore.vsr=")(.*?)(?:")', raw_func)[0]), 720]

        return new_url

    @staticmethod
    def streamcherry_d(a, b, param1, param2,
                       param3='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='):
        _c = None

        def _bignf(_a, _b):
            return _a < _b

        def _uknst(_a, _b):
            return _a + _b

        def _xmjzt(_a, _b):
            return _a != _b

        def _igrai(_a, _b):
            return _a != _b

        def _wrqth(_a, _b):
            return _a + _b

        def _isrqd(_a, _b):
            return _a | _b

        def _nrfxr(_a, _b):
            return _a << _b

        def _bfusx(_a, _b):
            return _a & _b

        def _eguje(_a, _b):
            return _a >> _b

        def _rtbdl(_a, _b):
            return _a | _b

        def _sktia(_a, _b):
            return _a << _b

        def _tprod(_a, _b):
            return _a & _b

        def _eycrq(_a, _b):
            return _a ^ _b

        params1 = param1.split('|')

        _0x1598e0 = -1
        _0x59b81a = ''
        _0x2e4782 = -1
        _0x426d70 = -1
        _0x5a46ef = -1
        _0x3b6833 = -1
        _0x2c0540 = -1
        _0x29d5bf = -1
        _0x4a2f3a = -1
        # _0x184b8d = int(b, 16)
        _0x184b8d = int(b)
        k = ''
        for new_param1 in params1:
            if new_param1 == '0':
                _0x4a2f3a = 0
                _0x29d5bf = 0
                _0x3b6833 = 0
                _0x426d70 = 0
            elif new_param1 == '1':
                while _bignf(_0x1598e0, len(a)):
                    params2 = param2.split('|')
                    for new_param2 in params2:
                        if new_param2 == '0':
                            _0x59b81a = _uknst(_0x59b81a, chr(_0x2e4782))
                        elif new_param2 == '1':
                            if _xmjzt(_0x426d70, 64):
                                _0x59b81a = _uknst(_0x59b81a, chr(_0x5a46ef))
                        elif new_param2 == '2':
                            _0x29d5bf = k.index(a[_0x1598e0])
                            _0x1598e0 += 1
                        elif new_param2 == '3':
                            if _igrai(_0x3b6833, 64):
                                _0x59b81a = _wrqth(_0x59b81a, chr(_0x2c0540))
                        elif new_param2 == '4':
                            _0x2c0540 = _isrqd(_nrfxr(_bfusx(_0x29d5bf, 15), 4), _eguje(_0x3b6833, 2))
                        elif new_param2 == '5':
                            _0x2e4782 = _rtbdl(_nrfxr(_0x4a2f3a, 2), _eguje(_0x29d5bf, 4))
                        elif new_param2 == '6':
                            _0x4a2f3a = k.index(a[_0x1598e0])
                            _0x1598e0 += 1
                        elif new_param2 == '7':
                            _0x5a46ef = _sktia(_tprod(_0x3b6833, 3), 6) | _0x426d70
                        elif new_param2 == '8':
                            _0x426d70 = k.index(a[_0x1598e0])
                            _0x1598e0 += 1
                        elif new_param2 == '9':
                            _0x3b6833 = k.index(a[_0x1598e0])
                            _0x1598e0 += 1
                        elif new_param2 == '10':
                            _0x2e4782 = _eycrq(_0x2e4782, _0x184b8d)
                        else:
                            raise ValueError('Unexpected value')

            elif new_param1 == '2':
                a = re.sub(r'[^A-Za-z0-9+/=]', '', a)
            elif new_param1 == '3':
                # k = ''.join(k.split('')[::-1])
                k = k[::-1]
            elif new_param1 == '4':
                # k = ''.join(k.split('')[::-1])
                k = param3
            elif new_param1 == '5':
                _0x2e4782 = 0
                _0x2c0540 = 0
                _0x5a46ef = 0
            elif new_param1 == '6':
                _0x59b81a = ''
            elif new_param1 == '7':
                _0x1598e0 = 0
            elif new_param1 == '8':
                return _0x59b81a
            else:
                raise ValueError('Unexpected value')

    def get_video_link_from_openload(self, url):
        """
        Parses the streamcherry source and fetches the video link from there.
        :param url: URL.
        :return:
        """
        _c = None

        def _xxm(_a, _b):
            return _a < _b

        def _jla(_a, _b):
            return _a * _b

        def _azp(_a, _b):
            return _a + _b

        def _dod(_a, _b, _c):
            return _a(_b, _c)

        # def _poy(_a, _b):
        #     return _a in _b

        def _dkf(_a, _b):
            return _a(_b)

        def _tjf(_a, _b):
            return _a * _b

        def _hiz(_a, _b):
            return _a ^ _b

        def _wyx(_a, _b):
            return _a ^ _b

        def _faz(_a, _b):
            return _a ^ _b

        def _gcy(_a, _b):
            return _a % _b

        def _ucs(_a, _b):
            return _a < _b

        def _dhh(_a, _b):
            return _a * _b

        def _pqu(_a, _b):
            return _a / _b

        def _emz(_a, _b):
            return _a << _b

        def _zbd(_a, _b):
            return _a & _b

        def _lnk(_a, _b):
            return _a != _b

        def _dyi(_a, _b):
            return _a >> _b

        # def _woa(_a, _b):
        #     return _a in _b

        def _gzw(_a, _b):
            return _a < _b

        def _cbv(_a, _b):
            return _a << _b

        def _zft(_a, _b):
            return _a & _b

        def _tcv(_a, _b):
            return _a >= _b

        def _eak(_a, _b, _c):
            return _a(_b, _c)

        def _qhb(_a, _b):
            return _a >= _b

        def special_dollar(_id):
            res = tree.xpath('.//*[@*="' + _id[1:] + '"]')
            return res[0]

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        request = self.session.get(url, headers=headers)
        html = request.text
        # with open('tmp.html', 'rb') as fl:
        #     html = fl.read().decode()

        raw_params = re.findall(r'(?:var _0x9495 *= *\[)(.*?)(?:\])', html)
        raw_params = re.sub('\'', '', raw_params[0])
        raw_params = raw_params.split(',')
        raw_params = [''.join(bytearray.fromhex(y).decode() for y in x.split('\\x')[1:]) for x in raw_params]
        param1 = raw_params[6]
        param2 = raw_params[25]
        param3 = raw_params[33]

        tree = self.parser.parse(html)
        param4 = tree.xpath('.//p/@id')
        assert len(param4) == 2
        param5 = re.findall(r'(?:_1x4bfb36 *= *parseInt\(\')(.*?)(?:\', *)(\d+)(?:\) *)([+-])(?: *)(\d+)(?:;)', html)
        assert len(param5) == 1 and len(param5[0]) == 4
        param5 = (param5[0][0], param5[0][1], ''.join(param5[0][2:4]))
        param6 = re.findall(r'(?:_0x138ee5 *= *\')(.*?)(?:\')', html)
        assert len(param6) == 1
        param6 = ''.join(bytearray.fromhex(y).decode() for y in param6[0].split('\\x')[1:])
        param7 = re.findall(r'(?:_0x30725e, *\(parseInt\(\')(\d+?)(?:\', *)(\d+)(?:\) *)([-+])(?: *)(\d+)(?: *)'
                            r'([-+])(?: *)([\dx]+)(?: *)([-+])(?: *)(\d+)(?:\) */ *\()(\d+)(?: *)([-+])(?: *)'
                            r'([\dx]+)(?:\)\),)', html)
        assert len(param7) == 1 and len(param7[0]) == 11
        param7 = [x for x in param7[0]]
        for i in (5, 10):
            param7[i] = str(int(param7[i], 16))
        param7 = (param7[0], int(param7[1]), int(''.join(param7[2:4])), int(''.join(param7[4:6])),
                  int(''.join(param7[6:8])), int(param7[8]), int(''.join(param7[9:11])))

        _0x1bf6e5 = ''
        _0x439a49 = ''
        _0x5d72cd = ''
        _0x31f4aa = ''
        _0x3d7b02 = ''
        _0x896767 = ''
        _0x3fa834 = ''
        _0x531f91 = ''
        _0x41e0ff = 0
        _0x5eb93a = 0
        _0x37c346 = 0
        _0x145894 = 0
        _0x30725e = 0
        _1x4bfb36 = 0
        _0x1a0e90 = 0
        _0x2de433 = 0
        _0x1a9381 = 0
        _0x3d9c8e = 0
        _0x1a873b = 0
        _0x332549 = 0
        _0x1fa71e = 0
        # _0x184b8d = int(b)
        # special_dollar = '640K ought to be enough for anybody'
        _0x31f4aa = {}
        for new_param1 in param1.split('|'):
            if new_param1 == '0':
                _0x1bf6e5 = ''
            elif new_param1 == '1':
                i = 0
                while _xxm(i, len(_0x439a49)):
                    _0x41e0ff = _jla(i, 8)
                    _0x40b427 = _0x439a49[i:_azp(i, 8)]
                    _0x577716 = _dod(int, _0x40b427, 0x10)
                    # if not _poy()
                    # Something to do with window...
                    # _0x577716 = 0
                    _0x31f4aa['ke'].append(_0x577716)
                    # params2 = param2.split('|')
                    i += 8
            elif new_param1 == '2':
                _0x439a49 = _0x5d72cd[0: _0x41e0ff]
            elif new_param1 == '3':
                _0xccbe62 = len(_0x5d72cd)
            elif new_param1 == '4':
                _0x3d7b02 = _0x31f4aa['ke']
            elif new_param1 == '5':
                _0x5d72cd = _0x5d72cd[_0x41e0ff:]
            elif new_param1 == '6':
                _0x439a49 = 0
            elif new_param1 == '7':
                # todo: not sure about that...
                _0x1bf6e5 = re.sub(r'\$*$', '', _0x1bf6e5)
                # _dkf(special_dollar, '#' + param4[1])
                # _dkf(special_dollar, '#' + param4[1]).text(_0x1bf6e5)
            elif new_param1 == '8':
                _0x41e0ff = _jla(9, 8)
            elif new_param1 == '9':
                _0x3d7b02 = []
            elif new_param1 == '10':
                while _xxm(_0x439a49, len(_0x5d72cd)):
                    for _0x2d6ce4 in param6.split('|'):
                        if _0x2d6ce4 == '0':
                            _0x896767 = 0
                        elif _0x2d6ce4 == '1':
                            _0x2de433 = _azp(_tjf(_0x5eb93a, 2), _0x37c346)
                        elif _0x2d6ce4 == '2':
                            _0x145894 += 1
                        elif _0x2d6ce4 == '3':
                            _0x30725e = _hiz(_wyx(_0x30725e,
                                                  int((int(param7[0], param7[1]) + param7[2] + param7[3] + param7[4]) /
                                                      (param7[5] + param7[6]))),
                                             _1x4bfb36)
                        elif _0x2d6ce4 == '4':
                            # 0x28a28dec = 681741804
                            _0x59ce16 = 0x28a28dec
                        elif _0x2d6ce4 == '5':
                            # 0x40 = 64
                            _0x5eb93a = 0x40
                        elif _0x2d6ce4 == '6':
                            _0x30725e = _faz(_0x896767, _0x3d7b02[_gcy(_0x145894, 9)])
                        elif _0x2d6ce4 == '7':
                            i = 0
                            while _ucs(i, 4):
                                # _0x444853 = _0x5949(13)[_0x5949(1)].split('|')
                                for _0x3d6c21 in param2.split('|'):
                                    if _0x3d6c21 == '0':
                                        _0x1a0e90 = int(_dhh(_pqu(_0x41e0ff, 0x9), i))
                                    elif _0x3d6c21 == '1':
                                        _0x2de433 = _emz(_0x2de433, int(_pqu(_0x41e0ff, 0x9)))
                                    elif _0x3d6c21 == '2':
                                        _0x1a9381 = _zbd(_0x30725e, _0x2de433)
                                    elif _0x3d6c21 == '3':
                                        if _lnk(_0x3fa834, special_dollar):
                                            _0x1bf6e5 += _0x3fa834
                                    elif _0x3d6c21 == '4':
                                        _0x3fa834 = chr(_0x1a9381 - 1)
                                    elif _0x3d6c21 == '5':
                                        _0x1a9381 = _dyi(_0x1a9381, _0x1a0e90)
                                    else:
                                        raise ValueError('Unexpected value')

                                i += 1

                        elif _0x2d6ce4 == '8':
                            _0x37c346 = 0x7f
                        elif _0x2d6ce4 == '9':
                            _0x31f4aa = {'mm': 0x80, 'xx': 0x3f}
                        elif _0x2d6ce4 == '10':
                            while 1:
                                # _0x5949('0x1b') = param3
                                for _0x204cab in param3.split('|'):
                                    if _0x204cab == '0':
                                        _0x439a49 += 1
                                    elif _0x204cab == '1':
                                        _0x1a873b += 6
                                    elif _0x204cab == '2':
                                        # Something to do with document
                                        # if not _wda()...
                                        # _0x3d9c8e += 10
                                        # _0x31f4aa['xx'] = 0x11
                                        if _gzw(_0x1a873b, _dhh(6, 5)):
                                            _0x332549 = _zbd(_0x3d9c8e, _0x31f4aa['xx'])
                                            _0x896767 += _cbv(_0x332549, _0x1a873b)
                                        else:
                                            _0x332549 = _zft(_0x3d9c8e, _0x31f4aa['xx'])
                                            _0x896767 += _dhh(_0x332549, int(math.pow(2, _0x1a873b)))
                                    elif _0x204cab == '3':
                                        _0x1fa71e = _0x5d72cd[_0x439a49:_azp(_0x439a49, 2)]
                                    elif _0x204cab == '4':
                                        if _tcv(_azp(_0x439a49, 1), len(_0x5d72cd)):
                                            _0x5eb93a = 0x8f
                                    elif _0x204cab == '5':
                                        _0x439a49 += 1
                                    elif _0x204cab == '6':
                                        _0x3d9c8e = _eak(int, _0x1fa71e, 0x10)
                                        # _0x3d9c8e = _eak(int, _0x1fa71e, 16)
                                    else:
                                        raise ValueError('Unexpected value')

                                if not _qhb(_0x3d9c8e, _0x5eb93a):
                                    break
                        elif _0x2d6ce4 == '11':
                            _1x4bfb36 = int(param5[0], int(param5[1])) + int(param5[2])
                        elif _0x2d6ce4 == '12':
                            _0x1a873b = 0
                        elif _0x2d6ce4 == '13':
                            _0x3d9c8e = 0
                        else:
                            raise ValueError('Unexpected value')

            elif new_param1 == '11':
                _0x531f91 = _dkf(special_dollar, _azp('#', param4[0])).text
            elif new_param1 == '12':
                _0x5d72cd = ord(_0x531f91[0])
            elif new_param1 == '13':
                _0x5d72cd = _0x531f91
            elif new_param1 == '14':
                _0x41e0ff = _dhh(9, 8)
            elif new_param1 == '15':
                _0x145894 = 0
            elif new_param1 == '16':
                _0x31f4aa = {'k': _0x439a49, 'ke': []}

            else:
                raise ValueError('Unexpected value')
        final_url = 'https://oload.vip/stream/' + _0x1bf6e5 + '?mime=true'
        return [final_url, 0]

    def get_video_link_from_pvideo(self, url):
        """
        Parses the streamcherry source and fetches the video link from there.
        :param url: URL.
        :return:
        """

    def get_video_link_from_hqq_tv(self, url, referer):
        """
        Parses the streamcherry source and fetches the video link from there.
        :param url: URL.
        :param referer: Page referer.
        :return:
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            'Referer': referer,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        request = self.session.get(url, headers=headers)
        videokey = re.findall(r'(?:videokey = ")(.+?)(?:")', request.text)
        if not request.ok or len(videokey) == 0:
            error_module = ExternalSourceErrorModule(self.name, url)
            raise NoVideosException(error_module.message, error_module)
        videokey = videokey[0]
        referer = base64.b64encode(referer.encode("utf-8")).decode('utf-8')
        headers = {
            'Accept': '*/*',
            'Cache-Control': 'max-age=0',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': url,
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        params = {
            'mode': 'insertLog',
            'videokey': videokey,
            'referer': referer,
            'adblock': 1,
        }
        post_req = self.session.post('https://pbtube.co/ajax.php', headers=headers, data=params)
        assert post_req.ok
        adb = re.findall(r'(?:var adb = \')(.+?)(?:\')', request.text)
        if not request.ok or len(adb) == 0:
            error_module = ExternalSourceErrorModule(self.name, url)
            raise NoVideosException(error_module.message, error_module)
        adb = adb[0]

        # link_m3u8 = "/player/get_md5.php?ver=3&secure=0&adb=" + adb + "&v=" + "UTZ5azY5YkZRM3lNSnF0K3hrM0Nqdz09" +\
        #             "&token="+encodeURIComponent(token)+"&gt=";
        link_m3u8 = "/player/get_md5.php?ver=3&secure=0&adb=" + adb + "&v=" + "UTZ5azY5YkZRM3lNSnF0K3hrM0Nqdz09" +\
                    "&token="+''+"&gt="
        link_m3u8 = urljoin(url, link_m3u8)

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        # mp3u_url = 'https://hqq.tv/player/get_md5.php'
        params = {
            'ver': 3,
            'secure': 0,
            'adb': 0,
            'v': 'L0F6SnJZc3hLMEpPR2piTnlodXNWZz09',
            'token': '',
            'gt': '0e0d41e33e3e0e1a0a1a401d22e6aaf6',
        }
        tmp_request = self.session.get(link_m3u8, headers=headers, params=params)
        if not tmp_request.ok:
            error_module = ExternalSourceErrorModule(self.name, url)
            raise NoVideosException(error_module.message, error_module)

        return tmp_request

    @staticmethod
    def _split_params(raw_params):
        """
        Split the textual parameters
        """
        res = []
        cnt = 0
        start_i = 0
        for i, c in enumerate(raw_params):
            if c == '\'':
                if cnt == 0:
                    # Beginning of the quote
                    cnt += 1
                else:
                    # End of quote
                    cnt -= 1
            if c == ',' and cnt == 0:
                # Outside of the quote
                res.append(raw_params[start_i:i])
                start_i = i + 1
        if start_i < len(raw_params):
            res.append(raw_params[start_i:])
        return res


class KTMoviesFetcher(ExternalFetcher):
    def __init__(self, session=None, user_agent=None, parser=None, name='TKMovies', ):
        super(KTMoviesFetcher, self).__init__(session, user_agent, parser, name)

    def _find_correct_url(self, video_data):
        """
        Finds the correct url from raw url.
        :param video_data: Video data.
        :return:
        """
        # print('a')
        c = []
        for a, v in video_data.items():
            b = None
            if type(v) is not str:
                continue
            if v[0:8] == 'function':
                b = v[8:]
            if b is not None and b[0] == '/':
                # print((a, b[1:]))
                c.append((a, b[1:]))
        if len(c) == 0:
            self._find_correct_url4(video_data)
            return

        video_data['innerHTML'] = ''
        self._find_correct_url2(video_data, c)

        # t = Timer(0.02, self._find_correct_url3, (video_data, c))
        # t.start()
        # self._find_correct_url3(video_data, c)
        self._find_correct_url3(video_data, c)
        time.sleep(0.02)

        # t3 = Timer(0.07, self._find_correct_url4, (video_data,))
        # t3.start()
        self._find_correct_url4(video_data)

        # if all('function' not in video_data[x[0]] for x in c):
        #     return
        # else:
        time.sleep(50 / 1000)
        # t2 = Timer(0.05, self._find_correct_url, (video_data, ))
        # t2.start()
        # t2.join()
        return self._find_correct_url(video_data)

    @staticmethod
    def _cb(_a, _b=None):
        if not _a:
            return None
        if _b is not None:
            _a['innerHTML'] = str(_b)
        return _a['innerHTML']

    @staticmethod
    def _find_correct_url2(video_data, a):
        """
        Finds the correct url from raw url.
        :param video_data: Video data.
        :return:
        """

        # bR = substring, bQ = length, bN(a) = f[a-3], bH(a) = f[a+1], bM(a) = f[a-2],
        # bP = (new Date).getTime() = int(time.time() * 1000)
        # cB(a, b) = if not a: return bH(-1), else: of typeof(b) != bN(114) a.innerHTML = b, return a.innerHTML
        def _by(*args):
            return ''.join((str(x) for x in args))

        bi = video_data
        e = video_data
        # a = [('video_url', re.findall(r'(?:fucntion/)(.*)', new_video_data['video_url'])[0])]
        # if 'video_alt_url' in new_video_data:
        #     a.append(('video_alt_url', re.findall(r'(?:fucntion/)(.*)', new_video_data['video_alt_url'])[0]))

        k = int(time.time() * 1000)

        for ii, aa in enumerate(a):
            c = 0
            h = aa[1].index('/')
            if h > 0:
                i = int(aa[1][0:h])
                h = aa[1][h:]
            else:
                i = 0
                h = aa[1]
            while c < 12:
                g = i
                j = int(time.time() * 1000)
                for d in aa[1]:
                    f = int(d) if d.isdigit() else 0
                    g += c * f
                g = math.floor(g / 7) if int(time.time() * 1000) - j > 100 else math.floor(g / 6)
                KTMoviesFetcher._cb(bi, int(KTMoviesFetcher._cb(bi) or 0) + g)
                if int(time.time() * 1000) - k > 1e3:
                    KTMoviesFetcher._cb(bi, math.floor(int(KTMoviesFetcher._cb(bi) or 0) / 2))
                c += 1

            # bM(49) == 'function
            if e[aa[0]] and e[aa[0]][0:8] == 'function':
                f = int(KTMoviesFetcher._cb(bi))
                if f < 0:
                    # f = '' + str(-f)
                    f = str(-f)
                    for c in range(4):
                        f += f
                    h = h[1:]
                    h = h.split('/')
                    for c in range(len(h[5])):
                        g = c
                        for d in range(len(f)):
                            g += int(f[d])
                        while g >= len(h[5]):
                            g -= len(h[5])
                        i = h[5][c]
                        h[5] = _by(h[5][0:c], h[5][g], h[5][c + 1:])
                        h[5] = _by(h[5][0:g], i, h[5][g + 1:])
                    e[aa[0]] = '/'.join(h)
                else:
                    e[aa[0]] = _by('function', '/', f, h)
        return e

    @staticmethod
    def _find_correct_url3(video_data, a):
        """
        Finds the correct url from raw url.
        :param video_data: Video data.
        :return:
        """
        # print('correct_url3')
        # bR = substring, bQ = length, bN(a) = f[a-3], bH(a) = f[a+1], bM(a) = f[a-2],
        # bP = (new Date).getTime() = int(time.time() * 1000)
        # cB(a, b) = if not a: return bH(-1), else: of typeof(b) != bN(114) a.innerHTML = b, return a.innerHTML
        for b, v in enumerate(a):
            c = 0
            while c < 12:
                f = 0
                g = int(time.time() * 1000)
                for c, u in enumerate(v[1]):
                    e = int(u) if u.isdigit() else 0
                    f += c * e
                f = math.floor(f / 7) if int(time.time() * 1000) - g < 100 else math.floor(f / 6)
                KTMoviesFetcher._cb(video_data, int(KTMoviesFetcher._cb(video_data) or 0) - f)
                c += 1

    @staticmethod
    def _find_correct_url4(video_data):
        """
        Finds the correct url from raw url.
        :param video_data: Video data.
        :return:
        """
        b = 'function/'
        c = 'code'
        # d = '16px'
        d_int = 16
        for x, v in video_data.items():
            if type(v) is not str:
                continue
            if v[0:9] == b:
                g = v[9:].split('/')
                # print(g)
                if g[0].isdigit() and int(g[0]) > 0:
                    h = g[6][0:2 * d_int]
                    i = KTMoviesFetcher._do_some_magic(video_data, c, d_int) if KTMoviesFetcher._do_some_magic else ''
                    if i and h:
                        j = h
                        for k in range(len(h))[::-1]:
                            ll = k
                            for m in range(k, len(i)):
                                ll += int(i[m])
                            while ll >= len(h):
                                ll -= len(h)
                            n = ''
                            for o in range(len(h)):
                                n += h[ll] if o == k else (h[k] if o == ll else h[o])
                            h = n
                        g[6] = g[6].replace(j, h)
                        g = g[1:]
                        video_data[x] = b[-1].join(g)

    @staticmethod
    def _do_some_magic(a, b, c):
        d = ""
        o = int

        for e in a:
            if b in e and len(a[e]) == o(c):
                d = a[e]
                # print(d)
                break

        if d:
            f = ""
            for g in range(1, len(d)):
                f += str(o(d[g])) if d[g].isdigit() and int(d[g]) > 0 else str(1)
            j = o(len(f) / 2)
            k = o(f[0:j + 1])
            ll = o(f[j:])
            g = ll - k
            if g < 0:
                g = -g
            f = g
            g = k - ll
            if g < 0:
                g = -g
            f += g
            f *= 2
            f = str(f)
            i = o(c) / 2 + 2
            m = ""
            for g in range(j + 1):
                for h in range(1, 4 + 1):
                    n = o(d[g + h]) + o(f[g])
                    if n >= i:
                        n -= i
                    m += str(int(n))
            return m

        return d

    def get_video_link(self, url):
        """
        Parses the streamcherry source and fetches the video link from there.
        :param url: URL.
        :return:
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3*',
            'Cache-Control': 'max-age=0',
            # 'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        tmp_request = self.session.get(url, headers=headers)
        raw_data = re.findall(r'(?:var flashvars = )({.*?})(?:;)', tmp_request.text, re.DOTALL)
        if not tmp_request.ok or len(raw_data) == 0:
            error_module = ExternalSourceErrorModule(self.name, url)
            raise NoVideosException(error_module.message, error_module)
        raw_data = prepare_json_from_not_formatted_text(raw_data[0])

        self._find_correct_url(raw_data)
        video_links = [raw_data['video_url'] + '?rnd=' + str(raw_data['rnd'])]
        resolution = re.findall(r'\d+', raw_data['video_url_text']) if 'video_url_text' in raw_data else []
        video_resolution = [resolution[0] if len(resolution) > 0 else None]
        i = 1
        while 1:
            new_video_field = 'video_alt_url{i}'.format(i=i if i != 1 else '')
            new_text_field = 'video_alt_url{i}_text'.format(i=i if i != 1 else '')
            is_redirect_field = 'video_alt_url{i}_redirect'.format(i=i if i != 1 else '')
            if new_video_field in raw_data:
                if is_redirect_field not in raw_data:
                    video_links.append(raw_data[new_video_field] + '?rnd=' + str(raw_data['rnd']))
                    resolution = re.findall(r'\d+', raw_data[new_text_field]) if new_text_field in raw_data else []
                    video_resolution.append(resolution[0] if len(resolution) > 0 else None)
                i += 1
            else:
                break

        return video_links, video_resolution


if __name__ == '__main__':
    user_agent_manager = UserAgents('../Data')
    # a = ExternalFetcher(user_agent=user_agent_manager.get_user_agent())
    # a.get_video_link_from_full_beeg('')
    # a.get_video_link_from_hqq_tv('https://hqq.tv/player/embed_player.php?'
    #                              'vid=RWlmcnR2ZWdJb1lSc2pPd1B3S2tLdz09&autoplay=no',
    #                              'https://netpornsex.net/bangbus-nerdy-girl-gets-fucked-hard/')

    a = KTMoviesFetcher(user_agent=user_agent_manager.get_user_agent())
    res = a.get_video_link('https://www.hdtube.porn/videos/youngster-fucks-girlfriend-s-stepmom-'
                           'from-behind-after-blowjob/',)
    print(res)
