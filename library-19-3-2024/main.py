import os
from functools import lru_cache
from configparser import ConfigParser
import base64

from fastapi import FastAPI, Request
from fastapi_tryton import Tryton, Settings

HOME_DIR = os.getenv('HOME')
default_dir = os.path.join(HOME_DIR, 'fast.ini')
config = ConfigParser()
config.read(default_dir)
databases = list(eval(config.get('databases', 'uri')))
trytond_config = config.get('General', 'trytond_config')
# host_ = config.get('General', 'host')
API_KEY = config.get('Auth', 'api_key') 


database = 'super1'


@lru_cache()
def get_settings():
    return Settings(
        tryton_db=database,
        tryton_user=None,
        tryton_config=trytond_config
    )

setting_config = get_settings()
print(setting_config)


app = FastAPI()
app.settings = get_settings()
tryton = Tryton(app)


@app.get("/")
async def root(request: Request):
    return {"message": "Hello World"}


@app.get("/parties")
async def parties(request: Request):
    print("GETTINF PARTIRD")
    Party = tryton.pool.get('party.party')
    args = {
        'domain': [],
        'limit': 17,
        'fields_names': ['id', 'name'],
    }

    @tryton.transaction(request)
    def _get_data():
        records = Party.search_read(**args)
        return records

    res = _get_data()
    print('_records => ', res)
    return res


@app.get("/cities")
async def cities():
    City = tryton._get('party.city_code')
    args = {
        'domain': [],
        'limit': 17,
        'fields_names': ['id', 'name', 'code'],
    }
    cities = City.search_read(args)
    return cities


@app.post("/create")
async def create(arg: dict):
    """
    This method create a new record from 'arg' Dict:
    ...model: Str for name of model, example: 'party.party'
    ...context: Optional, dict of key-values including {company?, user?}
    ...record: Dict example, {'name': 'James Bond', 'code': '007'}
    """
    Model = tryton._get(arg.pop('model'))
    result = Model.create(arg)
    return result


@app.post("/search")
async def search(arg: dict):
    """
    This method search records from 'arg' Dict:
    ...model: Str for name of model, example: 'party.party'
    ...context: Optional, dict of key-values including {company?, user?}
    ...domain: String (As Tryton domain)
    ...fields_names: Dict example, {'name': 'James Bond', 'code': '007'}
    ...limit: int
    """
    Model = tryton._get(arg.pop('model'))
    result = Model.search(arg)
    return result


@app.post("/browse")
async def browse(arg: dict):
    """
    This method return records from ids from 'arg' Dict:
    ...model: Str for name of model, example: 'party.party'
    ...ids: List ids of records
    ...fields_names: List, example, ['name', 'code', ...]
    ...context: Optional, dict of key-values including {company?, user?}
    """
    Model = tryton._get(arg.pop('model'))
    result = Model.browse(arg)
    return result


@app.post("/search_read")
async def search_read(arg: dict):
    """
    This method search and read records from 'arg' Dict:
    ...model: Str for name of model, example: 'party.party'
    ...context: Optional, dict of key-values including {company?, user?}
    ...domain: String (As Tryton domain)
    ...fields_names: Dict example, {'name': 'James Bond', 'code': '007'}
    ...limit: Optional, int
    """
    Model = tryton._get(arg.pop('model'))
    result = Model.search_read(arg)
    return result


@app.post("/write")
async def write(arg: dict):
    """
    This method write records from 'arg' Dict:
    ...model: Str for name of model, example: 'party.party'
    ...context: Optional, dict of key-values including {company?, user?}
    ...ids: List ids of records
    ...values: Dict example, {'name': 'James Bond', 'code': '007'}
    """
    Model = tryton._get(arg.pop('model'))
    result = Model.write(arg)
    return result


@app.post("/delete")
async def delete(arg: dict):
    """
    This method delete records from 'arg' Dict:
    ...model: Str for name of model, example: 'party.party'
    ...context: Optional, dict of key-values including {company?, user?}
    ...ids: List of ids of records
    """
    Model = tryton._get(arg.pop('model'))
    result = Model.delete(arg)
    return result


@app.post("/button_method")
async def button_method(arg: dict):
    """
    This method call trigger method/button on Tryton model 'arg' Dict:
    ...model: Str for name of model, example: 'sale.sale'
    ...context: Optional, dict of key-values including {company?, user?}
    ...method: String, Example 'quote'
    ...ids: List of ids
    """
    Model = tryton._get(arg.pop('model'))
    result = Model.button_method(arg)
    return result


@app.post("/method")
async def method(arg: dict):
    """
    This method call class method on Tryton model 'arg' Dict:
    ...model: Str for name of model, example: 'party.party'
    ...context: Optional, dict of key-values including {company?, user?}
    ...method: String
    ...args: Dict values variables
    """
    Model = tryton._get(arg.pop('model'))
    result = Model.method(arg)
    return result


@app.post("/report")
async def report(arg: dict):
    """
    This method call class method on Tryton model 'arg' Dict:
    ...report: Name of report, example: 'purchase.purchase'
    ...records: List of records ids to render
    ...data: Dict with values
    ...context: Optional, dict of key-values including {company?, user?}
    """
    report = tryton._get_report(arg.pop('report'))
    ctx = arg.get('context', {})
    data = arg.get('data', {})
    records = arg.get('records', [])
    oext, content, direct_print, name = report.execute(records, data, ctx)
    result = {
        'name': name,
        'oext': oext,
        'content': base64.b64encode(content),
        'direct_print': direct_print,
    }
    return result


@app.post("/wizard")
async def wizard(arg: dict):
    """
    This method call class method on Tryton model 'arg' Dict:
    ...wizard: Name of report, example: 'hotel.night_audit'
    ...method: List of records ids to render
    ...view: (Optional) Dict with values
    ...context: (Optional) dict of key-values including {company?, user?}
    """
    Wizard = tryton._get_wizard(arg.pop('wizard'))
    method = arg.get('method')
    view = arg.get('view', {})
    ctx = arg.get('context', {})
    result = Wizard.run(method, view, ctx)
    return result


"""
Run test

uvicorn test_api:app --reload --host 0.0.0.0 --port 8020

"""