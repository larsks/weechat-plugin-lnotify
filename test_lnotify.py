try:
    # for Python 3
    from unittest import mock
except ImportError:
    # for Python 2
    import mock

import sys


class fake_weechat:
    '''Just enough of the weechat module to allow the lnotify
    to run without errors.'''

    options = {}

    WEECHAT_RC_OK = 0
    WEECHAT_HOOK_PROCESS_ERROR = 10

    @staticmethod
    def current_buffer():
        return 0

    @staticmethod
    def buffer_get_string(*args, **kwargs):
        raise NotImplementedError

    @staticmethod
    def hook_process_hashtable(*args, **kwargs):
        raise NotImplementedError

    @classmethod
    def config_get_plugin(kls, opt):
        return kls.options.get(opt, '')

    @classmethod
    def config_set_plugin(kls, opt, value):
        kls.options[opt] = value


# This is where we fake 'import weechat'.
sys.modules['weechat'] = fake_weechat


import lnotify  # NOQA


BUFFER_CONFIG = {
    'localvar_type': 'channel',
    'localvar_away': False,
    'localvar_nick': 'testuser',
    'short_name': '#testing',
}


def fake_get_string(**overrides):
    buffer_config = dict(BUFFER_CONFIG, **overrides)

    def _(buffer, opt):
        return buffer_config[opt]

    return _


def setup_module():
    lnotify.cfg = lnotify.config()


@mock.patch('weechat.hook_process_hashtable')
@mock.patch('weechat.buffer_get_string')
def test_handle_msg_public_highlight(mock_buffer_get_string,
                                     mock_hook_process_hashtable):
    mock_buffer_get_string.side_effect = fake_get_string()
    lnotify.handle_msg('', 0, '', '',  [], True, '(prefix)', 'this is a test')

    mock_hook_process_hashtable.assert_called_with(
        'notify-send',
        {'arg1': '-i', 'arg2': 'weechat',
         'arg3': '-a', 'arg4': 'WeeChat',
         'arg5': '(prefix) @ #testing', 'arg6': 'this is a test'},
        20000, 'process_cb', '')


@mock.patch('weechat.hook_process_hashtable')
@mock.patch('weechat.buffer_get_string')
def test_handle_msg_public_nohighlight(mock_buffer_get_string,
                                       mock_hook_process_hashtable):
    mock_buffer_get_string.side_effect = fake_get_string()
    lnotify.handle_msg('', 0, '', '',  [], False, '(prefix)', 'this is a test')

    mock_hook_process_hashtable.assert_not_called()


@mock.patch('weechat.hook_process_hashtable')
@mock.patch('weechat.buffer_get_string')
def test_handle_msg_private(mock_buffer_get_string,
                            mock_hook_process_hashtable):
    mock_buffer_get_string.side_effect = fake_get_string(
        localvar_type='private')
    lnotify.handle_msg('', 0, '', '',  [], True, '(prefix)', 'this is a test')

    mock_hook_process_hashtable.assert_called_with(
        'notify-send',
        {'arg1': '-i', 'arg2': 'weechat',
         'arg3': '-a', 'arg4': 'WeeChat',
         'arg5': '#testing', 'arg6': 'this is a test'},
        20000, 'process_cb', '')


@mock.patch('weechat.hook_process_hashtable')
@mock.patch('weechat.buffer_get_string')
def test_handle_msg_away(mock_buffer_get_string,
                         mock_hook_process_hashtable):
    mock_buffer_get_string.side_effect = fake_get_string(localvar_away=True)

    lnotify.handle_msg('', 0, '', '',  [], True, '(prefix)', 'this is a test')

    mock_hook_process_hashtable.assert_not_called()


@mock.patch('weechat.hook_process_hashtable')
@mock.patch('weechat.buffer_get_string')
def test_handle_msg_tags(mock_buffer_get_string,
                         mock_hook_process_hashtable):
    mock_buffer_get_string.side_effect = fake_get_string()

    lnotify.handle_msg('', 0, '', 'nick_testuser', [], True, '(prefix)',
                       'this is a test')

    mock_hook_process_hashtable.assert_not_called()
