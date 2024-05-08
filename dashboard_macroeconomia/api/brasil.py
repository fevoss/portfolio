from datetime import datetime, timedelta
import pandas as pd
import numpy as np


def obter_ultima_curva_pre_disponivel() -> pd.Series:
    import pyettj.ettj as ettj
    import pyettj.modelo_ettj as modelo_ettj
    ate = datetime.now()
    if ate.hour < 20:
        ate = ate - timedelta(days=1)
    de = datetime.now() - timedelta(days=8)
    data = ettj.listar_dias_uteis(de.strftime("%d/%m/%Y"), ate.strftime("%d/%m/%Y"))[-1]
    data = datetime.strptime(data, "%Y-%m-%d")
    curva = ettj.get_ettj(data=data.strftime("%d/%m/%Y"), curva='PRE')
    t = curva['Dias Corridos'] / 252
    y = curva[curva.columns[1]] / 100
    p = pd.Series(modelo_ettj.calibrar_curva_svensson(t.values, y.values),
                  index=['beta1', 'beta2', 'beta3', 'beta4', 'lambda1', 'lambda2'])
    t = np.arange(1, 2521, 1)
    taxas = pd.Series(modelo_ettj.svensson(*p, t / 252),
                      index=[data + timedelta(days=i) for i in t.tolist()],
                      name=data.strftime("%d/%m/%y"))
    return taxas


def obter_historico_embi() -> pd.Series:
    import ipeadatapy as ipea
    embi_mais = ipea.timeseries('JPM366_EMBI366')['VALUE (-)'].dropna()
    embi_mais.name = 'EMBI (+)'
    return embi_mais


def obter_dolar_esperado() -> pd.Series:
    import bcb
    em = bcb.Expectativas()
    ep = em.get_endpoint('ExpectativasMercadoAnuais')
    df = ep.query().filter(ep.Indicador ==
                           'Câmbio').filter(ep.Data >= (datetime.today()
                                                            - timedelta(days=15)).strftime("%Y-%m-%d")).collect()
    df = df.set_index('Data')[['Media', 'DataReferencia', 'baseCalculo', 'numeroRespondentes']]
    dia = df.index.max()
    df = df[(df['baseCalculo'] == 0)].loc[dia].set_index('DataReferencia')['Media']
    df.name = dia
    return df


if __name__ == "__main__":
    print(obter_dolar_esperado())