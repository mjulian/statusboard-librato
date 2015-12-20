#!/usr/bin/env python
from datetime import datetime, timedelta
from flask.ext.api import FlaskAPI
import logging
import os
import pytz

import pytoml as toml
import librato

LIBRATO_USER = os.environ['LIBRATO_USER']
LIBRATO_TOKEN = os.environ['LIBRATO_TOKEN']

app = FlaskAPI(__name__)
api = librato.connect(LIBRATO_USER, LIBRATO_TOKEN)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Read in configuration options
with open('librato.toml', 'rb') as librato_config_file:
    librato_config = toml.load(librato_config_file)

refresh_rate = librato_config.get('refresh_rate')
log.info('librato.toml: Setting refresh rate to %ss' % refresh_rate)

time_to_fetch = timedelta(hours=librato_config.get('time_to_fetch'))
log.info('librato.toml: Fetching past %sh of datapoints' % time_to_fetch)

local_timezone = pytz.timezone(librato_config.get('local_timezone'))
log.info('librato.toml: Setting local time zone to %s' % local_timezone)

metric_resolution = librato_config.get('metric_resolution')
log.info('librato.toml: Setting metric resolution to %ss' % metric_resolution)


@app.route('/metric/<metric_name>/<source>', methods=['GET'])
def get_metric(metric_name, source):
    # The Status Board graph object
    # get_metric() updates this and then returns it when it's complete
    graph_result = {
        'graph': {
            'title': None,
            'refreshEveryNSeconds': refresh_rate,
            'type': 'line',
            'datasequences': None
        }
    }

    datapoints = []
    timedelta = datetime.today() - time_to_fetch
    start_time = timedelta.strftime('%s')

    log.info('Running query for %s with source %s for the past %sh' % (metric_name, source, time_to_fetch))
    metric = api.get(metric_name, start_time=start_time, resolution=metric_resolution)
    graph_result['graph']['title'] = metric_name

    try:
        for data in metric.measurements[source]:
            value = data.get('value')
            measure_time_dt = datetime.fromtimestamp(data.get('measure_time'), local_timezone)
            measure_time = measure_time_dt.strftime('%H:%M:%S')
            datapoints.append({'title': measure_time, 'value': value})

        num_datapoints = len(datapoints)
        if num_datapoints == 200:
            log.info('%s datapoints found. This is the max permissable and may be truncated' % num_datapoints)
        else:
            log.info('%s datapoints found' % num_datapoints)

        graph_result['graph']['datasequences'] = [{'datapoints': datapoints, 'title': source}]

    except KeyError:
        log.info('No datapoints found in the metric query')
        graph_result['graph']['error'] = {}
        graph_result['graph']['error']['message'] = 'No datapoints found'

    finally:
        return graph_result

if __name__ == '__main__':
    app.run(debug=os.environ['DEBUG'])
