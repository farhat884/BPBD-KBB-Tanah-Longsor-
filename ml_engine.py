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
    # Menggunakan file Excel Kecamatan
    excel_path = os.path.join(app_root_path, 'data', 'Data_Potensi_Penduduk_Terpapar_Tanah_Longsor.xlsx')
    if not os.path.exists(excel_path):
        print("⚠️ File Excel tidak ditemukan!")
        return pd.DataFrame()

    df_raw = pd.read_excel(excel_path)
    
    records = []
    for _, row in df_raw.iterrows():
        kec_name = str(row.get('Kecamatan', '')).strip()
        if not kec_name or kec_name.lower() == 'nan': continue
        
        # 'Teredukasi' di data ini maksudnya adalah Warga Terpapar yang butuh edukasi
        terpapar = clean_number(row.get('Teredukasi', 0))
        rentan_bl = clean_number(row.get('Rentan_Balita_Lansia', 0))
        rentan_dis = clean_number(row.get('Rentan_Disabilitas', 0))
        rentan_ibu = clean_number(row.get('Rentan_Ibu_Hamil', 0))

        records.append({
            'Kecamatan': kec_name.title(),
            'Warga_Terpapar': terpapar,
            'Rentan_Balita_Lansia': rentan_bl,
            'Rentan_Disabilitas': rentan_dis,
            'Rentan_Ibu_Hamil': rentan_ibu,
            'Kelas_Risiko': str(row.get('Kelas_Risiko', 'Sedang')).title()
        })

    return pd.DataFrame(records)
    
    return df
