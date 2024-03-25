from sklearn.metrics import log_loss, accuracy_score, f1_score, recall_score, precision_score
from sklearn.model_selection._split import _BaseKFold
import pandas as pd
import numpy as np


class ExpurgarKFold(_BaseKFold):

    def __init__(self, t1: pd.Series, n_divisoes=3, pct_embargo=0.01):

        """
        Remove os eventos de treinamento que tenham overlap com os eventos de teste, assim possibilita que não haja
        vazamento de informação do conjunto de treinamento para o teste devido ao overlap dos labels.  Além disso,
        possibilita determina um período de embargo nos conjunto de treino que seja temporalmente posterior ao conjuno
        de teste, assim evitando que a correlação serial possa indesejavelmente inflar o poder preditivo do modelo.

        """

        super(ExpurgarKFold, self).__init__(n_splits=n_divisoes, shuffle=False, random_state=None)

        self.n_divisoes = n_divisoes
        self.t1 = t1.copy()
        self.pct_embargo = pct_embargo

    def split(self, x: pd.DataFrame, y: pd.Series = None, groups=None):

        if not x.index.equals(self.t1.index):
            raise ValueError('O index das features X precisa ser o mesmo index de t1')

        n_linhas_embargo = int(x.shape[0] * self.pct_embargo)

        indices = np.arange(x.shape[0])
        indexes_testes = [(i[0], i[-1] + 1) for i in np.array_split(indices, self.n_divisoes)]

        for i, j in indexes_testes:

            # Definindo o período de tempo que o teste utiliza
            indice_teste = indices[i:j]
            t0_teste = self.t1.iloc[indice_teste].index.min()
            t1_teste = self.t1.iloc[indice_teste].max()

            # Filtrando o treino antes do teste para que não tenha sobreposição com o teste que vem depois.
            treino_antes_do_teste = self.t1.iloc[:i]
            treino_antes_do_teste = treino_antes_do_teste[treino_antes_do_teste < t0_teste]

            # Filtrando o treino depois para que não haja sobreposição com o teste que vem antes.
            treino_depois_do_teste = self.t1.iloc[j:]
            treino_depois_do_teste = treino_depois_do_teste[treino_depois_do_teste > t1_teste]

            # 2) Previnindo contra a correlação serial através do embargo
            treino_depois_do_teste = treino_depois_do_teste.iloc[n_linhas_embargo:]
            indice_treino = treino_antes_do_teste.index.union(treino_depois_do_teste.index)
            indice_treino = [self.t1.index.get_loc(i) for i in indice_treino]
            yield indice_treino, indice_teste


def validacao_cruzada_score(clf: any,
                            x: pd.DataFrame | pd.Index,
                            y: pd.Series,
                            weights: pd.Series,
                            t1: pd.Series,
                            metrica='neg_log_loss',
                            n_divisoes: int = 3,
                            pct_embargo: float = 0.01) -> np.array:

    cv_gen = ExpurgarKFold(n_divisoes=n_divisoes, t1=t1, pct_embargo=pct_embargo)

    score = []

    for treino, teste in cv_gen.split(x=x):
        fit = clf.fit(X=x.iloc[treino], y=y.iloc[treino], sample_weight=weights.iloc[treino].values)
        match metrica:
            case 'neg_log_loss':
                score_metrica = -log_loss(y.iloc[teste],
                                          y_pred=fit.predict_proba(x.iloc[teste, :]),
                                          sample_weight=weights.iloc[teste].values,
                                          labels=clf.classes_)
                score.append(score_metrica)
            case 'accuracy':
                score_metrica = accuracy_score(y.iloc[teste],
                                               y_pred=fit.predict(x.iloc[teste, :]),
                                               sample_weight=weights.iloc[teste].values)
                score.append(score_metrica)
            case 'f1':
                score_metrica = f1_score(y.iloc[teste],
                                         y_pred=fit.predict(x.iloc[teste, :]),
                                         sample_weight=weights.iloc[teste].values)
                score.append(score_metrica)
            case 'recall':
                score_metrica = recall_score(y.iloc[teste],
                                             y_pred=fit.predict(x.iloc[teste, :]),
                                             sample_weight=weights.iloc[teste].values)
                score.append(score_metrica)
            case 'precision':
                score_metrica = precision_score(y.iloc[teste],
                                                y_pred=fit.predict(x.iloc[teste, :]),
                                                sample_weight=weights.iloc[teste].values)
                score.append(score_metrica)
            case _:
                raise ValueError(f"Métrica de Performance {metrica} inválida.")
    return np.array(score)


if __name__ == "__main__":
    from sklearn.ensemble import RandomForestClassifier
    from machine_learning.labeling import aplicar_tripla_barreira
    from machine_learning.weights import calcular_pesos

    ativos = pd.read_excel('ativos.xlsx', index_col=0)
    label = aplicar_tripla_barreira(precos=ativos['BTCUSDT'], alvos=pd.Series(0.05, index=ativos.index),
                                    barreira_vertical=5)
    label['pesos'] = calcular_pesos(precos=ativos['BTCUSDT'], label=label)

    modelo = RandomForestClassifier(criterion='entropy',
                                    class_weight='balanced_subsample',
                                    n_estimators=200,
                                    max_samples=label['pesos'].mean(),
                                    max_features=1,
                                    min_weight_fraction_leaf=0.05,
                                    oob_score=True,
                                    random_state=1)

    x = pd.DataFrame(0.5, index=label.index, columns=['feature_1', 'feature_2'])

    score = validacao_cruzada_score(clf=modelo, x=x,  y=label['label'], weights=label['pesos'], t1=label['t1'],
                                    metrica='accuracy',  n_divisoes=3, pct_embargo=0.01)

    print(score)

