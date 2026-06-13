import numpy as np, pandas as pd, time
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score

t0 = time.time()
DATA = "data/"
tr = pd.read_csv(DATA + "train.csv")
te = pd.read_csv(DATA + "test.csv")
target = "class"
cat_cols = ["spectral_type", "galaxy_population"]

def add_features(df):
    df = df.copy()
    # color indices — astronomically the strongest discriminators
    df["u_g"] = df["u"] - df["g"]
    df["g_r"] = df["g"] - df["r"]
    df["r_i"] = df["r"] - df["i"]
    df["i_z"] = df["i"] - df["z"]
    df["u_r"] = df["u"] - df["r"]
    df["g_i"] = df["g"] - df["i"]
    df["u_z"] = df["u"] - df["z"]
    return df

tr = add_features(tr); te = add_features(te)
for c in cat_cols:
    cats = pd.Categorical(pd.concat([tr[c], te[c]], axis=0)).categories
    tr[c] = pd.Categorical(tr[c], categories=cats).codes
    te[c] = pd.Categorical(te[c], categories=cats).codes

feat = [c for c in tr.columns if c not in ["id", target]]
X, y, Xte = tr[feat], tr[target], te[feat]
cat_mask = [c in cat_cols for c in feat]

def make_model():
    return HistGradientBoostingClassifier(
        max_iter=800, learning_rate=0.05, max_leaf_nodes=63,
        min_samples_leaf=40, l2_regularization=1.0,
        categorical_features=cat_mask, early_stopping=True,
        validation_fraction=0.1, n_iter_no_change=40, random_state=42)

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
accs, f1s = [], []
for i,(tri,vai) in enumerate(skf.split(X,y)):
    m = make_model(); m.fit(X.iloc[tri], y.iloc[tri])
    p = m.predict(X.iloc[vai])
    a = accuracy_score(y.iloc[vai],p); f = f1_score(y.iloc[vai],p,average="macro")
    accs.append(a); f1s.append(f)
    print(f"fold {i}: acc={a:.5f} macroF1={f:.5f}  ({time.time()-t0:.0f}s)")
print(f"CV acc    = {np.mean(accs):.5f} +/- {np.std(accs):.5f}")
print(f"CV macroF1= {np.mean(f1s):.5f} +/- {np.std(f1s):.5f}")

final = make_model(); final.fit(X,y)
pred = final.predict(Xte)
pd.DataFrame({"id":te["id"],"class":pred}).to_csv("submission_v2.csv", index=False)
print("saved submission_v2.csv")
print(f"done in {time.time()-t0:.0f}s")
