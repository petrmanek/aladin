import requests
import time
import datetime


class Aladin:
    # Large fragments of this class are translations of inline JavaScript at:
    # https://www.chmi.cz/files/portal/docs/meteo/ov/aladin/results/ala.html

    def __init__(self):
        self.session = requests.Session()

    def list_forecasts(self):
        now = int(time.time())
        response = self.session.get(
            f'https://www.chmi.cz/files/portal/docs/meteo/ov/aladin/results/public/mapy/mdirs.txt?{now}')
        response.raise_for_status()

        lines = response.text.splitlines()
        return [int(line) for line in lines if line.strip()]

    def list_ranges(self, forecast):
        # Hard-coded in JavaScript :/
        ranges = ['00', '03', '06', '09', '12', '15', '18', '21', '24', '27', '30', '33',
                  '36', '39', '42', '45', '48', '51', '54', '57', '60', '63', '66', '69', '72']
        row_num = len(ranges)
        if str(forecast)[8:] == '18':
            # range 18UTC produces 54h forecasts instead of 72h
            row_num = len(ranges) - 6

        return ranges[:row_num]

    def list_params(self):
        # Hard-coded in JavaScript :/
        return {
            "T2m": "Teplota ve 2 m [°C]",
            "prec": "Srážky celkové [mm/3h] (s vyšrafovanými oblastmi sněžení)",
            "v10mmslp": "Vítr v 10 m [m/s] (s vyznačenými oblastmi s nárazy větru >15m/s), Tlak přepočtený na hladinu moře [hPa]",
            "nebul": "Oblačnost [černá=jasno, bílá=zataženo]",
            "nebulb": "Oblačnost nízká [černá=jasno, barva=zataženo]",
            "nebulm": "Oblačnost střední [černá=jasno, barva=zataženo]",
            "nebulh": "Oblačnost vysoká [černá=jasno, barva=zataženo]",
            "RH2m": "Relativní vlhkost ve 2m [%]",
            "veind": "Ventilační Index [m^2/s]",
            "Tmxmn": "Teplota minimální/maximální",
            "prec24": "Srážky celkové [mm/24h] (s vyšrafovanými oblastmi sněžení)"
        }

    def retrieve(self, param, forecast, rng, use_legacy_rad, write_buffer):
        rootpath = 'https://www.chmi.cz/files/portal/docs/meteo/ov/aladin/results/public/mapy/data'
        url_to_download = ''

        # Calculate the date we are forecasting for: date of forecast + range
        forecast_str = str(forecast)
        forecast_date = datetime.datetime(int(forecast_str[:4]), int(
            forecast_str[4:6]), int(forecast_str[6:8]), int(forecast_str[8:10]), 0, 0)
        forecast_date += datetime.timedelta(hours=int(rng))
        forecast_rng_hour = forecast_date.hour

        # Check if the file should exist, and download it if it does
        if not (param == 'prec' and rng == '00') and \
           not (param == 'prec24' and int(rng) < 24) and \
           not (param == 'prec24' and forecast_rng_hour != 6) and \
           not (param == 'Tmxmn' and int(rng) < 12) and \
           not (param == 'Tmxmn' and forecast_rng_hour != 6 and forecast_rng_hour != 18):
            if param == 'prec' or param == 'prec24':
                if use_legacy_rad:
                    url_to_download = f'{rootpath}/{forecast}/{param}_public_{rng}.png'
                else:
                    url_to_download = f'{rootpath}/{forecast}/{param}_public_rd_{rng}.png'
            else:
                url_to_download = f'{rootpath}/{forecast}/{param}_public_{rng}.png'

            # Here we essentially stream binary data into arbitrary MemoryIO-like buffer
            response = self.session.get(url_to_download, stream=True)
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=128):
                write_buffer.write(chunk)

            return True

        # Forecast file does not exist
        return False
