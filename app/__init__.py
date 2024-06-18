# import sys
# import traceback
# class TracePrints(object):
#     def __init__(self):
#         self.stdout = sys.stdout
#     def write(self, s):
#         self.stdout.write(s)
#         traceback.print_stack(file=self.stdout)
# sys.stdout = TracePrints()

from flask import Flask
from flask_cors import CORS

import settings
from app.common import HTTPException
from app.auth import app as auth_app
from app.users import app as users_app
from app.pathway import app as pathway_app
from app.lca import app as lca_app
from app.tea import app as tea_app
from app.fleet import app as fleet_app
from app.power_historic import app as power_historic_app
from app.grid import app as grid_app
from app.pps import app as pps_app
from app.industry.cement import app as industry_cement_app
from app.industry.steel import app as industry_steel_app
from app.industry.aluminum import app as industry_aluminum_app
from app.industry.fleet import app as industrial_fleet_app
from core.common import JSONEncoder

app = Flask('SESAME')
CORS(app)

sentry_dsn = settings.SENTRY_DSN
if sentry_dsn is not None:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0
    )

app.json_encoder = JSONEncoder

@app.errorhandler(HTTPException)
def handle_error(err):
    return err.serialize()

@app.route('/')
def _root():
    return 'ok'

app.register_blueprint(auth_app, url_prefix='/auth')
app.register_blueprint(users_app, url_prefix='/users')
app.register_blueprint(pathway_app, url_prefix='/pathway')
app.register_blueprint(lca_app, url_prefix='/lca')
app.register_blueprint(tea_app, url_prefix='/tea')
app.register_blueprint(fleet_app, url_prefix='/fleet')
app.register_blueprint(power_historic_app, url_prefix='/power_historic')
app.register_blueprint(grid_app, url_prefix='/grid')
app.register_blueprint(pps_app, url_prefix='/pps')
app.register_blueprint(industry_cement_app, url_prefix='/industry/cement')
app.register_blueprint(industry_steel_app, url_prefix='/industry/steel')
app.register_blueprint(industry_aluminum_app, url_prefix='/industry/aluminum')
app.register_blueprint(industrial_fleet_app, url_prefix='/industry/fleet')
