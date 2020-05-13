class HandlerManager(object):
    def __init__(self, logo_dir, user_data_dir, session_id, source_handler):
        self.handlers = {}
        self.logo_dir = logo_dir
        self.user_data_dir = user_data_dir
        self.session_id = session_id
        # xbmc.log('Preparing handlers for source ids {s}'.format(s=source_ids))
        for _x in source_handler.source_range:
            try:
                _h = source_handler(_x, logo_dir)
                if _h.is_active is False:
                    continue
                self.handlers[_h.handler_id] = _h
            except ValueError:
                continue

    def get_handler(self, handler_id, use_web_server):
        handler = self.handlers[handler_id]
        if handler.initialized_module is None:
            handler.initialized_module = handler.main_module(source_id=handler_id, data_dir=self.user_data_dir,
                                                             session_id=self.session_id, use_web_server=use_web_server)
        return handler.initialized_module

    def store_data_for_all_handlers(self):
        """
        Saves tthe data for all handlers.
        :return:
        """
        for handler_id in self.handlers:
            self.store_data_for_handler(handler_id)

    def store_data_for_handler(self, handler_id):
        """
        Saves the data for all handlers.
        :param handler_id: Handler id.
        :return:
        """
        handler = self.handlers[handler_id]
        if handler.initialized_module is not None:
            handler.initialized_module.catalog_manager.save_store_data()
