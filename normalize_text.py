import pandas as pd

# 1. Carregar o dataset original
df_original = pd.read_csv('dataset_hypertns.csv')

# 2. Fazer uma cópia para transformar (mantendo o original intacto na variável df_original)
df = df_original.copy()

# 3. Limpar espaços extras nos nomes das colunas
df.columns = df.columns.str.strip()

# 4. Mapear variáveis binárias (Yes/No) e Hypertension (High/Low)
bin_map = {'Yes': 1, 'No': 0}
df['Family_History'] = df['Family_History'].map(bin_map)
df['Diabetes']       = df['Diabetes'].map(bin_map)
df['Hypertension']   = df['Hypertension'].map({'High': 1, 'Low': 0})

# 5. Mapear Gender
df['Gender'] = df['Gender'].map({'Female': 0, 'Male': 1})

# 6. Codificação ordinal para Education_Level
edu_map = {'Primary': 1, 'Secondary': 2, 'Tertiary': 3}
df['Education_Level'] = df['Education_Level'].map(edu_map)

# 7. Remover espaços extras em colunas categóricas restantes
for col in ['Employment_Status', 'Smoking_Status', 'Physical_Activity_Level']:
    df[col] = df[col].str.strip()

# 8. One-hot encoding com dtype=int para Employment_Status, Smoking_Status e Physical_Activity_Level
df = pd.get_dummies(
    df,
    columns=['Employment_Status', 'Smoking_Status', 'Physical_Activity_Level'],
    drop_first=True,
    dtype=int
)

# 9. Converter colunas booleanas que eventualmente existam em 0/1
bool_cols = df.select_dtypes(include='bool').columns
df[bool_cols] = df[bool_cols].astype(int)

# 10. Salvar o dataset transformado completo em um novo CSV
df.to_csv('hypertension_dataset_transformed.csv', index=False)

# 11. (Opcional) Exibir as primeiras linhas para conferência
print(df.head())
