**./mock_frontend/shallwe/.env**\
REACT_APP_REDIRECT_URI=https://доменный.адрес.лендинга

---
**./shallwe_core/shallwe_core/build_config.py**\
SHALLWE_CONF_SECRET_KEY="набор символов", получить у девелопера\
SHALLWE_CONF_DB_NAME="имя основной базы postgres"\
SHALLWE_CONF_TEST_DB_NAME="имя тестовой базы postgres"\
SHALLWE_CONF_DB_USER="имя юзера postgres"\
SHALLWE_CONF_DB_PASS="пароль postgres"\
SHALLWE_CONF_DB_HOST="хост postgres", дефолт - "localhost"\
SHALLWE_CONF_DB_PORT=порт postgres, дефолт - 5432\
SHALLWE_CONF_OAUTH_CLIENT_ID="гугл клиент", взять в консоли shallwe.ua@gmail.com\
SHALLWE_CONF_OAUTH_CLIENT_SECRET="гугл секрет", взять в консоли гугл ^\
SHALLWE_CONF_ENV_MODE=по ситуации "DEV", "QA", "STAGE" или "PROD"\
SHALLWE_CONF_GOOGLE_CALLBACK_URL="https://доменный.адрес.лендинга"
SHALLWE_CONF_ALLOWED_HOSTS="host.one","host.two" - запятая даже при одном
SHALLWE_CONF_CSRF_TRUSTED_ORIGINS="https://origin.one","https://origin.two" - аналогично,