import numpy as np
import pandas as pd
import math
from sklearn.metrics import log_loss, accuracy_score, f1_score, recall_score, precision_score
from machine_learning.cross_validation import ExpurgarKFold, validacao_cruzada_score


def mdi(clf: any, features: pd.DataFrame, classificacoes: pd.Series, pesos: pd.Series):
    """
    Mean Decrease Impurity (MDI) é um método rápido In-Sample (IS) para tree-based classificadores.

    Observações:
     1) Como é IS, todas as features terão alguma importância sem considerar seu poder preditivo.
     2) Resultados entre 0 e 1.
     3) Dilui a importância sob efeitos substitutos.
     4) Devido ao modo como a impureza é calculada, esse indicador tem um viés em relação a alguns preditores.
    """

    fit = clf.fit(X=features, y=classificacoes, sample_weight=pesos)
    df0 = {i: arvore.feature_importances_ for i, arvore in enumerate(fit.estimators_)}
    df0 = pd.DataFrame.from_dict(df0, orient='index')
    df0.columns = features.columns

    # As estimativas zerados demonstram features com importance nula
    impureza = pd.concat({'mean': df0.mean(), 'sd': df0.std() / math.sqrt(df0.shape[0])}, axis=1)
    impureza /= impureza['mean'].sum()
    impureza = impureza.sort_values('mean', ascending=False)
    return impureza


def mda(clf: any, features: pd.DataFrame, classificacoes: pd.Series, pesos: pd.Series,
        t1: pd.Series, n_divisoes: int, criterio_performance: str = 'neg_log_loss', pct_embargo: float = 0.01):
    """
    MDA (Mean Decrease Accuracy) é um método devagar que mede a redução da performance OOS
    (accuracy, negative_log_loss, ...) devido a ausência de uma feature específica. A ausência é simulada com a
    permutação da feature.

    Observações:
        1) Devido aos efeitos substitutos, esse método pode sugerir irrelevância de features importantes.
        2) É possível a conclusão de que todos os atributos são irrelevantes.
        3) A features pode ter relevância negativa, indicando piora da performance do modelo na presença dessa
        features.
    """

    cv_generator = ExpurgarKFold(n_divisoes=n_divisoes, t1=t1, pct_embargo=pct_embargo)

    score = pd.Series(dtype='float64')
    score_permutado = pd.DataFrame(columns=features.columns, dtype='float64')

    for i, (treino, teste) in enumerate(cv_generator.split(x=features)):
        x_treino = features.iloc[treino]
        y_treino = classificacoes.iloc[treino]
        peso_treino = pesos.iloc[treino]
        x_teste = features.iloc[teste]
        y_teste = classificacoes.iloc[teste]
        peso_teste = pesos.iloc[teste]
        fit = clf.fit(X=x_treino, y=y_treino, sample_weight=peso_treino)
        match criterio_performance:
            case 'neg_log_loss':
                score.loc[i] = -log_loss(y_true=y_teste,
                                         y_pred=fit.predict_proba(x_teste),
                                         sample_weight=peso_teste.values,
                                         labels=clf.classes_)
            case 'accuracy':
                score.loc[i] = accuracy_score(y_true=y_teste,
                                              y_pred=fit.predict(x_teste),
                                              sample_weight=peso_teste.values)

            case 'f1':
                previsao = fit.predict(x_teste)
                score.loc[i] = f1_score(y_true=y_teste,
                                        y_pred=previsao,
                                        sample_weight=peso_teste.values)

            case 'recall':
                previsao = fit.predict(x_teste)
                score.loc[i] = recall_score(y_teste,
                                            previsao,
                                            sample_weight=peso_teste.values)
            case 'precision':
                previsao = fit.predict(x_teste)
                score.loc[i] = precision_score(y_teste,
                                               previsao,
                                               sample_weight=peso_teste.values)

        for j in x_teste.columns:
            x_teste_permutado = x_teste.copy(deep=True)
            np.random.shuffle(x_teste_permutado[j].values)  # Permutação de uma coluna para quebrar a relação
            match criterio_performance:
                case 'neg_log_loss':
                    score_permutado.loc[i, j] = -log_loss(y_true=y_teste,
                                                          y_pred=fit.predict_proba(x_teste_permutado),
                                                          sample_weight=peso_teste.values,
                                                          labels=clf.classes_)
                case'accuracy':
                    score_permutado.loc[i, j] = accuracy_score(y_true=y_teste,
                                                               y_pred=fit.predict(x_teste_permutado),
                                                               sample_weight=peso_teste.values)
                case 'f1':
                    previsao = fit.predict(x_teste_permutado)
                    score_permutado.loc[i, j] = f1_score(y_teste, previsao, sample_weight=peso_teste.values)
                case 'recall':
                    previsao = fit.predict(x_teste_permutado)
                    score_permutado.loc[i, j] = recall_score(y_teste, previsao, sample_weight=peso_teste.values)

    # Gerando a diferença entre o score e o score permutado
    importancia = (-score_permutado).add(score, axis=0)

    if criterio_performance == 'neg_log_loss':
        importancia /= -score_permutado
    else:
        importancia /= (1. - score_permutado)
    importancia = pd.concat({'mean': importancia.mean(),
                             'sd': importancia.std() / math.sqrt(importancia.shape[0])},
                            axis=1)
    return importancia.sort_values('mean', ascending=False)


def sfi(clf: any, features: pd.DataFrame, classificacoes: pd.Series, pesos: pd.Series,
        t1: pd.Series, n_divisoes: int, criterio_performance: str = 'neg_log_loss', pct_embargo: float = 0.01):
    """
    SFI é um método OOS. Ele vai calcular a importância de uma única feature, por isso, não sofre de efeitos
    substitutos.

    Observações:
    1) Pode considerar que todas as features não são importantes devido a avaliação ser CV OOS.
    2) Não considera a importância condicional a outras features (importância combinada).

    """

    importancia = pd.DataFrame(columns=['mean', 'sd'], dtype='float64')
    for nome in features.columns:
        df0 = validacao_cruzada_score(clf=clf, x=features[[nome]], y=classificacoes, weights=pesos,
                                      t1=t1, metrica=criterio_performance, n_divisoes=n_divisoes,
                                      pct_embargo=pct_embargo)
        importancia.loc[nome, 'mean'] = df0.mean()
        importancia.loc[nome, 'sd'] = df0.std() / math.sqrt(df0.shape[0])
    if criterio_performance == 'neg_log_loss':
        importancia['mean'] = -importancia['mean']
        return importancia.sort_values('mean', ascending=True)
    return importancia.sort_values('mean', ascending=False)
