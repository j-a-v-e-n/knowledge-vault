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
drop = ["id", target]
feat = [c for c in tr.columns if c not in drop]

# encode categoricals as ordinal codes (consistent across train/test)
for c in cat_cols:
    cats = pd.Categorical(pd.concat([tr[c], te[c]], axis=0)).categories
    tr[c] = pd.Categorical(tr[c], categories=cats).codes
    te[c] = pd.Categorical(te[c], categories=cats).codes

X = tr[feat]
y = tr[target]
Xte = te[feat]
cat_mask = [c in cat_cols for c in feat]

def make_model():
    return HistGradientBoostingClassifier(
        max_iter=600, learning_rate=0.05, max_leaf_nodes=63,
        min_samples_leaf=50, l2_regularization=1.0,
        categorical_features=cat_mask, early_stopping=True,
        validation_fraction=0.1, n_iter_no_change=30, random_state=42,
    )

# 5-fold CV
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
accs, f1s = [], []
for i, (tri, vai) in enumerate(skf.split(X, y)):
    m = make_model()
    m.fit(X.iloc[tri], y.iloc[tri])
    p = m.predict(X.iloc[vai])
    a = accuracy_score(y.iloc[vai], p)
    f = f1_score(y.iloc[vai], p, average="macro")
    accs.append(a); f1s.append(f)
    print(f"fold {i}: acc={a:.5f} macroF1={f:.5f}  ({time.time()-t0:.0f}s)")

print(f"CV acc    = {np.mean(accs):.5f} +/- {np.std(accs):.5f}")
print(f"CV macroF1= {np.mean(f1s):.5f} +/- {np.std(f1s):.5f}")

# train on full data, predict test
final = make_model()
final.fit(X, y)
pred = final.predict(Xte)
sub = pd.DataFrame({"id": te["id"], "class": pred})
sub.to_csv("submission.csv", index=False)
print("saved submission.csv", sub.shape)
print(sub["class"].value_counts(normalize=True).round(4).to_dict())
print(f"done in {time.time()-t0:.0f}s")
