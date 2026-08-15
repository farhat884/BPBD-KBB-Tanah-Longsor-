import os
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def clean_name(s):
    if not s: return ''
    return str(s).lower().replace('_', '').replace(' ', '').replace('kecamatan', '').replace('kec.', '').replace('desa', '').strip()

# Fungsi khusus untuk membersihkan angka dari titik, koma, huruf, dan spasi
def clean_number(val):
    if pd.isna(val) or val == '': return 0
    # Ubah ke string, hapus spasi, hapus koma, hapus titik
    val_str = str(val).replace(' ', '').replace(',', '').replace('.', '')
    try:
        return int(val_str)
    except:
        return 0

def get_ml_clustered_data(app_root_path):
    excel_path = os.path.join(app_root_path, 'data', 'Data_Desa_Longsor.xlsx')
    if not os.path.exists(excel_path):
        print("⚠️ File Excel Data_Desa_Longsor.xlsx tidak ditemukan!")
        return pd.DataFrame()

    df_raw = pd.read_excel(excel_path)
    df_raw.columns = df_raw.columns.str.strip().str.lower()
    
    records = []
    for _, row in df_raw.iterrows():
        desa_name = str(row.get('desa', '')).strip()
        if not desa_name or desa_name == 'nan': continue
        
        # Bersihkan format angka dengan fungsi baru yang lebih kebal
        total_warga = clean_number(row.get('jumlah_penduduk', 0))
            
        if total_warga <= 0: 
            print(f"⚠️ Melewati Desa {desa_name} karena jumlah penduduk 0 atau format angka salah.")
            continue

        teredukasi = clean_number(row.get('teredukasi', 0)) if 'teredukasi' in row else 0
        rentan_bl = clean_number(row.get('umur_rentan', 0))
        rentan_miskin = clean_number(row.get('miskin', 0))
        rentan_dis = clean_number(row.get('disabilitas', 0))

        records.append({
            'Kecamatan': str(row.get('kecamatan', '')).capitalize(),
            'Desa': desa_name.title(),
            'Total_Warga': total_warga,
            'Warga_Teredukasi': teredukasi,
            'Persen_Edukasi': round((teredukasi / total_warga) * 100, 2) if total_warga > 0 else 0,
            'Rentan_Balita_Lansia': rentan_bl,
            'Rentan_Miskin': rentan_miskin,
            'Rentan_Disabilitas': rentan_dis,
            'Kelas_Risiko': 'Tinggi' if total_warga > 5000 else 'Sedang', 
            'Rasio_BL': (rentan_bl / total_warga) * 100,
            'Rasio_Miskin': (rentan_miskin / total_warga) * 100,
            'Rasio_Dis': (rentan_dis / total_warga) * 100
        })

    df = pd.DataFrame(records)
    if df.empty: 
        print("⚠️ DataFrame kosong! Tidak ada data yang berhasil diproses.")
        return df

    # K-Means Clustering
    features = ['Rasio_BL', 'Rasio_Miskin', 'Rasio_Dis', 'Persen_Edukasi']
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[features])

    kmeans = KMeans(n_clusters=3, random_state=42, n_init='auto')
    df['Cluster'] = kmeans.fit_predict(X_scaled)
    
    return df
