from .app import Application


class WebPage:

    '''basic class for all pages'''

    def __init__(self, app, url = ''):
        if(not isinstance(app, Application)):
            raise ValueError('Invalid input parameter: instance of "Application" class should be given')
        self._app = app
        self.page_url = url
        self.wait_time = 5

    def open(self, wait_condition = None, time = 0, timeout_msg = ''):
        self._app.openPage(self.page_url, wait_condition, time, timeout_msg)
        return self

    def __getattr__(self, name):
        method = getattr(self._app, name, None)
        if(method is None): raise AttributeError('The method "{0}" was not found in the class "{1}"'.format(name, self._app.__class__))
        return method