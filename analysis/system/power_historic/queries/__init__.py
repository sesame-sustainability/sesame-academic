import os
import pugsql

import settings

queries = pugsql.module('analysis/system/power_historic/queries')
queries.connect(settings.DB_URL)
