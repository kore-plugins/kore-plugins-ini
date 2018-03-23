import pytest
import tempfile

from six import b

from kore import config_factory


class TestIniConfig(object):

    @pytest.fixture
    def logging_config(self):
        return b("""
[loggers]
keys = root
[handlers]
keys = console
[formatters]
keys = generic
[logger_root]
level = DEBUG
handlers = console
[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic
[formatter_generic]
format = %(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s
        """)

    @pytest.yield_fixture
    def ini_file(self):
        with tempfile.NamedTemporaryFile(suffix='.ini') as f:
            f.write(b('[TESTING]\nkey = value'))
            f.flush()
            yield f

    @pytest.yield_fixture
    def ini_file_upper(self):
        with tempfile.NamedTemporaryFile(suffix='.ini') as f:
            f.write(b('[TESTING]\nKEY = value'))
            f.flush()
            yield f

    @pytest.yield_fixture
    def ini_file_with_logging(self, ini_file, logging_config):
        ini_file.write(logging_config)
        ini_file.flush()
        yield ini_file

    def test_file_not_found(self):
        config_type = 'ini'
        config_opt = {
            'ini_file': 'test.ini',
            'bar': 'baz',
        }

        with pytest.raises(RuntimeError):
            config_factory.create(config_type, **config_opt)

    def test_get_section(self, ini_file):
        config_type = 'ini'
        config_opt = {
            'ini_file': ini_file.name,
            'bar': 'baz',
        }
        config = config_factory.create(config_type, **config_opt)
        
        with pytest.raises(KeyError):
            config.get_section('UNDEFINED')

    def test_get_section_default_value(self, ini_file):
        config_type = 'ini'
        config_opt = {
            'ini_file': ini_file.name,
            'bar': 'baz',
        }

        config = config_factory.create(config_type, **config_opt)
        section = config.get_section('TESTING')

        result = config.get('UNDEFINED', 'undefined')

        assert result == 'undefined'

    def test_section_option(self, ini_file):
        config_type = 'ini'
        config_opt = {
            'ini_file': ini_file.name,
            'bar': 'baz',
        }
        config = config_factory.create(config_type, **config_opt)
        section = config.get_section('TESTING')

        result = section['key']

        assert result == 'value'

    def test_section_option_upper(self, ini_file_upper):
        config_type = 'ini'
        config_opt = {
            'ini_file': ini_file_upper.name,
            'bar': 'baz',
        }
        config = config_factory.create(config_type, **config_opt)
        section = config['TESTING']

        result = dict(section)

        assert result == {
            'KEY': 'value',
        }

    def test_get_value(self, ini_file):
        config_type = 'ini'
        config_opt = {
            'ini_file': ini_file.name,
            'bar': 'baz',
        }
        config = config_factory.create(config_type, **config_opt)
        section = config.get_section('TESTING')

        result = section.get('key2', 'undefined')

        assert result == 'undefined'

    def test_logging(self, ini_file_with_logging):
        config_type = 'ini'
        config_opt = {
            'ini_file': ini_file_with_logging.name,
            'ini_logging': True,
            'ini_logging_disable_existing': False,
        }
        config = config_factory.create(config_type, **config_opt)

        loggers = config.get_section('loggers')

        assert loggers['keys'] == 'root'

        handlers = config.get_section('handlers')

        assert handlers['keys'] == 'console'

        formatters = config.get_section('formatters')

        assert formatters['keys'] == 'generic'
