from components.config import PASTA_ENTRADA
from components.pii_detector import PIIDetector

#                          ==================Ponto de entrada principal do sistema.=================
def main():
#     Busca automaticamente o primeiro arquivo Excel/CSV na pasta configurada
    arquivo_entrada = None
#     Procura arquivos Excel (.xlsx)
    arquivos_xlsx = list(PASTA_ENTRADA.glob('*.xlsx'))
    if arquivos_xlsx:
        arquivo_entrada = arquivos_xlsx[0]
    if not arquivo_entrada:
        arquivos_xls = list(PASTA_ENTRADA.glob('*.xls'))
        if arquivos_xls:
            arquivo_entrada = arquivos_xls[0]

#     Se não encontrou Excel, procura .csv
    if not arquivo_entrada:
        arquivos_csv = list(PASTA_ENTRADA.glob('*.csv'))
        if arquivos_csv:
            arquivo_entrada = arquivos_csv[0]
    if not arquivo_entrada:
        print(" ERRO: Arquivo de dados não encontrado!")
        print(f" Coloque um arquivo Excel (.xlsx) ou CSV na pasta: {PASTA_ENTRADA}")
        return
    
#     Inicializa detector com threshold conservador
    detector = PIIDetector(threshold=30)
    detector.processar_arquivo(str(arquivo_entrada))
    print(" Processamento concluído com sucesso!")

if __name__ == '__main__':
    main()