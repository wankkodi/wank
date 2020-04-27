# Internet tools
import requests

# Playlist tools
import m3u8

# Multithreading
from .multithreading import ThreadPool
try:
    import multiprocessing as mp
except ImportError:
    mp = None

# OS
from os import remove

# Warnings and exceptions
import warnings

# Youtube
# from pytube import YouTube
# from pytube import exceptions as youtube_exceptions
from youtube_dl import YoutubeDL
from youtube_dl.utils import DownloadError

# Subprocess
import subprocess

# Math
from math import ceil

# System sleep
from time import sleep

# Internet tools
from .. import urljoin, urlparse


class VideoFetchTools(object):
    CHUNK_SIZE = 3 * 2 ** 20  # bytes
    DOWNLOAD_CHUNK_SIZE = 3 * 2 ** 20  # bytes

    def __init__(self, session=None):
        self.session = session if session is not None else requests.session()

    @staticmethod
    def get_list_of_fragments_from_m3u8(m3u8_url):
        """
        Get all the possible video fragments in the given url of m3u.
        :param m3u8_url: address of m3u file.
        :return: lists of urls and durations of video fragments.
        """
        m3u8_obj = m3u8.load(m3u8_url)
        urls = [x.absolute_uri for x in m3u8_obj.segments]
        durations = [x.duration for x in m3u8_obj.segments]
        cumulative_durations = [x.duration for x in m3u8_obj.segments]
        for i in range(1, len(durations)):
            cumulative_durations[i] = cumulative_durations[i-1] + durations[i]

        return urls, durations, cumulative_durations

    def get_video_from_segments(self, video_data, video_i, filename):
        """
        Fetches the video.
        :param video_data: VideoNode object.
        :param video_i: Video stream index.
        :param filename: Store Filename.
        :return: Video m3u8 (m3u8 object).
        """
        video_link = video_data.video_sources[video_i]
        req = self.session.get(url=video_link.link,
                               headers=video_data.headers if video_data.headers is None else self.session.headers,
                               json=video_data.json,
                               params=video_data.params,
                               data=video_data.query_data,
                               verify=video_data.verify)
        if req.status_code != 200:
            raise RuntimeError('Wrong download status for url {u}. Got {s}'.format(u=video_link.link,
                                                                                   s=req.status_code))
        video_m3u8 = m3u8.loads(req.text)

        ts_urls = [x.uri if urlparse(x.uri).hostname is not None else urljoin(video_link.link, x.uri)
                   for x in video_m3u8.segments]
        raw_data = self.merge_ts_fragments(ts_urls, verbose=1)
        with open(filename, 'wb') as f:
            f.write(raw_data)

        return filename

    def get_video(self, video_data, video_i, filename):
        """
        Fetches the video.
        :param video_data: VideoNode object.
        :param video_i: Video stream index.
        :param filename: Store Filename.
        :return: Video m3u8 (m3u8 object).
        """
        video_link = video_data.video_sources[video_i]
        # req = self.session.get(video_link, headers=headers)
        # if req.status_code not in (200, 201, 206):
        #     warnings.warn('Wrong download status for url {u}. Got {s}'.format(u=video_link, s=req.status_code))
        #     continue
        #     return req.content

        # NOTE the stream=True parameter below
        with self.session.get(video_link.link,
                              headers=video_data.headers
                              if video_data.headers is not None else self.session.headers,
                              stream=True,
                              json=video_data.json,
                              cookies=video_data.cookies if video_data.json is not None else self.session.cookies,
                              params=video_data.params,
                              data=video_data.query_data,
                              verify=video_data.verify) as r:
            if not r.ok:
                # If we are here, something went wrong
                raise RuntimeError('Could not fetch any video!')
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=self.DOWNLOAD_CHUNK_SIZE):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        # f.flush()
        return filename

    def merge_ts_fragments(self, urls, verbose=0, num_of_threads=10):
        """
        Merge the ts short fragments onto one file
        :param urls: list of urls with the ts fragments.
        :param verbose: verbose level:
        0 - no output text.
        1 - print the number of segment we are dealing with.
        :param num_of_threads: number of threads we want to download in parallel.
        num_of_threads
        :return:
        """

        # open one ts_file from the list after another and append them to merged.ts
        def download_segment_in_parallel(loc_i, loc_ts_url, loc_store_data):
            ts_data = self.session.get(loc_ts_url)
            assert ts_data.status_code == 200, 'Wrong download status. Got {s}'.format(s=ts_data.status_code)

            if verbose > 0:
                print('Downloading segment number {nm} out of {tnm}.'.format(nm=loc_i, tnm=len(urls)))
                loc_store_data[loc_i] = ts_data.content

        store_data = {i: None for i in range(len(urls))}
        workers = ThreadPool(num_of_threads)  # 100 is the number of threads
        for i, ts_url in enumerate(urls):
            workers.add_task(download_segment_in_parallel, i, ts_url, store_data)
        workers.wait_completion()  # not needed, only if you need to be certain all work is done before continuing

        data = b''
        for i in range(len(urls)):
            data += store_data[i]

        return data

    def combine_youtube_video(self, video_links, audio_links, filename):
        """
        Combines the audio and videos streams into the file.
        :param video_links: List of video links objects.
        :param audio_links: List of audio audio objects.
        :param filename: Save filename.
        :return: None.
        """
        video_filename = None
        audio_filename = None
        # Fetching video
        for stream in video_links:
            try:
                video_filename = 'tmp_video.mp4'
                # stream.download(filename=video_filename)
                self._download_youtube_video(stream, video_filename)
            except DownloadError:
                warnings.warn('Cannot download the url {u}. Trying the next one'.format(u=stream))
                continue
            break

        # Fetching audio
        for stream in audio_links:
            try:
                audio_filename = 'tmp_audio.mp4'
                # stream.download(filename=video_filename)
                self._download_youtube_video(stream, audio_filename)
            except DownloadError:
                warnings.warn('Cannot download the url {u}. Trying the next one'.format(u=stream))
                continue
            break

        # Combining
        new_video = None
        output_filename = None
        if video_filename is not None and audio_filename is not None:
            output_filename = 'new_tmp_video.mp4'
            cmd = 'ffmpeg -y -i {ia} -i {iv} -filter:a aresample=async=1 -c:a aac -c:v copy {ov}' \
                  ''.format(ia=audio_filename, iv=video_filename, ov=output_filename)
            subprocess.call(cmd, shell=True)
            with open(output_filename, 'rb') as fl:
                new_video = fl.read()

        if video_filename is not None:
            remove(video_filename)
        if audio_filename is not None:
            remove(audio_filename)
        if output_filename is not None:
            remove(output_filename)

        with open(filename, 'wb') as fl:
            fl.write(new_video)

        return new_video

    @staticmethod
    def get_playlist_of_youtube_source(url, must_combine_audio=False):
        """
        Returns the playlist of Youtube source
        :param url: video URL.
        :param must_combine_audio: Flag that indicates whether we need the combine audio.
        :return: list of links to video, sorted by bandwidth.
        """
        # Pytube implementation
        # yt = YouTube(url)
        # video_playlists = [x for x in yt.streams.all() if x.type == 'video']
        # audio_playlists = [x for x in yt.streams.all() if x.type == 'audio']
        # video_playlists.sort(key=lambda x: (int(x.resolution[:-1]), x.fps), reverse=True)
        # audio_playlists.sort(key=lambda x: int(x.abr[:-4]), reverse=True)
        # playlists = yt.streams.order_by('resolution').desc().all()
        # video_playlists = yt.streams

        # Youtube_dl implementation
        ydl_opts = {
            'format': 'bestaudio/best',
        }
        yt = YoutubeDL(ydl_opts)
        meta = yt.extract_info(url, download=False)
        if must_combine_audio:
            video_playlists = [x for x in meta['formats'] if x['vcodec'] != 'none' and x['acodec'] != 'none']
        else:
            video_playlists = [x for x in meta['formats'] if x['vcodec'] != 'none']
        audio_playlists = [x for x in meta['formats'] if x['vcodec'] == 'none']
        video_playlists.sort(key=lambda y: (y['height'], y['fps'] if y['fps'] is not None else 0), reverse=True)
        audio_playlists.sort(key=lambda y: int(y['abr']), reverse=True)

        # playlists = yt.streams.order_by('resolution').desc().all()
        # video_playlists = yt.streams
        return video_playlists, audio_playlists

    @staticmethod
    def _download_youtube_video(stream, filename):
        # url = stream.url
        # filesize = stream.filesize
        url = stream['url']
        filesize = stream['filesize']

        ranges = [[url, i * VideoFetchTools.CHUNK_SIZE, (i + 1) * VideoFetchTools.CHUNK_SIZE - 1]
                  for i in range(ceil(filesize / VideoFetchTools.CHUNK_SIZE))]
        ranges[-1][2] = None  # Last range must be to the end of file, so it will be marked as None.

        if mp is not None:
            pool = mp.Pool(min(len(ranges), 64))
            # pool = mp.Pool(min(len(ranges), 4))
            chunks = pool.map(VideoFetchTools._download_youtube_chunk, ranges)
            pool.close()
            pool.join()
        else:
            chunks = [None] * len(ranges)
            workers = ThreadPool(min(len(ranges), 64))  # 100 is the number of threads
            for i, data_range in enumerate(ranges):
                workers.add_task(VideoFetchTools._store_youtube_chunk_to_param, i, data_range, chunks)

        with open(filename, 'wb') as outfile:
            for chunk, chunk_range in zip(chunks, ranges):
                if chunk is None:
                    # We had some problem with the fetching...
                    new_chunk = VideoFetchTools._download_youtube_chunk(chunk_range)
                    outfile.write(new_chunk)
                else:
                    outfile.write(chunk)

    @staticmethod
    def _download_youtube_chunk(args):
        url, start, finish = args
        range_string = '{}-'.format(start)

        if finish is not None:
            range_string += str(finish)

        # response = requests.get(url, headers={'Range': 'bytes=' + range_string})
        # return response.content

        number_of_retries = 0
        max_number_of_retries = 5
        try:
            response = requests.get(url, headers={'Range': 'bytes=' + range_string})
            if response.content is None:
                sleep(5)
                raise requests.exceptions.ConnectionError
            return response.content
        except (requests.exceptions.SSLError,
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ContentDecodingError,
                requests.exceptions.SSLError,
                requests.exceptions.ChunkedEncodingError,
                ) as err:
            number_of_retries += 1
            if number_of_retries > max_number_of_retries:
                warnings.warn(str(err))
                raise err

    @staticmethod
    def _store_youtube_chunk_to_param(args):
        i = args[0]
        store = args[2]
        new_args = args[1]
        store[i] = VideoFetchTools._download_youtube_chunk(new_args)


# class M3U8Tools(object):
#     @staticmethod
#     def parse_hdrezka_request_header(header):
#         """
#         Get all the available playlists url of m3u.
#         :param header: address of m3u file
#         :return: parsed m3u8 object.
#         """
#         request = requests.utils.unquote(header)
#         request = requests.utils.parse_dict_header(request.replace('&', ','))
#         correct_m3u8_url = request['manifest_m3u8']
#         payload = request.copy()
#         payload.pop('manifest_m3u8')
#         response = requests.get(correct_m3u8_url, data=payload)
#         m3u8_object = m3u8.loads(response.text)
#         return m3u8_object
#
#     @staticmethod
#     def parse_m38u_from_url(m3u8_url):
#         """
#         Get all the available playlists url of m3u.
#         :param m3u8_url: address of m3u file
#         :return: parsed m3u8 object.
#         """
#         m3u8_object = m3u8.load(m3u8_url)
#         return m3u8_object
#
#     @staticmethod
#     def get_available_playlists(m3u8_pbject):
#         """
#         Get all the available playlists url of m3u.
#         :param m3u8_pbject: m3u8 object
#         :return: lists of urls and durations of video fragments.
#         """
#         urls = [x.absolute_uri for x in m3u8_pbject.playlists]
#         bandwidths = [x.stream_info.bandwidth for x in m3u8_pbject.playlists]
#         resolutions = [x.stream_info.resolution for x in m3u8_pbject.playlists]
#
#         return urls, bandwidths, resolutions


if __name__ == '__main__':
    # vf = VideoFetchTools()
    # url = 'manifest_m3u8=http%3A%2F%2Fstreamblast.cc%2Fvideo%2F00654ff8f2b31c63%2Findex.m3u8%3Fcd%3D0' \
    #       '%26expired%3D1491260806%26mw_pid%3D157' \
    #       '%26reject%3D1%26signature%3D100ebb155cdac7136ba756f16bb30743' \
    #       '&manifest_mp4=null&token=00654ff8f2b31c63&pid=157'
    # m3u8_object = vf.parse_hdrezka_request_header(url)

    # url = 'https://s11.escdn.co/hls/jg6nskvxoftu7m7cyz6vkoassbhyttrgpqikdilg2,' \
    #       '6hn774v4jbzkf7ik74q,fsn574v4jb6zdgdo55q,.urlset/master.m3u8'
    # m3u8_object = vf.parse_m38u_from_url(url)
    #
    # urls, bandwidths, resolutions = vf.get_available_playlists(m3u8_object)
    #
    # for url, bandwidth, resolution in zip(urls, bandwidths, resolutions):
    #     urls, _, _ = vf.get_list_of_fragments_from_m3u8(url)
    #     dat = vf.merge_ts_fragments(urls, 1, 10)
    #     vf.save_file(dat, 'tmp{lres}.ts'.format(lres=resolution[1]))
    pass
