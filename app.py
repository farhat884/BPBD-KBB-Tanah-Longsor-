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
# 1. LOAD DATA
# =========================================================
df_data = get_ml_clustered_data(app.root_path)

data_dict = {}
if not df_data.empty:
    data_dict = {
        clean_name(row['Desa']): row for row in df_data.to_dict('records')
    }
    print(f"🔍 DEBUG: Desa yang siap di-mapping: {list(data_dict.keys())[:10]}...")

# =========================================================
# 2. BACA GEOJSON
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
            pass

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
                pass

    return {'type': 'FeatureCollection', 'features': features}

def get_nama_desa(properties):
    for key in ['village', 'nama_desa', 'desa', 'NAMOBJ']:
        if key in properties and properties[key]:
            return str(properties[key])
    return ''

# =========================================================
# 3. GENERATE PETA
# =========================================================
def get_legend_html():
    return """
    <div style="
        position: fixed; 
        bottom: 30px; left: 30px; width: 260px; 
        background-color: white; z-index:9999; font-size:12px; font-family: sans-serif;
        border:2px solid #ccc; border-radius: 8px; padding: 12px; box-shadow: 2px 2px 8px rgba(0,0,0,0.2);">
        <b style="font-size: 13px;">Status Kerawanan Kecamatan</b><br>
        <span style="font-size: 11px; color: #555;">Total Warga Butuh Edukasi</span>
        <hr style="margin: 6px 0;">
        <i style="background: #d7191c; width: 14px; height: 14px; float: left; margin-right: 10px;"></i> <b>Darurat Tinggi</b> (&ge; 40,000 jiwa)<br>
        <div style="clear:both; margin-top: 4px;"></div>
        <i style="background: #fdae61; width: 14px; height: 14px; float: left; margin-right: 10px;"></i> <b>Siaga Sedang</b> (20,000 - 39,999 jiwa)<br>
        <div style="clear:both; margin-top: 4px;"></div>
        <i style="background: #2b83ba; width: 14px; height: 14px; float: left; margin-right: 10px;"></i> <b>Aman / Rendah</b> (&lt; 20,000 jiwa)<br>
    </div>
    """

def generate_map():
    m = folium.Map(location=[-6.8452, 107.5023], zoom_start=11, tiles='OpenStreetMap')
    geojson_data = load_local_geojson_files()

    def style_function(feature):
        raw_name = get_nama_desa(feature['properties']) 
        key_clean = clean_name(raw_name)
        fill_color = '#cccccc' 

        if key_clean in data_dict:
            # WARNA DITENTUKAN OLEH TOTAL KECAMATAN
            terpapar_kecamatan = data_dict[key_clean]['Total_Terpapar_Kecamatan']
            
            if terpapar_kecamatan >= 40000: fill_color = '#d7191c'
            elif terpapar_kecamatan >= 20000: fill_color = '#fdae61'
            else: fill_color = '#2b83ba'
        
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
            
            # --- POP-UP DETAIL DESA SAAT DIKLIK ---
            popup_html = f"""
            <div style="font-family: Arial, sans-serif; min-width: 250px; font-size:12px;">
                <div style="background-color: #d35400; color: white; padding: 8px; border-radius: 4px 4px 0 0; text-align: center;">
                    <h3 style="margin:0; font-size: 15px; letter-spacing: 1px;">KEC. {d['Kecamatan'].upper()}</h3>
                    <span style="font-size: 11px;">Total Terpapar Kecamatan: <b>{d['Total_Terpapar_Kecamatan']:,}</b> jiwa</span>
                </div>
                <div style="padding: 10px; border: 1px solid #ccc; border-top: none; border-radius: 0 0 4px 4px; background-color: #f8f9fa;">
                    <div style="text-align: center; margin-bottom: 8px;">
                        <span style="font-size: 11px; color: #555;">KONDISI LOKAL WILAYAH INI:</span><br>
                        <b style="font-size: 14px; color: #2c3e50;">DESA {d['Desa'].upper()}</b>
                    </div>
                    <div style="background-color: white; border: 1px solid #e0e0e0; padding: 8px; border-radius: 4px; text-align: center;">
                        <b style="font-size: 11px; color: #7f8c8d;">WARGA TERPAPAR (DESA)</b><br>
                        <span style="font-size: 20px; color: #c0392b; font-weight: bold;">{d['Warga_Terpapar_Desa']:,}</span> <span style="font-size:11px;">jiwa</span>
                    </div>
                    <table style="width: 100%; font-size: 11px; margin-top: 10px; color: #34495e;">
                        <tr>
                            <td>Total Penduduk Desa</td>
                            <td style="text-align: right;"><b>{d['Total_Warga_Desa']:,}</b> jiwa</td>
                        </tr>
                        <tr>
                            <td>Rentan (Balita/Lansia)</td>
                            <td style="text-align: right;"><b>{d['Rentan_BL_Desa']:,}</b> jiwa</td>
                        </tr>
                        <tr>
                            <td>Rentan (Miskin)</td>
                            <td style="text-align: right;"><b>{d['Rentan_Miskin_Desa']:,}</b> jiwa</td>
                        </tr>
                        <tr>
                            <td>Rentan (Disabilitas)</td>
                            <td style="text-align: right;"><b>{d['Rentan_Disabilitas_Desa']:,}</b> jiwa</td>
                        </tr>
                    </table>
                </div>
            </div>
            """
            
            # --- LEGENDA MINI SAAT DI-HOVER ---
            tooltip_html = f"""
            <div style="font-family: Arial, sans-serif; text-align: center; min-width: 160px;">
                <b style="font-size: 13px; color: #d35400;">KEC. {d['Kecamatan'].upper()}</b><br>
                Total Terpapar: <b>{d['Total_Terpapar_Kecamatan']:,}</b> jiwa<br>
                <hr style="margin: 6px 0; border: 0; border-top: 1px solid #ccc;">
                <i style="font-size: 10px; color: #34495e;">Klik untuk Zoom & Lihat Detail Desa {d['Desa']}</i>
            </div>
            """
        else:
            popup_html = f'<b>Wilayah: {raw_name.capitalize()}</b><br>Data belum dimasukkan.'
            tooltip_html = f'Area {raw_name.capitalize()}'

        geo_obj = folium.GeoJson(
            feature,
            style_function=style_function,
            highlight_function=highlight_function,
            tooltip=folium.Tooltip(tooltip_html),
            popup=folium.Popup(popup_html, max_width=350),
            zoom_on_click=True # Fitur zoom otomatis
        )
        
        if key_clean:
            # Hapus tooltip ganda
            geo_obj.add_child(folium.features.GeoJsonTooltip(fields=[], labels=False)) 
            geo_obj.options['className'] = f'desa-item desa-{key_clean}'
            
        geo_obj.add_to(m)

    m.get_root().html.add_child(folium.Element(get_legend_html()))
    return m._repr_html_()

# =========================================================
# 4. ROUTING & AI
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
    konteks_ml = str(data_dict)
    
    system_prompt = f"""
Kamu adalah Asisten Virtual BPBD KBB.
Berikut adalah data spasial risiko bencana:
{konteks_ml}

ATURAN MENJAWAB:
1. DILARANG KERAS mengarang data. Gunakan angka persis dari data.
2. Jika ditanya prioritas, cari yang "Total_Terpapar_Kecamatan" atau "Warga_Terpapar_Desa"-nya tertinggi.
3. Wajib gunakan format Bullet Points.
4. Gunakan huruf tebal (**teks**) untuk menegaskan wilayah.
5. Jawab maksimal 3 paragraf, padat dan jelas.
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
        ai_reply = res_json['choices'][0]['message']['content']
        return jsonify({"reply": ai_reply})
    except Exception as e:
        return jsonify({"reply": f"[SISTEM] Kerusakan modul pemrosesan API: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
