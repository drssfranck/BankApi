import pandas as pd
import json
import io
import requests

# ---- Paths ----
PATH_TRANSACTIONS = "https://oxymis-my.sharepoint.com/:x:/g/personal/i_mbe_stu-mba-esg_com/EVmfmPCgAaRDv8-3nGEVeEkBo7fliWtmHYwfcviA80c84g?e=AErORU&download=1"
PATH_CARDS        = "https://oxymis-my.sharepoint.com/:x:/g/personal/i_mbe_stu-mba-esg_com/Ec0Hsd7EE3lKiOA7nC8zQfsBF8NT5w7y9o48djAZc4tfAw?e=u7nocZ&download=1"
PATH_USERS        = "https://oxymis-my.sharepoint.com/:x:/g/personal/i_mbe_stu-mba-esg_com/EQI4TFk_tL1EgKyh1MJ-JGUB6rEjVmddSw-YxpMu-Kj7Xg?e=Rk2Ydj&download=1"
PATH_MCC          = "https://oxymis-my.sharepoint.com/:u:/g/personal/i_mbe_stu-mba-esg_com/ERLgfSNpHNNMiZahFGMrmr4BUo4RVP9M5tuIHrGCUV1oEg?e=b4WtpX&download=1"
PATH_LABELS       = "https://oxymis-my.sharepoint.com/:u:/g/personal/i_mbe_stu-mba-esg_com/EZByNXfujI1JsPfbAba5-BgBQXbIbjyiVJzD82nGbkmO8A?e=loVvY6&download=1"
OUTPUT_PATH       = "data.pkl"

def download_from_sharepoint(url):
    """
    Télécharge un fichier depuis SharePoint avec gestion des redirections
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, allow_redirects=True)
    response.raise_for_status()
    return response.content

# Lecture des fichiers
print("Chargement des datasets...")

print("Téléchargement de transactions...")
content = download_from_sharepoint(PATH_TRANSACTIONS)
df_trans = pd.read_csv(io.BytesIO(content))

print("Téléchargement de cards...")
content = download_from_sharepoint(PATH_CARDS)
df_cards = pd.read_csv(io.BytesIO(content))

print("Téléchargement de users...")
content = download_from_sharepoint(PATH_USERS)
df_users = pd.read_csv(io.BytesIO(content))

print("Téléchargement de MCC...")
content = download_from_sharepoint(PATH_MCC)
mcc_data = json.loads(content.decode('utf-8'))


df_mcc = pd.DataFrame(list(mcc_data.items()), columns=['mcc', 'mcc_description'])
df_mcc['mcc'] = df_mcc['mcc'].astype(int)

print("Téléchargement de labels...")
content = download_from_sharepoint(PATH_LABELS)
labels_data = json.loads(content.decode('utf-8'))

if 'root' in labels_data and 'target' in labels_data['root']:
    labels_dict = labels_data['root']['target']
    df_labels = pd.DataFrame(list(labels_dict.items()), columns=['id', 'is_fraud'])
    df_labels['id'] = df_labels['id'].astype(int)
else:
    df_labels = pd.DataFrame()

print("\n✅ Datasets chargés !")
print(f"  - Transactions: {len(df_trans):,} lignes, {len(df_trans.columns)} colonnes")
print(f"  - Cards: {len(df_cards):,} lignes, {len(df_cards.columns)} colonnes")
print(f"  - Users: {len(df_users):,} lignes, {len(df_users.columns)} colonnes")
print(f"  - MCC: {len(df_mcc):,} codes")
print(f"  - Labels: {len(df_labels):,} labels")

# ---- Fusions ----
print("\n🔄 Fusion des données...")

# Renommeage des colonnes 'id' avant fusion 
df_cards_renamed = df_cards.rename(columns={'id': 'card_id_pk'})
df_users_renamed = df_users.rename(columns={'id': 'user_id_pk', 'client_id': 'client_id_pk'})

# Fusion niveau 1 : transactions + cards
df_merged = df_trans.merge(
    df_cards_renamed, 
    left_on='card_id', 
    right_on='card_id_pk', 
    how="left"
)
print(f"  ✓ Après fusion cards: {len(df_merged):,} lignes")

# Fusion niveau 2 : + users
df_merged = df_merged.merge(
    df_users_renamed, 
    left_on='client_id', 
    right_on='client_id_pk', 
    how="left"
)
print(f"  ✓ Après fusion users: {len(df_merged):,} lignes")

# Fusion niveau 3 : + MCC descriptions
if not df_mcc.empty and 'mcc' in df_merged.columns:
    df_merged = df_merged.merge(df_mcc, on='mcc', how='left')
    print(f"  ✓ Après fusion MCC: {len(df_merged):,} lignes")

# Fusion niveau 4 : + fraud labels
if not df_labels.empty and 'id' in df_merged.columns:
    df_merged = df_merged.merge(df_labels, on='id', how='left')
    print(f"  ✓ Après fusion labels: {len(df_merged):,} lignes")

# Suppresson des colonnes dupliquées inutiles
columns_to_drop = ['card_id_pk', 'user_id_pk', 'client_id_pk']
df_merged = df_merged.drop(columns=[col for col in columns_to_drop if col in df_merged.columns])

# Sauvegarde
df_merged.to_pickle(OUTPUT_PATH)

print("\nFusion terminée avec succès !")
print(f"Fichier généré : {OUTPUT_PATH}")
print(f"Nombre de lignes : {len(df_merged):,}")
print(f"Nombre de colonnes : {len(df_merged.columns)}")

print(f"\n Colonnes finales ({len(df_merged.columns)}) :")
for i, col in enumerate(df_merged.columns, 1):
    print(f"  {i:2d}. {col}")

# Statistiques sur les fraudes
if 'is_fraud' in df_merged.columns:
    fraud_counts = df_merged['is_fraud'].value_counts()
    print(f"\n Statistiques de fraude :")
    for label, count in fraud_counts.items():
        percentage = (count / len(df_merged)) * 100
        print(f"  - {label}: {count:,} ({percentage:.2f}%)")

# Vérifier les valeurs manquantes importantes
print(f"\n  Principales valeurs manquantes :")
missing = df_merged.isnull().sum()
missing = missing[missing > 0].sort_values(ascending=False).head(10)
if len(missing) > 0:
    for col, count in missing.items():
        percentage = (count / len(df_merged)) * 100
        print(f"  - {col}: {count:,} ({percentage:.1f}%)")
else:
    print("  Aucune valeur manquante ! 🎉")

print(f"\n Aperçu des 3 premières lignes :")
print(df_merged.head(3).to_string())