from pathlib import Path

import pandas as pd
import pytest

import whatsappbot as bot

EXAMPLE_CSV = Path(__file__).resolve().parent.parent / 'message_list.example.csv'


class FakeBrowser:
    window_handles = ['janela-principal']


def test_load_message_list_adiciona_status_pendente():
    message_list = bot.load_message_list(EXAMPLE_CSV)

    assert list(message_list.columns) == ['Number', 'Message', 'Status']
    assert (message_list['Status'] == bot.PENDING).all()
    assert message_list['Number'].iloc[0] == '11999990001'


def test_load_message_list_exige_colunas(tmp_path):
    arquivo = tmp_path / 'lista.csv'
    arquivo.write_text('Telefone,Texto\n11999990001,Oi\n', encoding='utf-8')

    with pytest.raises(ValueError, match='Number'):
        bot.load_message_list(arquivo)


def test_send_pending_messages_registra_status_e_pula_enviadas(tmp_path):
    message_list = pd.DataFrame({
        'Number': ['11999990001', '11999990002', '11999990003'],
        'Message': ['a', 'b', 'c'],
        'Status': [bot.PENDING, bot.SENT, bot.PENDING],
    })
    result_path = tmp_path / 'result.xlsx'
    chamados = []

    def fake_send(browser, number, message):
        chamados.append(number)
        return number == '11999990001'

    bot.send_pending_messages(FakeBrowser(), message_list, result_path, send=fake_send)

    assert chamados == ['11999990001', '11999990003']
    assert list(message_list['Status']) == [bot.SENT, bot.SENT, bot.ERROR]
    salvo = pd.read_excel(result_path, dtype={'Number': str})
    assert list(salvo['Status']) == [bot.SENT, bot.SENT, bot.ERROR]
