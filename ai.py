import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Dropout

# 1. Carregar o dataset
df = pd.read_csv("dataset_hypertns.csv")  # ajuste o caminho/nome do CSV conforme necessário

# 2. Separar features (X) e target (y)
#    A coluna 'Hypertension' será o alvo (0 ou 1)
y = df["Hypertension"].values
X = df.drop(columns=["Hypertension"])

# 3. Identificar colunas contínuas e colunas binárias/categóricas
colunas_continuas = [
    "Age", "BMI", "Cholesterol", "Systolic_BP", "Diastolic_BP",
    "Alcohol_Intake", "Stress_Level", "Salt_Intake",
    "Sleep_Duration", "Heart_Rate", "LDL", "HDL",
    "Triglycerides", "Glucose"
]
# As demais colunas já são 0/1 ou categorias numéricas discretas:
# Family_History, Diabetes, Gender, Education_Level,
# Employment_Status_Retired, Employment_Status_Unemployed,
# Smoking_Status_Former, Smoking_Status_Never,
# Physical_Activity_Level_Low, Physical_Activity_Level_Moderate
colunas_binarias = [
    "Family_History", "Diabetes", "Gender", "Education_Level",
    "Employment_Status_Retired", "Employment_Status_Unemployed",
    "Smoking_Status_Former", "Smoking_Status_Never",
    "Physical_Activity_Level_Low", "Physical_Activity_Level_Moderate"
]

# 4. Escalonar (StandardScaler) apenas as contíguas
scaler = StandardScaler()
X_continuas = scaler.fit_transform(X[colunas_continuas])
X_binarias = X[colunas_binarias].values  # já no formato numpy

# 5. Concatenar de volta para formar a matriz final de features
X_pre = np.hstack([X_continuas, X_binarias])

# 6. Dividir em treino e teste (80% treino / 20% teste)
X_train, X_test, y_train, y_test = train_test_split(
    X_pre, y, test_size=0.2, stratify=y, random_state=42
)

# 7. Definir arquitetura da rede neural
input_dim = X_train.shape[1]
model = Sequential([
    Dense(64, activation="relu", input_shape=(input_dim,)),
    Dropout(0.3),
    Dense(32, activation="relu"),
    Dropout(0.2),
    Dense(1, activation="sigmoid")  # saída binária
])

# 8. Compilar o modelo
model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

# 9. Treinamento
history = model.fit(
    X_train, y_train,
    validation_split=0.1,  # dentro do conjunto de treino, 10% para validação
    epochs=5,
    batch_size=32,
    verbose=1
)

# 10. Avaliar no conjunto de teste
loss_test, acc_test = model.evaluate(X_test, y_test, verbose=0)
print(f"Loss no teste: {loss_test:.4f}")
print(f"Acurácia no teste: {acc_test:.4f}")

# 11. Se quiser prever em novos exemplos:
#    X_novo deve seguir o mesmo preprocessamento (escalonamento + concatenação)
#    prob_pred = model.predict(X_novo)
#    y_pred = (prob_pred >= 0.5).astype(int)
