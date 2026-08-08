import os
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

TOTAL_WARGA_DICT = {
    'saguling': 37987, 'gununghalu': 84529, 'sindangkerta': 80814,
    'rongga': 65316, 'cipongkor': 109952, 'cililin': 104811,
    'cihampelas': 149178, 'batujajar': 118155, 'padalarang': 194806,
    'cipatat': 153339, 'ngamprah': 185000, 'cipeundeuy': 94127,
    'cikalongwetan': 137226, 'cisarua': 85458, 'parongpong': 118593,
    'lembang': 211159,
}

def clean_name(s):
    if not s: return ''
    return str(s).lower().replace('_', '').replace(' ', '').replace('kecamatan', '').replace('kec.', '').strip()

def get_ml_clustered_data(app_root_path):
    excel_path = os.path.join(app_root_path, 'data', 'Data_Potensi_Penduduk_Terpapar_Tanah_Longsor.xlsx')
    if not os.path.exists(excel_path):
        return pd.DataFrame()

    df_raw = pd.read_excel(excel_path)
    df_raw.columns = df_raw.columns.str.strip().str.lower()
    
    records = []
    for _, row in df_raw.iterrows():
        kec_name = str(row.get('kecamatan', '')).strip()
        if not kec_name or kec_name == 'nan': continue
        
        key_clean = clean_name(kec_name)
        total_warga = TOTAL_WARGA_DICT.get(key_clean, 0)
        if total_warga == 0: continue

        teredukasi = int(row.get('teredukasi', 0))
        rentan_bl = int(row.get('rentan_balita_lansia', 0))
        rentan_dis = int(row.get('rentan_disabilitas', 0))
        rentan_bumil = int(row.get('rentan_ibu_hamil', 0))

        records.append({
            'Kecamatan': kec_name.capitalize(),
            'Total_Warga': total_warga,
            'Warga_Teredukasi': teredukasi,
            'Persen_Edukasi': round((teredukasi / total_warga) * 100, 2),
            'Rentan_Balita_Lansia': rentan_bl,
            'Rentan_Disabilitas': rentan_dis,
            'Rentan_Ibu_Hamil': rentan_bumil,
            'Kelas_Risiko': str(row.get('kelas_risiko', 'Sedang')).strip(),
            'Rasio_BL': (rentan_bl / total_warga) * 100,
            'Rasio_Dis': (rentan_dis / total_warga) * 100,
            'Rasio_Bumil': (rentan_bumil / total_warga) * 100
        })

    df = pd.DataFrame(records)
    if df.empty: return df

    # Jalankan K-Means Clustering
    features = ['Rasio_BL', 'Rasio_Dis', 'Rasio_Bumil', 'Persen_Edukasi']
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[features])

    kmeans = KMeans(n_clusters=3, random_state=42, n_init='auto')
    df['Cluster'] = kmeans.fit_predict(X_scaled)
    
    return df