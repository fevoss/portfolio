from dataclasses import dataclass, field
import pandas as pd
import numpy as np


@dataclass()
class Diferenciador:
    d: float
    limite_peso: float = 0.0001
    _pesos: None | pd.Series = field(default=None, init=False)

    def __post_init__(self):
        if self.d < 0:
            raise Exception("Condição: D > 0 não satisfeito.")
        self._pesos = self._calc_pesos()
        # O limite da janela é definido pela combinação de grau de diferenciação e limite_compra peso
        self._janela = len(self._pesos)

    def _calc_pesos(self) -> pd.Series:
        """
        Cria o vetor de pesos para derivar a série parcialmente diferenciada.
        """
        pesos: list[float] = [1]
        i = 1
        while abs(pesos[-1]) > self.limite_peso:
            pesos.append(-pesos[-1] / i * (self.d - i + 1))
            i += 1
        return pd.Series(pesos[::-1])

    def calcular(self, log_precos: pd.Series) -> pd.Series:
        """
        Recomenda-se utilizar os log-preços para que a série seja mais heterocedastica.
        """
        dif_precos = pd.Series(dtype=float)
        for iloc, loc in enumerate(log_precos.index):
            if iloc < self._janela:
                dif_precos.loc[loc] = np.nan
            else:
                dif_precos.loc[loc] = np.dot(self._pesos.T, log_precos.loc[:loc].iloc[-self._janela:])
        return dif_precos


if __name__ == "__main__":
    ativos = pd.read_excel('ativos.xlsx', index_col=0)
    precos_diferenciados = Diferenciador(d=0.4).calcular(log_precos=np.log(ativos['BTCUSDT']))

    import matplotlib.pyplot as plt

    fig, ax1 = plt.subplots(figsize=(8, 8))
    ax2 = ax1.twinx()

    ax1.plot(np.log(ativos['BTCUSDT']), color='blue', alpha=0.5)
    ax2.plot(precos_diferenciados, color='black', alpha=0.5)

    ax1.set_xlabel('Data')
    ax1.set_ylabel('BTCUSDT', color='blue', fontsize=14)
    ax1.tick_params(axis="y", labelcolor='blue')

    ax2.set_ylabel('Dif_BTCUSDT', color='black', fontsize=14)
    ax2.tick_params(axis="y", labelcolor='black')

    fig.suptitle('Diferenciação Parcial', fontsize=20)
    fig.autofmt_xdate()
    plt.show()
