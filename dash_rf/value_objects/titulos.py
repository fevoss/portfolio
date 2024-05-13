from dataclasses import dataclass, asdict
from dash_rf.utils.calendario import *
from enum import Enum, auto


class Indexador(Enum):
    PRE = auto()
    CDI = auto()

    def __repr__(self):
        return str(self.name)

    def __str__(self):
        return str(self.name)


class Instrumento(Enum):
    LCA = auto()
    LCI = auto()
    CDB = auto()

    def __repr__(self):
        return str(self.name)

    def __str__(self):
        return str(self.name)

    @property
    def eh_isento(self):
        return self in [self.LCA, self.LCI]


@dataclass
class Titulo:
    pu: float
    indexador: Indexador
    instrumento: Instrumento
    qntde: float
    taxa: float
    emissor: str
    dt_compra: date | datetime
    dt_vencimento: date | datetime

    def __post_init__(self):
        if isinstance(self.dt_vencimento, datetime):
            self.dt_vencimento = self.dt_vencimento.date()
        if isinstance(self.dt_compra, datetime):
            self.dt_compra = self.dt_compra.date()
    @property
    def montante_inicial(self):
        return self.pu * self.qntde

    def du_ate_vencimento(self, dt: date) -> int:
        return calcular_du(dt_inicio=dt, dt_fim=self.dt_vencimento)

    def aliquota_ir(self, dt: date = None) -> float:
        if dt is None:
            dt = self.dt_compra
        dias_corridos = (self.dt_vencimento - dt).days
        aliquota = 0.225
        if 181 <= dias_corridos <= 360:
            aliquota = 0.2
        if 361 <= dias_corridos <= 720:
            aliquota = 0.175
        if dias_corridos > 720:
            aliquota = 0.15
        return aliquota * bool(self.instrumento.eh_isento)


    @property
    def maturity_value(self):
        return (1 + self.taxa) ** (self.du_ate_vencimento(dt=self.dt_compra) / 252) * self.pu

    def price_to_market(self, taxa: float, data: datetime):
        return self.maturity_value / ((1 + taxa) ** (calcular_du(dt_inicio=data, dt_fim=self.dt_vencimento) / 252))

    def price_to_market_series(self, taxas: pd.Series, datas: any) -> pd.Series:
        expoente = pd.Series(calcular_du(dt_inicio=datas, dt_fim=self.dt_vencimento), index=datas) / 252
        return self.maturity_value / ((1 + taxas) ** expoente)

    def to_dict(self):
        d = asdict(self)
        for key, value in d.items():
            if isinstance(value, datetime):
                d[key] = value.strftime("%d/%m/%y")
        return d

    @property
    def prazo(self) -> float:
        if self.dt_vencimento > date.today():
            return calcular_du(dt_inicio=date.today(), dt_fim=self.dt_vencimento) / 252
        return 0
