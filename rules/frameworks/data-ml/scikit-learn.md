# scikit-learn

## Leakage - the discipline the whole API exists to enforce

1. **Fit on train, transform on test - never fit on everything.** Any preprocessor (scaler, imputer, encoder, selector) fitted on data that includes test rows has leaked; your metrics are fiction. This is the most common and most expensive sklearn mistake.
2. **Pipelines make leakage structurally impossible - use them always:** `Pipeline([('prep', ...), ('model', ...)])` with `ColumnTransformer` for mixed types. Cross-validation and grid search over the *pipeline* re-fits preprocessing per fold correctly; hand-preprocessed-then-CV'd data does not.
3. **Split before you look:** `train_test_split` (stratified for classification: `stratify=y`) before any fitting, imputation, or target-informed exploration. Time series split by time (`TimeSeriesSplit`) - random splits on temporal data leak the future.
4. **The target never informs features computed on the full dataset** - target encoding, feature selection by correlation with y, oversampling (SMOTE) all happen inside the CV loop / pipeline (imblearn's Pipeline for samplers), never before the split.

## Evaluation honesty

5. **Accuracy is the wrong default:** report metrics matched to the problem - precision/recall/F1 (with the positive class stated), ROC-AUC vs PR-AUC (PR for imbalanced), MAE/RMSE with units, calibration when probabilities matter. `classification_report` + confusion matrix before claiming success.
6. **Cross-validate; a single split is an anecdote:** `cross_val_score`/`cross_validate` with appropriate CV (stratified k-fold default for classification; grouped `GroupKFold` when rows share an entity - user, patient, session - or you're leaking identity across folds).
7. **Baseline first:** `DummyClassifier`/`DummyRegressor` (and a simple linear model) set the floor - a fancy model that doesn't beat the dummy is noise. Report the baseline alongside.
8. **Tune on validation, report on untouched test:** `GridSearchCV`/`RandomizedSearchCV`/`HalvingGridSearchCV` inside the training data; the held-out test set is spent exactly once, at the end. Tuning against test is leakage with extra steps.

## Mechanics

9. **`random_state` set everywhere it exists** (splits, models, CV) - for reproducibility, and vary it to check you're not reporting seed luck.
10. **Know your model's preprocessing needs:** scaling matters for SVM/KNN/linear-with-regularization/NN, not for trees; one-hot vs ordinal encoding chosen by whether categories order; `handle_unknown='ignore'` on encoders that will meet new categories in production.
11. **`predict_proba` vs `decision_function` vs `predict`:** thresholding is a business decision - don't accept 0.5 by default when costs are asymmetric; tune the threshold on validation data.
12. **Persist pipelines, version everything:** `joblib.dump` the whole fitted pipeline (never just the model - preprocessing is part of the artifact); pin sklearn version alongside (pickles don't survive major version jumps); loading untrusted pickles is code execution.
13. **`n_jobs=-1` for parallel CV/search where the machine allows; `set_config(transform_output="pandas")` when column names must survive** - feature-name mismatches at predict time are a real production failure; keep the schema contract explicit.
