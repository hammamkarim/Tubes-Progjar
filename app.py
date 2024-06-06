# Flask untuk membuat website di python
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


file_json = 'static/website.json'
data_json = fetch_json(file_json)
urls = {data_web['url']: 'UNKNOWN' for data_web in data_json['data']}

status_data = {}


async def fetch_status(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            return url, 'UP' if response.status == 200 else 'DOWN'
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return url, 'DOWN'
    except Exception as e:
        logging.error(f"Error checking {url}: {e}")
        return url, 'DOWN'


async def check_website_status(url_group):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_status(session, url) for url in url_group]
        results = await asyncio.gather(*tasks)
        for url, status in results:
            status_data[url] = status


def schedule_checks():
    up_urls = [url for url, status in status_data.items() if status == 'UP']
    down_urls = [url for url, status in status_data.items()
                 if status == 'DOWN']
    # unknown_urls = [url for url, status in status_data.items()
    #                 if status == 'UNKNOWN']

    asyncio.run(check_website_status(up_urls))
    asyncio.run(check_website_status(down_urls))
    # asyncio.run(check_website_status(unknown_urls))


scheduler = BackgroundScheduler(timezone=pytz.utc)
scheduler.add_job(func=lambda: asyncio.run(
    check_website_status(urls.keys())), trigger="interval", seconds=60)
scheduler.add_job(func=lambda: schedule_checks(),
                  trigger="interval", seconds=10)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())


@app.route('/api/website', methods=['GET'])
def get_websites():
    return jsonify(data_json)


@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(status_data)


@app.route('/')
def index():
    return render_template('app.html')


if __name__ == "__main__":
    asyncio.run(check_website_status(urls.keys()))
    app.run(host='0.0.0.0', port=1000)
