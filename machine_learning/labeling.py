import pandas as pd
import numpy as np


# Execute esse código para entender o método de labeling

def aplicar_tripla_barreira(precos: pd.Series,
                            alvos: pd.Series,
                            barreira_vertical: int = None,
                            tp_fator: float = 1,
                            sl_fator: float = 1,
                            min_alvo: float = 0,
                            sinais: pd.Series | None = None) -> pd.DataFrame:
    """
    :param precos: pd.Series. Série de precos do ativo.
    :param alvos: pd.Series. É a retorno em que StopLoss/Takeprofit serão ativados.
    :param barreira_vertical:  int. Quantidade N de preços até que a operação sai indepentemente da ativação
    do StopLoss/Takeprofit.
    :param tp_fator: É o fator multiplicador do alvo para o TakeProfit.
    :param sl_fator: É o fator multiplicador do alvo para o StopLoss.
    :param min_alvo: É o alvo mínimo para se colocar um label.
    :param sinais: Caso já haja sinais, o metalabel será aplicado.
    """

    df = pd.DataFrame(columns=['t1', 'retorno', 'label' if sinais is None else 'metalabel'])

    if not isinstance(precos.index, pd.DatetimeIndex):
        raise ValueError("O index dos preços tem que ser pd.DatetimeIndex")

    if not precos.index.equals(alvos.index):
        raise ValueError("O index dos preços e dos alvos precisam ser idênticos.")

    log_precos = np.log(precos)

    for iloc, loc in enumerate(precos.index):

        alvo = alvos.loc[loc]

        if alvo < min_alvo:
            continue

        loc_max = np.nan
        if iloc + barreira_vertical < precos.shape[0] - 1:
            loc_max = log_precos.index[iloc + barreira_vertical]
            retornos = log_precos.loc[loc:loc_max].diff().fillna(0).cumsum()
        else:
            retornos = log_precos.loc[loc:].diff().fillna(0).cumsum()

        if sinais is not None:
            retornos *= sinais.loc[loc]

        t_takeprofit = retornos[retornos > alvo * tp_fator].index.min()
        t_stoploss = retornos[retornos < -alvo * sl_fator].index.min()

        # pd.Series lida com os valores nulos
        t1 = pd.Series([loc_max, t_stoploss, t_takeprofit]).min()
        if not pd.isna(t1):
            df.loc[loc, 'retorno'] = retornos.loc[t1]
            df.loc[loc, 't1'] = t1

    df[df.columns[-1]] = np.sign(df['retorno'])

    df.index.name = 't0'
    return df


if __name__ == "__main__":
    ativos = pd.read_excel('ativos.xlsx', index_col=0)
    label = aplicar_tripla_barreira(precos=ativos['BTCUSDT'], alvos=pd.Series(0.05, index=ativos.index),
                                    barreira_vertical=5)
    print(label)
