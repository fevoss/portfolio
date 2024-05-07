import pandas as pd

ativos = pd.read_excel('ativos.xlsx', index_col=0).columns.tolist()