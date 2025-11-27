import os

import numpy as np
from textgrid import TextGrid

if __name__ == "__main__":
    path = r"D:\Corpus\Result\English dataset - Corpus level tuning"
    path_candidates = os.path.join(path, r"Praditor results")  # r"D:\Corpus\Project_Praditor\praditor - batch"
    path_answers = os.path.join(path, r"Human annotation")# r"D:\Corpus\Project_Praditor\anno2"

    print(path_candidates)
    print(path_answers)
    onset_diffs = []
    onset_candidates = []
    onset_answers = []

    onset_manual = []
    onset_praditor = []
    end = 1
    if end == 1:
        print("First-onset")
    else:
        print("All")

    for fname in [f for f in os.listdir(path_candidates) if f.endswith("TextGrid")]:
        fname_candidate = os.path.join(path_candidates, fname)
        tg = TextGrid()
        tg.read(fname_candidate)
        onsets = [tier for tier in tg.tiers if tier.name == "onset"][0]
        onset_candidates = [onset.time for onset in onsets]

        fname_answer = os.path.join(path_answers, fname)
        tg = TextGrid()
        try:
            tg.read(fname_answer)
        except FileNotFoundError:
            continue
        onsets = [tier for tier in tg.tiers if tier.name == "onset"][0]
        if end == 1:
            onset_answers = [onset.time for onset in onsets][:1]  # 选第一个！！！！！！
        else:
            onset_answers = [onset.time for onset in onsets]
        # print([onset.time for onset in onsets], [onset.time for onset in onsets][:1])
        # onset_manual.extend([min([onset_answer - onset_candidate for onset_candidate in onset_candidates], key=abs) for onset_answer in onset_answers])

        for onset_answer in onset_answers:
            if np.isnan(onset_answer):
                continue
                # print(onset_answer)
            onset_manual.append(onset_answer)  # 加入答案←和对应答案最近的onset↓
            onset_praditor.append(onset_candidates[np.argmin([abs(onset_answer - onset_candidate) for onset_candidate in onset_candidates])])


        onset_diffs.extend([min([onset_answer - onset_candidate for onset_candidate in onset_candidates], key=abs) for onset_answer in onset_answers])
    # print(onset_manual)
    # print(onset_praditor)
    for t in [25, 20, 15, 10, 5, 1]:
        t_datas = [i for i in onset_diffs if abs(i) < t/1000]
        print(f"< {t:2d} ms")

    print()
    print(
        f"| File Number: {len([f for f in os.listdir(path_candidates) if f.endswith('TextGrid')])} | "
        f"Total Number: {len(onset_diffs)} | \n"
        "----------------------\n"
    )
    for t in [25, 20, 15, 10, 5, 1]:
        t_datas = [i for i in onset_diffs if abs(i) < t/1000]
        print(f"{len(t_datas)/len(onset_diffs):.3f} ({np.std(t_datas)*1000:.3f})")

    print()

    X = np.array(onset_manual).reshape(-1, 1)
    y = np.array(onset_praditor)
    # print(X)
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

    print(len(X))
    print(len(y))

    import statsmodels.api as sm

    # 为自变量添加常数项
    X_sm = sm.add_constant(X)

    # 使用 statsmodels 进行线性回归分析
    model = sm.OLS(y, X_sm).fit()  # 拟合模型

    # 提取回归系数、标准误差、自由度、t统计量和 p 值

    print(model.summary())






