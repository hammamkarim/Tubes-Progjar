from flask import Flask, jsonify, render_template
import asyncio
import aiohttp
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
import atexit
import logging
import json

logging.basicConfig(level=logging.INFO)
app = Flask(__name__, template_folder='html', static_folder='static')


def fetch_json(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data


file_json = 'website.json'
data_json = fetch_json(file_json)

status_data = {}


async def fetch_status(session, url):
    try:
        async with session.get(url, timeout=5) as response:
            return url, 'UP' if response.status == 200 else 'DOWN'
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return url, 'DOWN'
    except Exception as e:
        logging.error(f"Error checking {url}: {e}")
        return url, 'DOWN'


async def check_website_status():
    global status_data
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_status(session, url) for url in data_json]
        results = await asyncio.gather(*tasks)
        status_data = dict(results)

scheduler = BackgroundScheduler(timezone=pytz.utc)
scheduler.add_job(func=lambda: asyncio.run(
    check_website_status()), trigger="interval", seconds=30)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())


@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(status_data)


@app.route('/api/website', methods=['GET'])
def get_website():
    return jsonify(data_json)


@app.route('/')
def index():
    return render_template('app.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1000)
