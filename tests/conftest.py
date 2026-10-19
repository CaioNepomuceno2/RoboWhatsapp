import sys
from pathlib import Path

# Permite importar `helpers` e `whatsappbot` como no uso normal do script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'whatsappbot'))
