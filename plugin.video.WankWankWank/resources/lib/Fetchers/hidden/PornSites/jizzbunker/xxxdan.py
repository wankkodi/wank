import re

from ....catalogs.base_catalog import VideoSource, VideoNode
from .jizzbunker import JizzBunker


class XXXDan(JizzBunker):
    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://xxxdan.com/'

    def __init__(self, source_name='XXXDan', source_id=0, store_dir='.', data_dir='../Data',
                 source_type='Porn', use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(JizzBunker, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                         session_id)

    def _get_video_links_from_video_data_no_exception_check(self, video_data):
        """
        Extracts Video link from the video page without taking care of the exceptions (being done on upper level).
        :param video_data: Video data (dict).
        :return:
         """
        tmp_request = self.get_object_request(video_data)
        video_data = re.findall(r'(?:sources.push\()({.*})(?:\);)', tmp_request.text)
        video_links = re.findall(r'(?:src: *\')(.*?)(?:\')', video_data[0])
        video_links = [VideoSource(link=x) for x in video_links]
        return VideoNode(video_sources=video_links)

    @property
    def __version(self):
        return 0

    @property
    def _version_stack(self):
        return super(XXXDan, self)._version_stack + [self.__version]
