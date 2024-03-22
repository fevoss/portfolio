import pandas as pd
import numpy as np


def calcular_pesos(label: pd.DataFrame, precos: pd.Series, fator_tempo: float = None) -> pd.Series:
    """Calcula os pesos da amostra considerando a redundância dos labels. Esse método também da mais relevância aos
    labels associados a maiores retornos e permite que adicione um fator que reduz a relevância de amostra
    mais antigas."""

    log_precos = np.log(precos)

    # Estimando labels concorrentes
    c = pd.Series(0, index=log_precos.index)
    for loc in label.index:
        trade = label.loc[loc]
        c.loc[loc:trade.t1] += 1
    c = c.loc[c > 0]

    u = pd.Series(index=label.index)
    w = pd.Series(index=label.index)
    for loc in label.index:
        trade = label.loc[loc]

        # Calcular 'Uniqueness' do label
        u.loc[loc] = (1 / c.loc[loc:trade.t1]).mean()

        # Calcular retornos
        retornos = log_precos.loc[loc: trade.t1].diff()

        # Calculando peso ajustado pelo retorno
        w.loc[loc] = (retornos / c.loc[loc: trade.t1]).sum()

    w = w.abs()
    w *= label.shape[0] / w.sum()

    if fator_tempo is not None:
        fator = u.sort_index().cumsum()
        if fator_tempo >= 0:
            b = (1. - fator_tempo) / fator.iloc[-1]
        else:
            b = 1 / ((fator_tempo + 1) * fator.iloc[-1])
        a = 1. - b * fator.iloc[-1]
        fator = a + b * fator
        fator[fator < 0] = 0
        w *= fator
    return w


if __name__ == "__main__":
    from labeling import aplicar_tripla_barreira
    ativos = pd.read_excel('ativos.xlsx', index_col=0)
    label = aplicar_tripla_barreira(precos=ativos['BTCUSDT'], alvos=pd.Series(0.05, index=ativos.index),
                                    barreira_vertical=5)
    w = calcular_pesos(label, precos=ativos['BTCUSDT'])
    print(w)
