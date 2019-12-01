import json,requests,logging,inspect,atexit,yaml
from flask import Flask
from prometheus_client import start_http_server, Gauge
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
from apscheduler.schedulers.background import BackgroundScheduler

global g, config_file
config_file='config.yml'

g = Gauge('endpoint_health_http_code', 'HTTP code returned by app on health check path',['url','health_path'])

def check_endpoint_health(url):
	try:
		response=requests.get(url)
		code=response.status_code
		return code
	except Exception as e:
		logging.error("Exception in method %s(): %s" %(inspect.currentframe().f_code.co_name,str(e)))

def write_metrics(url,port,health_path):
	try:
		status=check_endpoint_health(url+':'+port+health_path)
		g.labels(url=url,health_path=health_path).set(str(status))
	except Exception as e:
		logging.error("Exception in method %s(): %s" %(inspect.currentframe().f_code.co_name,str(e)))

def read_config():
	try:
		config_dict = yaml.load(open(config_file),Loader=yaml.BaseLoader)
		for items in config_dict:
			write_metrics(items['url'],items['port'],items['path'])
	except Exception as e:
		logging.error("Exception in method %s(): %s" %(inspect.currentframe().f_code.co_name,str(e)))


if __name__=='uwsgi_file_app':
	try:
		logging.basicConfig(level=logging.INFO,format='%(levelname)s %(asctime)s - %(message)s', datefmt='%d-%b-%Y %H:%M:%S')
		app = Flask(__name__)
		run_exporter = DispatcherMiddleware(app, {'/metrics': make_wsgi_app()})
		read_config()
		scheduler = BackgroundScheduler()
		scheduler.add_job(func=read_config, trigger="interval", seconds=5)
		scheduler.start()
		atexit.register(lambda: scheduler.shutdown())
	except Exception as e:
		logging.error("Exception in method %s(): %s" %(inspect.currentframe().f_code.co_name,str(e)))
		atexit.register(lambda: scheduler.shutdown())
