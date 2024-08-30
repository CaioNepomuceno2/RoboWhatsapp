# import helpers
# import os
# import pandas as pd
# from glob import glob
# from datetime import datetime

# os.chdir(os.path.dirname(os.path.abspath(__file__)))

# browser = helpers.get_browser()
# helpers.open_whatsapp(browser)

# message_list = pd.read_excel('../message_list.xlsx')
# attachments_path = os.path.abspath('../assets')
# attachment_list = glob(f'{attachments_path}/*[.jpg, .jfif]')
# current_time = datetime.now().strftime('%d_%m_%Y-%H_%M')

# indices_to_drop = []  # Lista para manter o controle dos índices das linhas enviadas

# try:
#     for row in message_list.itertuples():
#         try:
#             result = helpers.send_message(
#                 browser, row.Number, row.Message, attachment_list
#             )
#         except Exception as ex:
#             print(f'Erro ao enviar a mensagem para {row.Number}: {ex}')
#             result = False

#         status = 'Enviada' if result else 'Erro'
#         message_list.loc[row.Index, 'Status'] = status

#         # Escreve o resultado no arquivo Excel após cada iteração
#         message_list.to_excel(f'../result_{current_time}.xlsx', index=False)

#         # Se a mensagem foi enviada, adiciona o índice à lista para excluir
#         if result:
#             indices_to_drop.append(row.Index)
            
#         # Interrompe o loop se o navegador for fechado
#         if not browser.window_handles:
#             print("Navegador foi fechado inesperadamente.")
#             break
            
#     # Exclui as linhas processadas da DataFrame original
#     message_list = message_list.drop(indices_to_drop)

#     # # Exclui as linhas processadas da DataFrame original
#     # message_list = message_list.drop(indices_to_drop)

#     # Salva a DataFrame final após a remoção das linhas enviadas
#     message_list.to_excel(f'../result_final_{current_time}.xlsx', index=False)

# except Exception as e:
#     # # Exclui as linhas processadas da DataFrame original
#     message_list = message_list.drop(indices_to_drop)
#     print(f'Erro durante o envio das mensagens: {e}')

# finally:
#     # Salva qualquer progresso antes de sair em caso de exceção
#     message_list = message_list.drop(indices_to_drop)
#     message_list.to_excel(f'../result_interrupted_{current_time}.xlsx', index=False)
#     browser.quit()



# # ... o resto do código acima permanece igual ...


import helpers
import os
import pandas as pd
from glob import glob
from datetime import datetime

def save_progress(message_list, file_path):
    """Função auxiliar para salvar o progresso em um arquivo Excel."""
    message_list.to_excel(file_path, index=False)

# Defina o diretório de trabalho para o diretório do script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

browser = helpers.get_browser()
helpers.open_whatsapp(browser)

message_list = pd.read_excel('../message_list.xlsx')
attachments_path = os.path.abspath('../assets')
attachment_list = glob(f'{attachments_path}/*[.jpg, .png, .jfif]')
current_time = datetime.now().strftime('%d_%m_%Y-%H_%M')
result_file_path = f'../result_{current_time}.xlsx'  # Caminho do arquivo de resultado

# Inicialize o arquivo de resultados, se ainda não existir
if not os.path.exists(result_file_path):
    message_list['Status'] = 'Pendente'  # Adiciona uma coluna de Status
    save_progress(message_list, result_file_path)

# Carrega a lista de mensagens com o status para manter o controle de quem já foi enviado
message_list = pd.read_excel(result_file_path)

try:
    for row in message_list.itertuples():
        if row.Status == 'Pendente':  # Verifica se a mensagem ainda está pendente
            try:
                result = helpers.send_message(
                    browser, row.Number, row.Message, attachment_list
                )
            except Exception as ex:
                print(f'Erro ao enviar a mensagem para {row.Number}: {ex}')
                result = False

            status = 'Enviada' if result else 'Erro'
            message_list.loc[row.Index, 'Status'] = status
            save_progress(message_list, result_file_path)  # Atualiza o arquivo de resultado
            
            # Interrompe o loop se o navegador for fechado
            if not browser.window_handles:
                print("Navegador foi fechado inesperadamente.")
                break

except Exception as e:
    print(f'Erro durante o envio das mensagens: {e}')

finally:
    # Salva qualquer progresso antes de sair em caso de exceção
    save_progress(message_list, result_file_path)
    browser.quit()
