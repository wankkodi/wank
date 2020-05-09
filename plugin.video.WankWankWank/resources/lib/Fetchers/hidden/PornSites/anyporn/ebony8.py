from .... import urljoin, parse_qsl

from ....catalogs.porn_catalog import PornCategories, PornFilterTypes
from .boundhub import BoundHub


class Ebony8(BoundHub):
    flip_number = 10

    @property
    def max_pages(self):
        """
        Most viewed videos page url.
        :return:
        """
        return 1000

    @property
    def object_urls(self):
        res = super(Ebony8, self).object_urls
        res.pop(PornCategories.CHANNEL_MAIN)
        res[PornCategories.CHANNEL_MAIN] = urljoin(self.base_url, '/sites/')
        return res

    def _prepare_filters(self):
        """
        Prepares the filters
        :return:
        """
        (category_params, porn_stars_params, actress_params, channel_params, tag_params, video_params,
         search_params) = super(Ebony8, self)._prepare_filters()
        channel_params = \
            {'sort_order': [(PornFilterTypes.VideosPopularityOrder, 'Most Viewed', 'cs_viewed'),
                            (PornFilterTypes.VideosRatingOrder, 'Top Rated', 'avg_videos_rating'),
                            (PornFilterTypes.AlphabeticOrder, 'Alphabetically', 'title'),
                            (PornFilterTypes.NumberOfVideosOrder, 'Most Videos', 'total_videos'),
                            ],
             }
        return (category_params, porn_stars_params, actress_params, channel_params, tag_params, video_params,
                search_params)

    @property
    def base_url(self):
        """
        Base site url.
        :return:
        """
        return 'https://www.ebony8.com/'

    def __init__(self, source_name='Ebony8', source_id=0, store_dir='.', data_dir='../Data', source_type='Porn',
                 use_web_server=True, session_id=None):
        """
        C'tor
        :param source_name: save directory
        """
        super(Ebony8, self).__init__(source_name, source_id, store_dir, data_dir, source_type, use_web_server,
                                     session_id)

    def _update_available_channels(self, channel_data):
        return self._update_available_base_object(channel_data,
                                                  './/div[@class="list-sponsors"]/div[@class="margin-fix"]/a',
                                                  PornCategories.CHANNEL)

    def _get_page_request_logic(self, page_data, params, page_number, true_object, page_filter, fetch_base_url):
        headers = {
            'Accept': '*.*',
            'Cache-Control': 'max-age=0',
            'Referer': self.base_url,
            'Host': self.host_name,
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }
        conditions = self.get_proper_filter(page_data).conditions
        true_sort_filter_id = self._default_sort_by[true_object.object_type] \
            if true_object.object_type in self._default_sort_by \
            else page_filter.sort_order.filter_id

        if page_number is None:
            page_number = 1
        params.update({
            'mode': 'async',
            'function': 'get_block',
        })
        if page_filter.length.value is not None:
            params.update(parse_qsl(page_filter.length.value))
        if page_number > 1:
            params['from'] = str(page_number).zfill(2)

        if true_object.object_type == PornCategories.CHANNEL_MAIN:
            params['block_id'] = 'list_content_sources_sponsors_list'
            params['sort_by'] = page_filter.sort_order.value
            if (
                    page_filter.period.value is not None and
                    (conditions.period.sort_order is None or true_sort_filter_id in conditions.period.sort_order)
            ):
                params['sort_by'] += page_filter.period.value

            page_request = self.session.get(fetch_base_url, headers=headers, params=params)
            return page_request
        else:
            return super(Ebony8, self)._get_page_request_logic(page_data, params, page_number, true_object,
                                                               page_filter, fetch_base_url)
