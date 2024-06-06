# import flask, kerangka kerja web mikro untuk membuat web di python
from flask import Flask, jsonify, render_template
# Library untuk membuat HTTP Request
import asyncio
import aiohttp
# Untuk menjadwalkan
from apscheduler.schedulers.background import BackgroundScheduler
# Butuh bantuan ini karena berhubungan dengan zona waktu
import pytz
# library untuk membantu menghentikan semua fungsi ketika program berhenti
import atexit
# Library untuk mencatat segala sesuatu yang terjadi
import logging

# Inisialisasi logging
logging.basicConfig(level=logging.INFO)

# Inisialisasi aplikasi Flask
app = Flask(__name__, template_folder='html', static_folder='css')

# List URL Web yang akan dicek
urls = [
    "https://penabulusamudrawiyata.org/",
    "https://akom-assinniyah.ac.id/",
    "https://aknj.ac.id/cms/",
    "https://akd.ac.id/",
    "https://akts.ac.id/",
    "https://poltekesjember.ac.id/",
    "https://poltekkespim.ac.id/",
    "https://polteksi.ac.id/",
    "https://politama-mjk.ac.id/",
    "https://polimercia.ac.id/",
    "https://www.kertacendekia.ac.id/",
    "https://politeknikmitraglobal.ac.id/",
    "https://polmain.ac.id/",
    "https://mapena.ac.id/",
    "https://untag-sby.ac.id/web/beritadetail/politag-surabaya-resmi-bergabung-dengan-untag-surabaya-sebagai-fakultas-vokasi.html",
    "https://poliwangi.ac.id/",
    "https://itsk-soepraoen.ac.id/",
    "https://pnm.ac.id/",
    "https://stikesmajapahit.ac.id/",
    "http://polisma.ac.id/v/",
    "https://www.pens.ac.id/",
    "https://poltek.ubaya.ac.id/",
    "https://nscpolteksby.ac.id/",
    "https://akbiddharmahusadakdr.ac.id/",
    "https://www.akabi.ac.id/",
    "https://sages.ac.id/",
    "https://akademikesehatansumenep.ac.id/",
    "https://ottimmo.ac.id/",
    "https://gizikaryahusadakediri.ac.id/",
    "https://stikesrustida.ac.id/",
    "https://akbidghs.com/",
    "https://akademifarmasijember.gofeedercloud.com/index.php/login",
    "https://aakdelimahusadagresik.ac.id/",
    "https://uds.ac.id/",
    "https://www.akfarmitseda.ac.id/",
    "https://akupintar.id/universitas/-/kampus/detail-kampus/akademi-kebidanan-sukawati-lawang/profil",
    "https://akbid-dharmapraja.ac.id/",
    "https://kebidanan.unpkediri.ac.id/",
    "https://ubibanyuwangi.ac.id/",
    "https://www.aak-malang.ac.id/",
    "https://wimisada.ac.id/",
    "https://www.akbidwijayakusumakotaternate.com/",
    "https://akafarmaponorogo.ac.id/",
    "https://medikawiyata.ac.id/",
    "https://stikespantiwaluya.ac.id/"  
]

# untuk menyimpan status setiap URL, dictionary kosong
status_data = {}

# Fungsi untuk mengecek status setiap website secara asynchronous
async def fetch_status(session, url):
    try:
        async with session.get(url, timeout=5) as response:
            return url, 'UP' if response.status == 200 else 'DOWN'
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return url, 'DOWN'
    except Exception as e:
        logging.error(f"Error checking {url}: {e}")
        return url, 'DOWN'

# Fungsi untuk mengecek status semua website secara asynchronous
async def check_website_status():
    global status_data
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_status(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        status_data = dict(results)

# Inisialisasi penjadwalan
scheduler = BackgroundScheduler(timezone=pytz.utc)
scheduler.add_job(func=lambda: asyncio.run(check_website_status()), trigger="interval", seconds=30)
scheduler.start()

# Penjadwalan akan berhenti ketika aplikasi berhenti
atexit.register(lambda: scheduler.shutdown())

# untuk mendapatkan status URL dalam format JSON.
@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(status_data)

# Ini untuk htmlnya
@app.route('/')
def index():
    return render_template('index.html')

# jalankan aplikasi Flask
if __name__ == "__main__":
    asyncio.run(check_website_status())
    app.run(host='192.168.76.63', port=5000)
