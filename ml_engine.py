import os
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def clean_name(s):
    if not s: return ''
    return str(s).lower().replace('_', '').replace(' ', '').replace('kecamatan', '').replace('kec.', '').replace('desa', '').strip()

def clean_number(val):
    if pd.isna(val) or val == '': return 0
    val_str = str(val).replace(' ', '').replace(',', '').replace('.', '')
    try:
        return int(val_str)
    except:
        return 0

def get_ml_clustered_data(app_root_path):
    excel_path = os.path.join(app_root_path, 'data', 'Data_Desa_Longsor.xlsx')
    if not os.path.exists(excel_path):
        print("⚠️ File Excel tidak ditemukan!")
        return pd.DataFrame()

    df_raw = pd.read_excel(excel_path)
    df_raw.columns = df_raw.columns.str.strip().str.lower()
    
    records = []
    for _, row in df_raw.iterrows():
        desa_name = str(row.get('desa', '')).strip()
        if not desa_name or desa_name == 'nan': continue
        
        total_warga = clean_number(row.get('jumlah_penduduk', 0))
        terpapar = clean_number(row.get('teredukasi', 0)) 
        rentan_bl = clean_number(row.get('umur_rentan', 0))
        rentan_miskin = clean_number(row.get('miskin', 0))
        rentan_dis = clean_number(row.get('disabilitas', 0))

        if total_warga <= 0: continue

        records.append({
            'Kecamatan': str(row.get('kecamatan', '')).capitalize(),
            'Desa': desa_name.title(),
            'Warga_Terpapar_Desa': terpapar,
            'Total_Warga_Desa': total_warga,
            'Rentan_BL_Desa': rentan_bl,
            'Rentan_Miskin_Desa': rentan_miskin,
            'Rentan_Disabilitas_Desa': rentan_dis,
            'Rasio_BL': (rentan_bl / total_warga) * 100 if total_warga > 0 else 0,
        })

    df = pd.DataFrame(records)
    if df.empty: return df

    # --- MENGHITUNG TOTAL KECAMATAN ---
    kecamatan_totals = df.groupby('Kecamatan')['Warga_Terpapar_Desa'].sum().reset_index()
    kecamatan_totals = kecamatan_totals.rename(columns={'Warga_Terpapar_Desa': 'Total_Terpapar_Kecamatan'})
    
    # Gabungkan kembali total kecamatan ke setiap baris desa
    df = df.merge(kecamatan_totals, on='Kecamatan', how='left')

    # Clustering (Opsional agar sistem ML tetap jalan)
    features = ['Total_Terpapar_Kecamatan', 'Rasio_BL']
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[features])
    kmeans = KMeans(n_clusters=3, random_state=42, n_init='auto')
    df['Cluster'] = kmeans.fit_predict(X_scaled)
    
    return df
