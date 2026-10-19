"""Envia mensagens pelo WhatsApp Web a partir de uma planilha.

A planilha precisa das colunas `Number` (DDD + número, sem o +55) e
`Message`. O status de cada envio é gravado em `result_<data>.xlsx` após
cada mensagem, para não perder o progresso se a execução for interrompida.
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

import helpers

if getattr(sys, 'frozen', False):  # executável gerado pelo PyInstaller
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_INPUT = BASE_DIR / 'message_list.xlsx'
REQUIRED_COLUMNS = ('Number', 'Message')
PENDING, SENT, ERROR = 'Pendente', 'Enviada', 'Erro'


def load_message_list(path):
    """Lê a planilha (.xlsx ou .csv) e garante a coluna `Status`.

    Se o arquivo já tiver `Status` (por exemplo, um result_*.xlsx de uma
    execução anterior), apenas as linhas 'Pendente' serão enviadas.
    """
    path = Path(path)
    if path.suffix.lower() == '.csv':
        message_list = pd.read_csv(path, dtype={'Number': str})
    else:
        message_list = pd.read_excel(path, dtype={'Number': str})

    missing = [col for col in REQUIRED_COLUMNS if col not in message_list.columns]
    if missing:
        raise ValueError(f'Colunas obrigatórias ausentes na planilha: {", ".join(missing)}')

    if 'Status' not in message_list.columns:
        message_list['Status'] = PENDING
    message_list['Status'] = message_list['Status'].fillna(PENDING).astype(str)
    return message_list


def save_progress(message_list, file_path):
    """Salva a planilha com o status atual de cada mensagem."""
    message_list.to_excel(file_path, index=False)


def send_pending_messages(browser, message_list, result_path, send=helpers.send_message):
    """Envia as mensagens pendentes, atualizando o arquivo de resultado a cada envio."""
    for row in message_list.itertuples():
        if row.Status != PENDING:
            continue

        try:
            result = send(browser, row.Number, row.Message)
        except Exception as ex:
            print(f'Erro ao enviar a mensagem para {row.Number}: {ex}')
            result = False

        message_list.loc[row.Index, 'Status'] = SENT if result else ERROR
        save_progress(message_list, result_path)

        if not browser.window_handles:
            print('Navegador foi fechado inesperadamente.')
            break

    return message_list


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description='Envia mensagens do WhatsApp Web a partir de uma planilha.')
    parser.add_argument('--entrada', default=str(DEFAULT_INPUT),
                        help='planilha .xlsx ou .csv com as colunas Number e Message '
                             '(padrão: message_list.xlsx na raiz do projeto)')
    parser.add_argument('--navegador', choices=('edge', 'chrome'), default='edge',
                        help='navegador usado pelo Selenium (padrão: edge)')
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    message_list = load_message_list(args.entrada)

    current_time = datetime.now().strftime('%d_%m_%Y-%H_%M')
    result_path = BASE_DIR / f'result_{current_time}.xlsx'
    save_progress(message_list, result_path)

    browser = helpers.get_browser(args.navegador)
    try:
        helpers.open_whatsapp(browser)
        send_pending_messages(browser, message_list, result_path)
    except Exception as e:
        print(f'Erro durante o envio das mensagens: {e}')
    finally:
        save_progress(message_list, result_path)
        print(f'Resultado salvo em: {result_path}')
        try:
            browser.quit()
        except Exception:
            pass  # o navegador já pode ter sido fechado pelo usuário


if __name__ == '__main__':
    main()
