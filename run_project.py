"""Run every authoring stage from a single command."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
for name in ['pipeline.py','build_charts.py','build_powerbi.py','build_dashboard.py','build_reports.py','build_notebook.py']:
    subprocess.run([sys.executable,str(root/'src'/name)],check=True,cwd=root)
print('Complete. Start with reports/Executive_Summary.pdf and README.md')
