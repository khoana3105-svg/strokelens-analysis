"""Fetch version 1 directly from its educational-use Kaggle publisher."""
import hashlib
import io
import json
from pathlib import Path
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REF = 'fedesoriano/stroke-prediction-dataset'
URL = f'https://www.kaggle.com/api/v1/datasets/download/{REF}?datasetVersionNumber=1'


def main():
    metadata_url = f'https://www.kaggle.com/api/v1/datasets/view/{REF}'
    with urllib.request.urlopen(metadata_url, timeout=60) as response:
        metadata = json.load(response)
    description = metadata.get('description', '')
    if 'Use only for educational purposes' not in description:
        raise RuntimeError('Source terms changed. Review before downloading.')
    with urllib.request.urlopen(URL, timeout=60) as response:
        archive = response.read()
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        payload = z.read('healthcare-dataset-stroke-data.csv')
    destination = ROOT / 'data' / 'raw' / 'healthcare-dataset-stroke-data.csv'
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.read_bytes() != payload:
        raise RuntimeError('Existing raw data differs; refusing to overwrite.')
    destination.write_bytes(payload)
    provenance = {'publisher': 'fedesoriano', 'source': f'https://www.kaggle.com/datasets/{REF}',
                  'download_url': URL, 'version': 1, 'release': '2021-01-26',
                  'license_label': metadata.get('licenseName'),
                  'terms': 'Use only for educational purposes; credit the author.',
                  'sha256': hashlib.sha256(payload).hexdigest(), 'bytes': len(payload),
                  'conversion': 'None. Original CSV bytes extracted from official ZIP.',
                  'units': {'age': 'years', 'bmi': 'kg/m²',
                            'avg_glucose_level': 'source numeric units; mg/dL convention assumed, not confirmed in source dictionary'}}
    (ROOT / 'docs' / 'provenance.json').write_text(json.dumps(provenance, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(provenance, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
