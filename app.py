import json
import os
from dotenv import load_dotenv
load_dotenv()
import folium
import requests
from flask import Flask, render_template, request, jsonify
from ml_engine import get_ml_clustered_data, clean_name

app = Flask(__name__)

# =========================================================
# 1. LOAD DATA DARI MESIN (ML_ENGINE)
# =========================================================
df_data = get_ml_clustered_data(app.root_path)

data_dict = {}
if not df_data.empty:
    # Menggunakan nama Desa sebagai key dari dictionary
    data_dict = {
        clean_name(row['Desa']): row for row in df_data.to_dict('records')
    }
    print(f"🔍 DEBUG: Desa yang siap di-mapping: {list(data_dict.keys())[:10]}...")
else:
    print("⚠️ DEBUG: Data dictionary kosong! Periksa file ml_engine.py dan dataset Excel.")

# =========================================================
# 2. BACA GEOJSON LOKAL
# =========================================================
def load_local_geojson_files():
    folder_path = os.path.join(app.root_path, 'static', 'id3217_bandung_barat')
    if not os.path.exists(folder_path):
        folder_path = app.root_path

    features = []
    main_file = os.path.join(folder_path, 'id3217_bandung_barat.geojson')
    
    if os.path.exists(main_file):
        try:
            with open(main_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get('type') == 'FeatureCollection' and len(data.get('features', [])) > 0:
                    return data
        except Exception as e:
            print(f'Error reading main GeoJSON: {e}')

    for filename in os.listdir(folder_path):
        if filename.endswith(('.geojson', '.json')):
            if filename in ['id3217_bandung_barat.geojson', 'id3217888_waduk.geojson']:
                continue
            filepath = os.path.join(folder_path, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('type') == 'FeatureCollection':
                        for feat in data['features']:
                            features.append(feat)
                    elif data.get('type') == 'Feature':
                        features.append(data)
            except Exception as e:
                print(f'Gagal membaca {filename}: {e}')

    return {'type': 'FeatureCollection', 'features': features}

def get_nama_kecamatan(properties):
    for key in ['district', 'nama_kec_file', 'WADMKC', 'NAMOBJ', 'nama_kecamatan', 'waerkd']:
        if key in properties and properties[key]:
            return str(properties[key])
    return ''

def get_nama_desa(properties):
    # Ekstraksi nama desa dari properties GeoJSON
    for key in ['village', 'nama_desa', 'desa', 'NAMOBJ']:
        if key in properties and properties[key]:
            return str(properties[key])
    return ''

# =========================================================
# 3. GENERATE PETA FOLIUM
# =========================================================
def get_legend_html():
    return """
    <div style="
        position: fixed; 
        bottom: 30px; left: 30px; width: 260px; 
        background-color: white; z-index:9999; font-size:12px; font-family: sans-serif;
        border:2px solid #ccc; border-radius: 8px; padding: 12px; box-shadow: 2px 2px 8px rgba(0,0,0,0.2);">
        <b style="font-size: 13px;">Prioritas Edukasi Bencana</b><br>
        <span style="font-size: 11px; color: #555;">Berdasarkan persentase warga teredukasi</span>
        <hr style="margin: 6px 0;">
        <i style="background: #d7191c; width: 14px; height: 14px; float: left; margin-right: 10px;"></i> <b>Prioritas Tinggi</b> (&lt; 25% Teredukasi)<br>
        <div style="clear:both; margin-top: 4px;"></div>
        <i style="background: #fdae61; width: 14px; height: 14px; float: left; margin-right: 10px;"></i> <b>Prioritas Sedang</b> (25% - 49.9%)<br>
        <div style="clear:both; margin-top: 4px;"></div>
        <i style="background: #2b83ba; width: 14px; height: 14px; float: left; margin-right: 10px;"></i> <b>Prioritas Rendah</b> (&ge; 50% Teredukasi)<br>
    </div>
    """

def generate_map():
    m = folium.Map(location=[-6.8452, 107.5023], zoom_start=11, tiles='OpenStreetMap')
    geojson_data = load_local_geojson_files()

    def style_function(feature):
        raw_name = get_nama_desa(feature['properties'])
        key_clean = clean_name(raw_name)
        fill_color = '#cccccc' # Default abu-abu

        if key_clean in data_dict:
            pct = data_dict[key_clean]['Persen_Edukasi']
            if pct >= 50.0:
                fill_color = '#2b83ba'  # Biru
            elif pct >= 25.0:
                fill_color = '#fdae61'  # Oranye
            else:
                fill_color = '#d7191c'  # Merah
        
        return {
            'fillColor': fill_color, 
            'color': '#111111', 
            'weight': 1.0, 
            'fillOpacity': 0.75,
            'className': f'desa-item desa-{key_clean}'
        }

    def highlight_function(feature):
        return {'weight': 2.5, 'color': '#000000', 'fillOpacity': 0.9}

    for feature in geojson_data['features']:
        raw_name = get_nama_desa(feature['properties'])
        key_clean = clean_name(raw_name)

        if key_clean == 'waduk':
            continue

        if key_clean in data_dict:
            d = data_dict[key_clean]
            
            pct = d['Persen_Edukasi']
            if pct >= 50.0:
                teks_prioritas = "<span style='color:#2b83ba; font-weight:bold;'>RENDAH (Aman)</span>"
            elif pct >= 25.0:
                teks_prioritas = "<span style='color:#e67e22; font-weight:bold;'>SEDANG</span>"
            else:
                teks_prioritas = "<span style='color:#d7191c; font-weight:bold;'>TINGGI (Butuh Segera)</span>"

            popup_html = f"""
            <div style="font-family: Arial, sans-serif; min-width: 210px; font-size:12px;">
                <h4 style="margin:0 0 6px 0; color:#2c3e50;">Desa {d['Desa']}</h4>
                <b>Kecamatan:</b> {d['Kecamatan']}<br>
                <b>Total Penduduk:</b> {d['Total_Warga']:,} jiwa<br>
                <b>Warga Teredukasi:</b> {d['Warga_Teredukasi']:,} jiwa (<b>{d['Persen_Edukasi']}%</b>)<br>
                <hr style="margin:6px 0;">
                <b>Prioritas Penyuluhan:</b> {teks_prioritas}
                <hr style="margin:6px 0;">
                <b>Kelompok Rentan:</b><br>
                • Umur Rentan: {d['Rentan_Balita_Lansia']:,} jiwa<br>
                • Miskin: {d['Rentan_Miskin']:,} jiwa<br>
                • Disabilitas: {d['Rentan_Disabilitas']:,} jiwa<br>
                <b>Jumlah Rentan:</b> {d['Rentan_Balita_Lansia'] + d['Rentan_Miskin'] + d['Rentan_Disabilitas']:,} jiwa<br>
                <b>Kelas Risiko BPBD:</b> {d['Kelas_Risiko']}
            </div>
            """
            tooltip_text = f"Desa {d['Desa']} (Kec. {d['Kecamatan']})"
        else:
            popup_html = f'<b>Desa: {raw_name.capitalize()}</b><br>Data belum dimasukkan.'
            tooltip_text = f'Desa {raw_name.capitalize()}'

        geo_obj = folium.GeoJson(
            feature,
            style_function=style_function,
            highlight_function=highlight_function,
            tooltip=tooltip_text,
            popup=folium.Popup(popup_html, max_width=320),
        )
        
        if key_clean:
            geo_obj.add_child(folium.features.GeoJsonTooltip(fields=[], labels=False))
            geo_obj.options['className'] = f'desa-item desa-{key_clean}'
            
        geo_obj.add_to(m)

    m.get_root().html.add_child(folium.Element(get_legend_html()))
    return m._repr_html_()

# =========================================================
# 4. ROUTING WEB & API CHATBOT
# =========================================================
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/kondisi')
def kondisi():
    peta_html = generate_map()
    return render_template('kondisi.html', peta_html=peta_html, data_dict=data_dict)

@app.route('/edukasi')
def edukasi():
    return render_template('edukasi.html')

@app.route('/cuaca')
def cuaca():
    return render_template('cuaca.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message')
    
    ringkasan_data = []
    if not df_data.empty:
        for _, row in df_data.iterrows():
            cluster = row.get('Cluster', -1)
            prioritas = "Tinggi" if cluster == 0 else ("Sedang" if cluster == 2 else "Rendah")
            ringkasan_data.append(f"- Desa {row['Desa']} (Kec. {row['Kecamatan']}): Prioritas {prioritas}")
    
    konteks_ml = str(data_dict)
    
    system_prompt = f"""
Kamu adalah Asisten Virtual BPBD (Badan Penanggulangan Bencana Daerah) Kabupaten Bandung Barat (KBB).
Tugasmu adalah membantu pengguna menganalisis data spasial terkait risiko dan mitigasi bencana longsor.
Gunakan bahasa Indonesia yang profesional, sopan, namun tetap mudah dipahami (informatif).
Jika ditanya siapa kamu, jawablah bahwa kamu adalah Chatbot AI dari BPBD KBB.

PENTING: Berikut adalah SATU-SATUNYA data clustering machine learning yang valid dan boleh kamu analisis:
{konteks_ml}

ATURAN MENJAWAB:
1. DILARANG KERAS mengarang nama daerah, kondisi geologi, infrastruktur, atau persentase angka. HANYA gunakan nama Desa/Kecamatan dan angka yang persis tertera pada data di atas!
2. Jika pengguna bertanya daerah prioritas, saring dan sebutkan hanya Desa yang berstatus "Prioritas Tinggi".
3. Wajib gunakan format Bullet Points (-) atau penomoran.
4. Gunakan huruf tebal (**teks**) untuk menegaskan nama Desa.
5. BULATKAN semua angka desimal menjadi maksimal 2 angka di belakang koma (contoh: 23.99).
6. Jawab maksimal 3 paragraf, singkat, padat, dan langsung ke intinya.
7. Jika data di atas ternyata kosong/blank, JANGAN MENGARANG JAWABAN.
8. KHUSUS PENCEGAHAN/EVAKUASI: Jika pengguna bertanya tentang cara pencegahan, evakuasi, atau apa yang harus dilakukan saat longsor, berikan 1-2 tips singkat, lalu ARAHKAN mereka untuk membaca pedoman lengkap dengan kalimat seperti: "Untuk panduan lebih lengkap, silakan kunjungi menu **Panduan Keselamatan** atau akses halaman /edukasi".
"""

    api_key = os.environ.get("GROQ_API_KEY") 
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        res_json = response.json()
        
        if 'error' in res_json:
            pesan_error = res_json['error'].get('message', 'Error tidak diketahui dari server')
            return jsonify({"reply": f"[DIAGNOSTIK SISTEM] Akses API ditolak oleh Groq. Alasan: {pesan_error}"})
            
        ai_reply = res_json['choices'][0]['message']['content']
        return jsonify({"reply": ai_reply})
        
    except Exception as e:
        return jsonify({"reply": f"[DIAGNOSTIK SISTEM] Kerusakan pada modul pemrosesan: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
