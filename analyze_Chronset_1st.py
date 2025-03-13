import os

import numpy as np
from textgrid import TextGrid


def tab_separated_to_dict(file_path):
    with open(file_path, 'r') as file:

        lines = [line.split("\t") for line in file.read().strip().split("\n")]
    dicts_list = dict(zip(
        [os.path.splitext(line[0])[0] for line in lines],
        [int(line[1])/1000 if line[1] != "NaN" else "NaN" for line in lines]

    ))

    return dicts_list


if __name__ == "__main__":

    path = r"D:\Corpus\Result\English dataset - Corpus level tuning"
    file_path = os.path.join(path, r"Chronset results")  # r"D:\Corpus\Project_Praditor\praditor - batch"
    path_answers = os.path.join(path, r"Human annotation")# r"D:\Corpus\Project_Praditor\anno2"



    onset_Chronset = {}
    for txt in os.listdir(file_path):
        if txt.endswith("txt"):
            onset_Chronset |= tab_separated_to_dict(os.path.join(file_path, txt))

    print(onset_Chronset)

    # path_answers = r"C:\Users\18357\PycharmProjects\RecPac_6\Chronset\Mandarin_answer"

    onset_answers = []

    onset_manual = {}

    for fname in [f for f in os.listdir(path_answers) if f.endswith("TextGrid")]:

        fname_answer = os.path.join(path_answers, fname)
        tg = TextGrid()
        tg.read(fname_answer)
        onsets = [tier for tier in tg.tiers if tier.name == "onset"][0]
        onset_answers = [onset.time for onset in onsets]

        onset_manual[os.path.splitext(fname)[0]] = onset_answers[0]

    onset_manual = dict(sorted(onset_manual.items()))
    onset_Chronset = dict(sorted(onset_Chronset.items()))

    # print(onset_manual)

    manuals = []
    Chronsets = []
    diffs = []
    count_answer_number = []

    for f in onset_manual:
        manual = onset_manual[f]
        try:
            Chronset = onset_Chronset[f]
        except KeyError:
            continue
        # print(manual, Chronset)
        if np.isnan(manual):
            continue
        count_answer_number.append(manual)
        try:
            diff = manual - Chronset
            diffs.append(diff)
            manuals.append(manual)
            Chronsets.append(Chronset)
        except:
            pass
    # onset_diffs = list(np.array(list(onset_manual.values())) - np.array(list(onset_Chronset.values())))
    print(f"Mean diff = {np.mean(np.array(diffs) * 1000)}, SE = {np.std(np.array(diffs) * 1000)}")

    for t in [25, 20, 15, 10, 5, 1]:
        t_datas = [i for i in diffs if abs(i) < t/1000]
        print(f"< {t:4d} ms")

    print(
        f"| File Number: {len(os.listdir(path_answers))} | "
        f"Detected Number: {len(diffs)} | "
        f"Should Find Number: {len(count_answer_number)}\n"
        "----------------------\n"
    )
    for t in [25, 20, 15, 10, 5, 1]:
        t_datas = [i for i in diffs if abs(i) < t/1000]
        print(f"{len(t_datas)/len(diffs):.3f} ({np.std(t_datas)*1000:.3f})")

    print()




    X = np.array(manuals).reshape(-1, 1)
    y = np.array(Chronsets).reshape(-1, 1)

    from sklearn.linear_model import LinearRegression

    # pipeline = Pipeline([
    #     #('scaler', StandardScaler()),  # 特征缩放
    #     ('linear_regression', LinearRegression())  # 线性回归模型
    # ])

    model = LinearRegression()
    # 训练模型
    model.fit(X, y)

    # 预测测试集
    y_pred = model.predict(X)

    # r2 = r2_score(X, y_pred)

    # print(f'\nR-squared: {r2:.10f}')

    # 计算残差
    residuals = y - y_pred
    # coefficients = model.coef_
    # intercept = model.intercept_


    for t in [25, 20, 15, 10, 5, 1]:
        t_datas = [i for i in residuals if abs(i) < t/1000]
        print(f"{len(t_datas)/len(residuals):.3f} ({np.std(t_datas)*1000:.3f})")

    X = 1000 * X
    y = 1000 * y

    import statsmodels.api as sm

    # 为自变量添加常数项
    X_sm = sm.add_constant(X)

    # 使用 statsmodels 进行线性回归分析
    model = sm.OLS(y, X_sm).fit()  # 拟合模型

    # 提取回归系数、标准误差、自由度、t统计量和 p 值

    print(model.summary())






