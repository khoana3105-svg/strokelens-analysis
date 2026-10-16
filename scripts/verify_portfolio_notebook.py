"""Execute the bilingual notebook with the current Python kernel; no installs."""
import argparse
import base64
import json
from pathlib import Path
import sys

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from nbconvert import HTMLExporter

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    path = ROOT / 'notebooks/StrokeLens_Analysis_EN_VI.ipynb'
    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(notebook, timeout=600, kernel_name='python3',
                            resources={'metadata': {'path': str(ROOT)}})
    client.km = KernelManager(kernel_name='python3')
    client.km.kernel_spec.argv = [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}']
    client.execute()
    result = json.loads((ROOT / 'outputs/upgraded_notebook/metrics_upgraded.json').read_text(encoding='utf-8'))
    h = result['holdout']
    notebook.cells[1].source = f'''## Tóm tắt / Executive summary

**VI:** 5.110 hồ sơ, 249 nhãn dương, 201 BMI thiếu. Chọn {result['selected']['family']} bằng CV/OOF trên development. Holdout n={result['holdout_n']}: AP {h['ap']:.4f}, ROC-AUC {h['roc_auc']:.4f}, recall {h['recall']:.1%}, precision {h['precision']:.1%}. Đọc cùng dương tính giả và hạn chế hiệu chuẩn. Đây là chạy lại cùng thí nghiệm và cùng holdout, không phải kiểm định độc lập mới.

**EN:** 5,110 records, 249 recorded positives, 201 missing BMI values. Model selection uses development CV/OOF only. Final holdout n={result['holdout_n']}: AP {h['ap']:.4f}, ROC-AUC {h['roc_auc']:.4f}, recall {h['recall']:.1%}, precision {h['precision']:.1%}. Scores are not calibrated personal future-risk probabilities; this run reproduces the same fixed experiment, not external validation.'''
    count = 0
    preview = ROOT / 'outputs/notebook_review'
    preview.mkdir(parents=True, exist_ok=True)
    for cell in notebook.cells:
        for output in cell.get('outputs', []):
            if output.get('output_type') == 'stream':
                output['text'] = output['text'].replace(str(Path(sys.prefix)), '<notebook-environment>')
            png = output.get('data', {}).get('image/png')
            if png:
                count += 1
                (preview / f'figure-{count:02d}.png').write_bytes(base64.b64decode(png))
    assert not any(o.output_type == 'error' for c in notebook.cells for o in c.get('outputs', []))
    nbformat.validate(notebook)
    nbformat.write(notebook, path)
    html, _ = HTMLExporter(template_name='lab').from_notebook_node(notebook)
    (preview / 'notebook-preview.html').write_text(html, encoding='utf-8')
    print(json.dumps({'cells': len(notebook.cells), 'figures': count, 'holdout': h}, indent=2))


if __name__ == '__main__':
    main()
