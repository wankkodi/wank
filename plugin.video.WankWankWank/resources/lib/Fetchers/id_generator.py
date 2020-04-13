import codecs


class IdGenerator:
    @staticmethod
    def make_id(obj):
        return int(codecs.encode(str(obj).encode('utf-8'), 'hex'), 16)

    @staticmethod
    def id_to_original_str(given_id):
        hex_id = hex(int(given_id))
        hex_id = hex_id[2:-1] if hex_id[-1] == 'L' else hex_id[2:]
        return codecs.decode(hex_id, 'hex').decode('utf-8')
