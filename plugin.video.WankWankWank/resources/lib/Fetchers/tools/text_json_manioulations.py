# import json
import re

white_spaces = '\r\n\t '


def clean_white_spaces(raw_text):
    return re.sub(r'^[\r\n\t ]*|[\r\n\t ]*$', '', raw_text)


def prepare_json_from_not_formatted_text(raw_text):
    """
    Takes text of the form where the keys are not put inside quotes, add the special quotes, and returns the proper
    JSON object
    :param raw_text: raw text
    :return: JSON object in case check_structure is True,
    """
    return_object = prepare_dict_from_not_formatted_text(raw_text)
    return return_object


def prepare_dict_from_not_formatted_text(raw_text):
    """
    Takes text of the form where the keys are not put inside quotes, add the special quotes, and returns the proper
    JSON object
    :param raw_text: raw text
    :return: JSON object in case check_structure is True,
    """
    raw_text = clean_white_spaces(raw_text)
    start_i = 1
    end_i = find_end_index(raw_text)
    raw_source = raw_text[start_i:end_i]
    if raw_text[0] == '{':
        res = prepare_json_dictionary_element(raw_source)
    elif raw_text[0] == '[':
        res = prepare_json_list_element(raw_source)
    else:
        res = prepare_json_text_element(raw_source)
    return res


def prepare_json_dictionary_element(raw_text):
    if len(raw_text) == 0:
        return {}
    raw_text = clean_white_spaces(raw_text)
    res = {}
    tmp_res = []
    i = 0
    separators = (':', ',')
    while 1:
        if len(tmp_res) != 2:
            x = raw_text[i]
            if x in white_spaces:
                i += 1
                if i >= len(raw_text):
                    return res
                continue
            elif x in ('"', '\'', '{', '['):
                open_i = i
                close_i = find_end_index(raw_text[i:]) + i + 1
                tmp_res.append(prepare_dict_from_not_formatted_text(raw_text[open_i:close_i]))
            else:
                open_i = i
                try:
                    close_i = raw_text[i + 1:].index(separators[len(tmp_res)]) + i + 1
                except ValueError:
                    # We reached the end of the text
                    close_i = len(raw_text)
                tmp_res.append(prepare_json_text_element(raw_text[open_i:close_i]))

            i = close_i
            if len(tmp_res) == 1:
                assert raw_text[i] == ':'
                i += 1
            raw_text = raw_text[:i] + clean_white_spaces(raw_text[i:])
        else:
            # We have both key and value
            res[tmp_res[0]] = tmp_res[1]
            tmp_res = []
            if i >= len(raw_text):
                return res

            x = raw_text[i]
            assert x == ','
            i += 1
            if i >= len(raw_text):
                return res


def prepare_json_list_element(raw_text):
    raw_text = clean_white_spaces(raw_text)
    if len(raw_text) == 0:
        return []
    res = []
    i = 0
    while 1:
        x = raw_text[i]
        if x in white_spaces:
            i += 1
            if i >= len(raw_text):
                return res
            continue
        elif x in ('"', '\'', '{', '['):
            open_i = i
            close_i = find_end_index(raw_text[i:]) + i + 1
            value = prepare_dict_from_not_formatted_text(raw_text[open_i:close_i])
        else:
            open_i = i
            close_i = (raw_text[i + 1:].index(',') + i + 1) if ',' in raw_text[i + 1:] else len(raw_text)
            value = prepare_json_text_element(raw_text[open_i:close_i])

        i = close_i
        res.append(value)
        if i >= len(raw_text):
            return res

        assert raw_text[i] == ','
        i += 1


def prepare_json_text_element(raw_text):
    res = clean_white_spaces(raw_text)
    if res.isdigit():
        return int(res)
    elif res.replace('.', '').isdigit() and res.count('.') == 1:
        return float(res)
    if res == 'true':
        return True
    if res == 'false':
        return False
    return res


def find_end_index(raw_text):
    start_char = raw_text[0]
    if start_char == '{':
        end_char = '}'
    elif start_char == '[':
        end_char = ']'
    elif start_char == '(':
        end_char = ')'
    elif start_char in ('"', '\''):
        close_i = raw_text[1:].index(start_char) + 1
        return close_i
    else:
        raise ValueError('Unknown parenthesis')
    start_is = [x for x, c in enumerate(raw_text) if start_char == c]
    end_is = [x + 1 for x, c in enumerate(raw_text[1:]) if end_char == c]
    diff = [x - y for x, y in zip(end_is[:-1], start_is[1:])]
    end_i = [i for i, x in enumerate(diff) if x < 0]
    end_i = end_i[0] if len(end_i) > 0 else len(end_is) - 1
    return end_is[end_i]
    # diff = 0
    # start_i = start_is.pop(0)
    # end_i = end_is.pop(0)
    # while len(start_is) > 0 or len(end_is) > 0:
    #     if len(start_is) > 0 and start_i < end_i:
    #         # We have subgroup
    #         diff += 1
    #         start_i = start_is.pop(0)
    #     else:
    #         # We have the previous series
    #         diff -= 1
    #         if diff == 0:
    #             return end_i
    #         end_i = end_is.pop(0)
    #
    # if diff == 0:
    #     return end_i
    # else:
    #     raise RuntimeError('Wrong Format')


if __name__ == '__main__':
    raw_text1 = '{"image":"//i.sexu.com/sexu-thumbs/26/2527029/23-main.jpg","width":"100%",' \
                '"aspectratio":"16:9","startparam":"start","autostart":false,"primary":"html5",' \
                '"splash":true,"share":false,"clip":{"downloadUrl":"//v.sexu.com/key=+l0QlP6z-' \
                '644KGL5HesZVA,end=1584412779,ip=87.69.109.56/sec=protect/download2=/sexu/26/2527029-720p-x.mp4",' \
                '"qualities":["240p","480p","720p"],"defaultQuality":"720p","thumbnails":{"width":800,"height":' \
                '450,"columns":5,"rows":5,"startIndex":1,"interval":25.53846153846154,' \
                '"template":"//i.sexu.com/sexu-thumbs/26/2527029/{time}-timeline-160x90.jpg"},' \
                '"vtt_link":"//i.sexu.com/sexu-thumbs/26/2527029/timeline.vtt"}}'
    raw_text2 = """
    {
    video_id: '5862',
    license_code: '$379086812506737',
    lrc: '50803888',
    rnd: '1585230732',
    video_url: 'function/0/https://faapy.com/get_file/1/3d3113fb955fedb21a2538341d623879/5000/5862/5862_240p.mp4/',
    postfix: '_240p.mp4',
    video_url_text: '240p',
    video_alt_url: 'function/0/https://faapy.com/get_file/1/0cb1db56efa0b3f41d23d02fd230f604/5000/5862/5862_360p.mp4/',
    video_alt_url_text: '360p',
    video_alt_url2: 'function/0/https://faapy.com/get_file/1/44c346222ab22a24dcd33958e35bf9d5/5000/5862/5862.mp4/',
    video_alt_url2_text: '720p HD',
    video_alt_url2_hd: '1',
    default_slot: '3',
    video_alt_url3: 'https://faapy.com/redirect_cs.php?id=114',
    video_alt_url3_text: 'Pure 4K HD',
    video_alt_url3_redirect: '1',
    timeline_screens_url: '//cdn.faapy.com/contents/videos_screenshots/5000/5862/timelines/hq_mp4/240x120/{time}.jpg',
    timeline_screens_interval: '3',
    timeline_screens_count: '110',
    preview_url: '//cdn.faapy.com/contents/videos_screenshots/5000/5862/preview.mp4.jpg',
    skin: 'dark.css',
    logo_position: '0,0',
    logo_anchor: 'topleft',
    volume: '0.5',
    preload: 'metadata',
    hide_controlbar: '1',
    mlogo_link: 'https://faapy.com/redirect_cs.php?id=114',
    lrcv: '1586138419701780139549907',
    vast_timeout1: '10',
    adv_pre_vast: '',
    adv_pre_vast_alt: 'https://syndication.exosrv.com/splash.php?idzone=3262224',
    adv_pre_duration: '30',
    adv_pre_duration_text: 'This ad will end in %time seconds',
    adv_pre_skip_text_time: 'Skip ad in %time',
    adv_pre_skip_text: 'Skip ad',
    embed: '1'
    }
    """
    raw_text3 = """
        { player: '#hola',
            share: false,
            poster: 'https://s9.videyo.net/i/02/00008/bfjj7rk6d3gg0000.jpg',
            sources: [{src: "https://s9.videyo.net/hls/,wgchdtu5ug5oigtf2lcqq5jizxw7pwxy6iog47hfuqhxffdy4jqwtkhldjuq,.urlset/master.m3u8", type: "application/x-mpegURL"}],
            preload: 'auto',
            thumbnails:{ vtt:'/dl?op=get_slides&length=2495.01&url=https://s9.videyo.net/i/02/00008/bfjj7rk6d3gg0000.jpg' },
            videojs_options: { 
                html5: {
                    hlsjsConfig: {
                        debug: false, 
                        //startLevel: 1,
                        //maxBufferLength: 30, 
                        //maxBufferSize: 6*1024*1024, 
                        //maxMaxBufferLength: 600, 
                        //capLevelToPlayerSize: true,
                    }
                },
                
                chromecast:{},
            },
        }    
    """
    raw_text4 = """
    {
        logo: "https://videos.freeones.com/foplayer/logo-small.png",
        poster: "https://img.freeones.com/videos/008/M5/NT/M5NTudp4tQoVC4pVMD8xRg/poster/351.jpg",
        flash: {
            swf: 'https://videos.freeones.com/foplayer/player.swf',
        },
        thumbnails: {
            baseUrl: 'https://img.freeones.com/videos/008/M5/NT/M5NTudp4tQoVC4pVMD8xRg/timeline/'
        },
        affiliateUrl: 'http://n4n.babecall.com/track/Fr33Stati0n.865.53.54.0.0.0.0.0.0.0.0',
        relatedXML: 'https://videos.freeones.com/PlayerRelatedXML/190896/',
        src: [
            {type: 'application/x-mpegURL', src: 'https://videolb.freeones.com/fo/008/M5/NT/M5NTudp4tQoVC4pVMD8xRg/list.smil/playlist.m3u8'},
            {type: 'application/dash+xml', src: 'https://videolb.freeones.com/fo/008/M5/NT/M5NTudp4tQoVC4pVMD8xRg/list.smil/manifest.mpd'},
            {type: 'video/mp4', src: 'https://videolb.freeones.com/fo/008/M5/NT/M5NTudp4tQoVC4pVMD8xRg/480p.mp4'}
        ],
        qualitySelector: {
            streamingUrl: 'https://videolb.freeones.com/fo/008/M5/NT/M5NTudp4tQoVC4pVMD8xRg',
            qualities: '1080p,720p,480p,360p,240p'
        },
        chromecast: {
            metadata:{
                title: document.getElementById('video-name').innerText,
                subtitle: 'Freeones.com'
            }
        }
    }
    """

    test_res = prepare_json_from_not_formatted_text(raw_text4)
    print(test_res)
    # print(find_end_index(raw_text[1:]))
