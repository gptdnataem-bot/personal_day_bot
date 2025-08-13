import requests

ECB_URL = "https://data.ecb.europa.eu/api/1.0/data/EXR/D..EUR.SP00.A?lastNObservations=1&format=jsondata"

def fetch_currencies(symbols = ('USD','RUB','GBP')):
    try:
        r = requests.get(ECB_URL, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        series_list = data.get('dataSets', [{}])[0].get('series', {})
        structure = data.get('structure', {}).get('dimensions', {}).get('series', [])
        currencies = structure[1]['values'] if len(structure) > 1 else []
        idx_to_ccy = {i: v.get('id') for i, v in enumerate(currencies)}
        rates = {}
        for key, series in series_list.items():
            parts = key.split(':')
            if len(parts) < 2: 
                continue
            cidx = int(parts[1])
            ccy = idx_to_ccy.get(cidx)
            if ccy and ccy in symbols:
                obs = series.get('observations', {})
                if obs:
                    last = list(obs.values())[-1]
                    rate = last[0]
                    rates[ccy] = rate
        if not rates:
            return None
        lines = [f"1 EUR = {rates[s]:.4f} {s}" for s in rates if s in symbols]
        return "; ".join(lines)
    except Exception:
        return None
