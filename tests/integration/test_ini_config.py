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
    def ini_file_with_logging(self, ini_file, logging_config):
        ini_file.write(logging_config)
        ini_file.flush()
        yield ini_file

    def test_ini_fiel_not_found(self):
        config_type = 'ini'
        config_opt = {
            'ini_file': 'test.ini',
            'bar': 'baz',
        }

        with pytest.raises(RuntimeError):
            config_factory.create(config_type, **config_opt)

    def test_ini_file_section(self, ini_file):
        config_type = 'ini'
        config_opt = {
            'ini_file': ini_file.name,
            'bar': 'baz',
        }

        config = config_factory.create(config_type, **config_opt)

        assert config['TESTING']['key'] == 'value'

    def test_ini_file_get_value(self, ini_file):
        config_type = 'ini'
        config_opt = {
            'ini_file': ini_file.name,
            'bar': 'baz',
        }

        config = config_factory.create(config_type, **config_opt)

        assert config['TESTING'].get('key2', {}) == {}

    def test_ini_logging(self, ini_file_with_logging):
        config_type = 'ini'
        config_opt = {
            'ini_file': ini_file_with_logging.name,
            'ini_logging': True,
            'ini_logging_disable_existing': False,
        }

        config = config_factory.create(config_type, **config_opt)

        assert config['TESTING'].get('key2', {}) == {}
