from dash_rf.value_objects.titulos import *

x1 = Titulo(pu=1000, indexador=Indexador.PRE, qntde=1, taxa=0.15, emissor='Banco Fibra',
            dt_compra=datetime(2022, 1, 1), dt_vencimento=datetime(2025, 1, 3), instrumento=Instrumento.CDB)
x2 = Titulo(pu=1000, indexador=Indexador.CDI, qntde=2, taxa=0.142, emissor='Banco Master',
            dt_compra=datetime(2022, 1, 1), dt_vencimento=datetime(2025, 7, 3), instrumento=Instrumento.CDB)
x3 = Titulo(pu=1000, indexador=Indexador.PRE, qntde=5, taxa=0.132, emissor='Banco Master',
            dt_compra=datetime(2022, 1, 1), dt_vencimento=datetime(2025, 7, 3), instrumento=Instrumento.CDB)
x4 = Titulo(pu=1000, indexador=Indexador.PRE, qntde=5, taxa=0.132, emissor='Banco Master',
            dt_compra=datetime(2022, 1, 1), dt_vencimento=datetime(2025, 7, 3), instrumento=Instrumento.LCA)

ativos = [x1, x2, x3, x4]

if __name__ == "__main__":
    print(x1.prazo)