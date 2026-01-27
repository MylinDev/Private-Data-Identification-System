import pandas as pd
from pathlib import Path
from typing import Dict

class FileProcessor:

#        Processa arquivo Excel/CSV com textos e gera resultado classificado.
    def processar_arquivo(self, arquivo_entrada: str, arquivo_saida: str = None, detector_callback=None):
        print(f"\n{'='*70}")
        print(f"  SISTEMA DE DETECÇÃO ")
        print(f"{'='*70}\n")
        
#         Define arquivo de saída padrão
        if arquivo_saida is None:
            arquivo_saida = Path(__file__).parent.parent.parent / 'Resultado' / 'resultado.xlsx'
        
#         Lê arquivo de entrada
        print(f" Lendo arquivo: {arquivo_entrada}")

        if arquivo_entrada.endswith('.csv'):
            df = pd.read_csv(arquivo_entrada)
        else:
            df = pd.read_excel(arquivo_entrada, engine='openpyxl')
        
        print(f"  {len(df)} registros carregados")
        
#         Identifica coluna de texto
        coluna_texto = None
        for col in df.columns:
            if 'texto' in col.lower() or 'conteúdo' in col.lower() or 'conteudo' in col.lower():
                coluna_texto = col
                break
        if coluna_texto is None:

#             Usa segunda coluna se não encontrar
            coluna_texto = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        print(f" OK-> Coluna de texto identificada: '{coluna_texto}'")
        print(f"\n Processando textos...\n")
        
#         Processa cada texto
        resultados = []
        for idx, row in df.iterrows():
            texto = str(row[coluna_texto]) if pd.notna(row[coluna_texto]) else ""
            
#             Detecta PII usando callback
            resultado = detector_callback(texto) if detector_callback else {'entidades': {}, 'score': 0, 'classificacao': 'PUBLICO', 'resumo': []}
            
#             Formata resumo para Excel
            entidades_str = ', '.join(resultado['resumo']) if resultado['resumo'] else 'Nenhuma'
            
            resultados.append({
                'ID': row[df.columns[0]],  # Primeira coluna como ID
                'Texto Mascarado': texto,
                'ENTIDADES_ENCONTRADAS': entidades_str,
                'CLASSIFICACAO': resultado['classificacao'],
                'SCORE': resultado['score']
            })
            
            if (idx + 1) % 10 == 0:
                print(f"   Processados: {idx + 1}/{len(df)}")
        
#         Cria DataFrame de resultado
        df_resultado = pd.DataFrame(resultados)
        
#         Estatísticas
        total_privado = (df_resultado['CLASSIFICACAO'] == 'PRIVADO').sum()
        total_publico = (df_resultado['CLASSIFICACAO'] == 'PUBLICO').sum()
        
        print(f"\n{'='*70}")
        print(f"  RESULTADO DA CLASSIFICAÇÃO")
        print(f"{'='*70}")
        print(f"  Total de registros: {len(df_resultado)}")
        print(f"   PRIVADO: {total_privado} ({total_privado/len(df_resultado)*100:.1f}%)")
        print(f"   PUBLICO: {total_publico} ({total_publico/len(df_resultado)*100:.1f}%)")
        print(f"{'='*70}\n")
        
#         Salva resultado
        df_resultado.to_excel(arquivo_saida, index=False, engine='openpyxl')
        print(f" Resultado salvo em: {arquivo_saida}\n")
        return df_resultado