import pandas as pd
from datetime import datetime, timedelta
import pyettj.modelo_ettj as modelo_ettj
import numpy as np


class UsaMacro:

    def obter_ultima_curva_pre_disponivel(self):
        ano = datetime.now().year
        base = 'https://home.treasury.gov/resource-center/data-chart-center'
        url = rf'{base}/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value={ano}'
        df = pd.read_html(url)[0]
        datas = [datetime.strptime(i, "%m/%d/%Y") for i in df['Date']]
        colunas = ['1 Mo', '2 Mo', '3 Mo', '4 Mo', '6 Mo', '1 Yr', '2 Yr', '3 Yr', '5 Yr', '7 Yr', '10 Yr', '20 Yr',
                   '30 Yr']
        df = df[colunas] / 100
        df.index = datas
        curva = df.loc[df.index.max()]

        dias_corridos = []
        for loc in curva.index:
            if 'Mo' in loc:
                dias_corridos.append(int(loc[:-3]) / 12)
            elif 'Yr' in loc:
                dias_corridos.append(int(loc[:-3]))
        p = modelo_ettj.calibrar_curva_svensson(np.array(dias_corridos), curva.values)
        t = np.arange(1, 30, 0.01)
        data = df.index.max().to_pydatetime()
        taxas = pd.Series(modelo_ettj.svensson(*p, t),
                          index=[data + timedelta(days=int(i * 365.25)) for i in t.tolist()],
                          name=data.strftime("%d/%m/%y"))
        return taxas


if __name__ == "__main__":
    print(UsaMacro().obter_ultima_curva_pre_disponivel())

