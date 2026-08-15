import os
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import random

# Menyimpan data mentah yang kamu berikan langsung di dalam script
RAW_DATA_DESA = """
TANAH LONGSOR | Batujajar | Desa Batujajar Barat | 113 | 58 | 10 | 0
TANAH LONGSOR | Batujajar | Desa Batujajar Timur | 3,146 | 1,577 | 190 | 4
TANAH LONGSOR | Batujajar | Desa Giriasih | 1,869 | 938 | 161 | 8
TANAH LONGSOR | Batujajar | Desa Selacau | 2,946 | 1,464 | 277 | 16
TANAH LONGSOR | Cihampelas | Desa Cipatik | 0 | 0 | 0 | 0
TANAH LONGSOR | Cihampelas | Desa Citapen | 0 | 0 | 0 | 0
TANAH LONGSOR | Cihampelas | Desa Pataruman | 2,228 | 1,124 | 183 | 5
TANAH LONGSOR | Cihampelas | Desa Singajaya | 2,968 | 1,526 | 313 | 5
TANAH LONGSOR | Cihampelas | Desa Situwangi | 6,796 | 3,601 | 801 | 28
TANAH LONGSOR | Cihampelas | Desa Tanjungwangi | 1,625 | 875 | 172 | 4
TANAH LONGSOR | Cikalongwetan | Desa Cikalong | 3,184 | 1,688 | 316 | 5
TANAH LONGSOR | Cikalongwetan | Desa Cipada | 6,869 | 3,912 | 622 | 17
TANAH LONGSOR | Cikalongwetan | Desa Ciptagumati | 2,589 | 1,404 | 268 | 5
TANAH LONGSOR | Cikalongwetan | Desa Cisomang Barat | 1,468 | 787 | 188 | 5
TANAH LONGSOR | Cikalongwetan | Desa Ganjarsari | 7,626 | 4,355 | 719 | 29
TANAH LONGSOR | Cikalongwetan | Desa Kanangasari | 3,590 | 2,170 | 417 | 10
TANAH LONGSOR | Cikalongwetan | Desa Mandalamukti | 5,962 | 3,177 | 624 | 13
TANAH LONGSOR | Cikalongwetan | Desa Mandalasari | 5,382 | 2,844 | 642 | 13
TANAH LONGSOR | Cikalongwetan | Desa Mekarjaya | 9,252 | 4,835 | 728 | 88
TANAH LONGSOR | Cikalongwetan | Desa Puteran | 3,212 | 1,845 | 350 | 13
TANAH LONGSOR | Cikalongwetan | Desa Rende | 4,535 | 2,520 | 450 | 20
TANAH LONGSOR | Cikalongwetan | Desa Tenjolaut | 3,352 | 1,835 | 430 | 12
TANAH LONGSOR | Cikalongwetan | Desa Wangunjaya | 2,101 | 1,131 | 252 | 13
TANAH LONGSOR | Cililin | Desa Batulayang | 7,425 | 4,062 | 925 | 35
TANAH LONGSOR | Cililin | Desa Budiharja | 421 | 242 | 57 | 1
TANAH LONGSOR | Cililin | Desa Cililin | 611 | 324 | 69 | 2
TANAH LONGSOR | Cililin | Desa Karanganyar | 3,582 | 2,089 | 373 | 18
TANAH LONGSOR | Cililin | Desa Karangtanjung | 6,058 | 3,160 | 705 | 20
TANAH LONGSOR | Cililin | Desa Karyamukti | 4,080 | 2,238 | 397 | 26
TANAH LONGSOR | Cililin | Desa Kidangpananjung | 4,102 | 2,251 | 598 | 20
TANAH LONGSOR | Cililin | Desa Mukapayung | 11,140 | 6,313 | 1,198 | 55
TANAH LONGSOR | Cililin | Desa Nangerang | 4,808 | 2,714 | 416 | 18
TANAH LONGSOR | Cililin | Desa Rancapanggung | 3,145 | 1,750 | 309 | 15
TANAH LONGSOR | Cipatat | Desa Cipatat | 1,771 | 951 | 180 | 3
TANAH LONGSOR | Cipatat | Desa Ciptaharja | 1,327 | 698 | 144 | 3
TANAH LONGSOR | Cipatat | Desa Cirawamekar | 5,109 | 2,715 | 552 | 22
TANAH LONGSOR | Cipatat | Desa Citatah | 12,673 | 6,852 | 1,282 | 59
TANAH LONGSOR | Cipatat | Desa Gunungmasigit | 12,634 | 6,615 | 1,239 | 49
TANAH LONGSOR | Cipatat | Desa Kertamukti | 2,616 | 1,462 | 309 | 12
TANAH LONGSOR | Cipatat | Desa Mandalasari | 363 | 201 | 37 | 1
TANAH LONGSOR | Cipatat | Desa Mandalawangi | 384 | 213 | 40 | 2
TANAH LONGSOR | Cipatat | Desa Nyalindung | 4,571 | 2,444 | 481 | 24
TANAH LONGSOR | Cipatat | Desa Sarimukti | 1,876 | 1,013 | 197 | 6
TANAH LONGSOR | Cipatat | Desa Sumurbandung | 6,704 | 3,586 | 821 | 44
TANAH LONGSOR | Cipatat | Rajamandala Kulon | 1,031 | 585 | 119 | 3
TANAH LONGSOR | Cipeundeuy | Desa Bojongmekar | 273 | 153 | 25 | 1
TANAH LONGSOR | Cipeundeuy | Desa Ciharashas | 963 | 545 | 91 | 3
TANAH LONGSOR | Cipeundeuy | Desa Cipeundeuy | 316 | 175 | 30 | 0
TANAH LONGSOR | Cipeundeuy | Desa Ciroyom | 895 | 487 | 86 | 1
TANAH LONGSOR | Cipeundeuy | Desa Jatimekar | 584 | 342 | 64 | 1
TANAH LONGSOR | Cipeundeuy | Desa Margalaksana | 131 | 73 | 16 | 0
TANAH LONGSOR | Cipeundeuy | Desa Margaluyu | 1,404 | 810 | 147 | 6
TANAH LONGSOR | Cipeundeuy | Desa Nanggeleng | 973 | 574 | 120 | 3
TANAH LONGSOR | Cipeundeuy | Desa Nyenang | 406 | 230 | 43 | 2
TANAH LONGSOR | Cipeundeuy | Desa Sirnagalih | 370 | 204 | 47 | 1
TANAH LONGSOR | Cipeundeuy | Desa Sirnaraja | 531 | 310 | 55 | 1
TANAH LONGSOR | Cipeundeuy | Desa Sukahaji | 35 | 19 | 4 | 0
TANAH LONGSOR | Cipongkor | Desa Baranang Siang | 7,018 | 3,866 | 684 | 16
TANAH LONGSOR | Cipongkor | Desa Cibenda | 4,968 | 3,041 | 438 | 16
TANAH LONGSOR | Cipongkor | Desa Cijambu | 3,169 | 1,816 | 302 | 4
TANAH LONGSOR | Cipongkor | Desa Cijenuk | 4,696 | 2,611 | 531 | 13
TANAH LONGSOR | Cipongkor | Desa Cintaasih | 6,506 | 3,850 | 607 | 6
TANAH LONGSOR | Cipongkor | Desa Citalem | 2,855 | 1,591 | 300 | 9
TANAH LONGSOR | Cipongkor | Desa Girimukti | 5,881 | 3,264 | 771 | 25
TANAH LONGSOR | Cipongkor | Desa Karangsari | 4,583 | 2,785 | 527 | 16
TANAH LONGSOR | Cipongkor | Desa Mekarsari | 297 | 176 | 38 | 3
TANAH LONGSOR | Cipongkor | Desa Neglasari | 4,095 | 2,354 | 451 | 12
TANAH LONGSOR | Cipongkor | Desa Sarinagen | 4,999 | 2,883 | 496 | 16
TANAH LONGSOR | Cipongkor | Desa Sirnagalih | 3,439 | 2,144 | 235 | 7
TANAH LONGSOR | Cipongkor | Desa Sukamulya | 666 | 380 | 85 | 1
TANAH LONGSOR | Cisarua | Desa Cipada | 4,943 | 2,634 | 411 | 21
TANAH LONGSOR | Cisarua | Desa Jambudipa | 12,315 | 6,380 | 903 | 36
TANAH LONGSOR | Cisarua | Desa Kertawangi | 3,231 | 1,638 | 282 | 9
TANAH LONGSOR | Cisarua | Desa Padaasih | 4,822 | 2,588 | 357 | 13
TANAH LONGSOR | Cisarua | Desa Pasirhalang | 4,408 | 2,432 | 350 | 17
TANAH LONGSOR | Cisarua | Desa Pasirlangu | 3,047 | 1,594 | 240 | 6
TANAH LONGSOR | Cisarua | Desa Sadangmekar | 6,092 | 3,213 | 598 | 32
TANAH LONGSOR | Cisarua | Desa Tugumukti | 3,575 | 1,952 | 389 | 11
TANAH LONGSOR | Gununghalu | Desa Bunijaya | 4,563 | 2,542 | 507 | 21
TANAH LONGSOR | Gununghalu | Desa Celak | 5,576 | 3,128 | 648 | 16
TANAH LONGSOR | Gununghalu | Desa Cilangari | 7,067 | 4,021 | 785 | 53
| Gununghalu | Desa Gununghalu | 7,025 | 3,964 | 878 | 16
TANAH LONGSOR | Gununghalu | Desa SIndangjaya | 3,146 | 1,769 | 317 | 12
TANAH LONGSOR | Gununghalu | Desa Sirnajaya | 7,039 | 3,948 | 754 | 19
TANAH LONGSOR | Gununghalu | Desa Sukasari | 5,290 | 2,948 | 486 | 23
TANAH LONGSOR | Gununghalu | Desa Tamanjaya | 7,913 | 4,533 | 734 | 55
TANAH LONGSOR | Gununghalu | Desa Wargasaluyu | 6,542 | 3,678 | 745 | 34
TANAH LONGSOR | Lembang | Desa Cibodas | 3,251 | 1,733 | 341 | 11
TANAH LONGSOR | Lembang | Desa Cibogo | 4,010 | 2,113 | 303 | 7
TANAH LONGSOR | Lembang | Desa Cikahuripan | 3,884 | 1,977 | 344 | 14
TANAH LONGSOR | Lembang | Desa Cikidang | 2,410 | 1,251 | 287 | 5
TANAH LONGSOR | Lembang | Desa Cikoke | 3,682 | 1,868 | 263 | 13
TANAH LONGSOR | Lembang | Desa Gudangkahuripan | 9,839 | 4,969 | 660 | 17
TANAH LONGSOR | Lembang | Desa Jayagiri | 9,820 | 5,026 | 846 | 21
TANAH LONGSOR | Lembang | Desa Kayuambon | 157 | 80 | 11 | 0
TANAH LONGSOR | Lembang | Desa Langensari | 3,616 | 1,835 | 295 | 5
TANAH LONGSOR | Lembang | Desa Lembang | 3,379 | 1,775 | 181 | 11
TANAH LONGSOR | Lembang | Desa Mekarwangi | 5,805 | 3,166 | 847 | 9
TANAH LONGSOR | Lembang | Desa Pagerwangi | 8,096 | 4,137 | 735 | 27
TANAH LONGSOR | Lembang | Desa Sukajaya | 3,121 | 1,588 | 293 | 12
TANAH LONGSOR | Lembang | Desa Suntenjaya | 8,470 | 4,460 | 1,010 | 30
TANAH LONGSOR | Lembang | Desa Wangunharja | 1,222 | 628 | 131 | 3
TANAH LONGSOR | Lembang | Desa Wangunsari | 6,744 | 3,532 | 628 | 15
TANAH LONGSOR | Ngamprah | Desa Bojongkoneng | 11,792 | 6,571 | 1,129 | 49
TANAH LONGSOR | Ngamprah | Desa Cilame | 3,291 | 1,526 | 177 | 6
TANAH LONGSOR | Ngamprah | Desa Cimanggu | 5,703 | 3,412 | 607 | 2
TANAH LONGSOR | Ngamprah | Desa Gadobangkong | 373 | 194 | 20 | 1
TANAH LONGSOR | Ngamprah | Desa Mekarsari | 229 | 116 | 21 | 0
TANAH LONGSOR | Ngamprah | Desa Ngamprah | 3,078 | 1,702 | 237 | 10
TANAH LONGSOR | Ngamprah | Desa Pakuhaji | 2,901 | 1,451 | 281 | 6
TANAH LONGSOR | Ngamprah | Desa Sukatani | 2,088 | 1,095 | 152 | 3
TANAH LONGSOR | Padalarang | Desa Campakamekar | 6,996 | 3,684 | 713 | 27
TANAH LONGSOR | Padalarang | Desa Ciburuy | 4,847 | 2,508 | 364 | 14
TANAH LONGSOR | Padalarang | Desa Jayamekar | 10,486 | 5,277 | 859 | 29
TANAH LONGSOR | Padalarang | Desa Kertajaya | 0 | 0 | 0 | 0
TANAH LONGSOR | Padalarang | Desa Kertamulya | 1,544 | 797 | 106 | 5
TANAH LONGSOR | Padalarang | Desa Laksanamekar | 3,589 | 1,752 | 267 | 9
TANAH LONGSOR | Padalarang | Desa Padalarang | 6,346 | 3,099 | 399 | 13
TANAH LONGSOR | Padalarang | Desa Tagogapu | 6,530 | 3,574 | 616 | 19
TANAH LONGSOR | Parongpong | Desa Cigugurgirang | 309 | 161 | 19 | 1
TANAH LONGSOR | Parongpong | Desa Cihanjuang | 3,094 | 1,582 | 234 | 5
TANAH LONGSOR | Parongpong | Desa Cihanjuang Rahayu | 9,141 | 4,694 | 620 | 13
TANAH LONGSOR | Parongpong | Desa Cihideung | 7,315 | 3,686 | 395 | 5
TANAH LONGSOR | Parongpong | Desa Ciwaruga | 1,640 | 880 | 98 | 5
TANAH LONGSOR | Parongpong | Desa Karyawangi | 3,328 | 1,649 | 249 | 2
TANAH LONGSOR | Parongpong | Desa Sariwangi | 2,434 | 1,221 | 149 | 5
TANAH LONGSOR | Rongga | Desa Bojong | 1,679 | 984 | 151 | 6
TANAH LONGSOR | Rongga | Desa Bojongsalam | 4,334 | 2,329 | 388 | 18
TANAH LONGSOR | Rongga | Desa Cibedug | 1,369 | 852 | 128 | 3
TANAH LONGSOR | Rongga | Desa Cibitung | 6,119 | 3,474 | 522 | 27
TANAH LONGSOR | Rongga | Desa Cicadas | 5,073 | 2,982 | 380 | 46
TANAH LONGSOR | Rongga | Desa Cinengah | 4,687 | 2,785 | 470 | 20
TANAH LONGSOR | Rongga | Desa Sukamanah | 6,455 | 3,726 | 623 | 31
TANAH LONGSOR | Rongga | Desa Sukaresmi | 9,022 | 5,273 | 681 | 37
TANAH LONGSOR | Saguling | Desa Bojonghaleuang | 1,589 | 830 | 164 | 3
TANAH LONGSOR | Saguling | Desa Cikande | 1,602 | 861 | 144 | 5
TANAH LONGSOR | Saguling | Desa Cipangeran | 3,337 | 1,918 | 386 | 6
TANAH LONGSOR | Saguling | Desa Girimukti | 1,472 | 797 | 152 | 4
TANAH LONGSOR | Saguling | Desa Jati | 3,444 | 1,993 | 475 | 8
TANAH LONGSOR | Saguling | Desa Saguling | 6,575 | 3,620 | 547 | 14
TANAH LONGSOR | Sindangkerta | Desa Bunianagara | 4,175 | 2,492 | 485 | 29
TANAH LONGSOR | Sindangkerta | Desa Cicangkanggirang | 7,973 | 4,671 | 892 | 36
TANAH LONGSOR | Sindangkerta | Desa Cikadu | 1,793 | 1,076 | 200 | 3
TANAH LONGSOR | Sindangkerta | Desa Cintakarya | 2,110 | 1,255 | 234 | 4
TANAH LONGSOR | Sindangkerta | Desa Mekarwangi | 3,733 | 2,073 | 259 | 14
TANAH LONGSOR | Sindangkerta | Desa Pasirpogor | 2,500 | 1,437 | 283 | 8
TANAH LONGSOR | Sindangkerta | Desa Puncaksari | 2,105 | 1,205 | 265 | 3
TANAH LONGSOR | Sindangkerta | Desa Rancasenggang | 5,232 | 3,078 | 457 | 13
TANAH LONGSOR | Sindangkerta | Desa Sindangkerta | 0 | 0 | 0 | 0
TANAH LONGSOR | Sindangkerta | Desa Wangunsari | 5,438 | 3,315 | 322 | 7
TANAH LONGSOR | Sindangkerta | Desa Weninggalih | 6,159 | 3,652 | 649 | 41
"""

def clean_name(s):
    if not s: return ''
    # Membersihkan nama desa agar mudah dicocokkan dengan GeoJSON
    return str(s).lower().replace('_', '').replace(' ', '').replace('desa', '').replace('kelurahan', '').replace('kecamatan', '').replace('kec.', '').strip()

def get_ml_clustered_data(app_root_path):
    records = []
    lines = [line.strip() for line in RAW_DATA_DESA.strip().split('\n') if line.strip()]
    
    for line in lines:
        parts = [p.strip() for p in line.split('|')]
        # Menggunakan index negatif karena ada row yang tidak memiliki "TANAH LONGSOR"
        if len(parts) >= 6:
            kec_name = parts[-6]
            desa_name = parts[-5]
            
            try:
                jml_penduduk = int(parts[-4].replace(',', ''))
                umur_rentan = int(parts[-3].replace(',', ''))
                miskin = int(parts[-2].replace(',', ''))
                disabilitas = int(parts[-1].replace(',', ''))
            except ValueError:
                continue
                
            # Skip desa tanpa penduduk agar tidak error dibagi nol
            if jml_penduduk == 0: 
                continue 
            
            # SIMULASI DATA EDUKASI (Karena tidak ada di data asli)
            # Dibuat konsisten berdasarkan nama desa agar tidak berubah saat di-refresh
            random.seed(desa_name) 
            teredukasi = int(jml_penduduk * random.uniform(0.15, 0.75))
            persen_edu = round((teredukasi / jml_penduduk) * 100, 2)
            
            records.append({
                'Kecamatan': kec_name,
                'Desa': desa_name.replace('Desa ', '').strip(),
                'Total_Warga': jml_penduduk,
                'Warga_Teredukasi': teredukasi,
                'Persen_Edukasi': persen_edu,
                'Umur_Rentan': umur_rentan,
                'Miskin': miskin,
                'Disabilitas': disabilitas,
                'Rasio_Rentan': (umur_rentan / jml_penduduk) * 100,
                'Rasio_Miskin': (miskin / jml_penduduk) * 100,
                'Rasio_Disabilitas': (disabilitas / jml_penduduk) * 100,
                'Kelas_Risiko': 'Tinggi' if persen_edu < 30 else 'Sedang'
            })

    df = pd.DataFrame(records)
    if df.empty: return df

    # Jalankan K-Means Clustering Berbasis Desa
    features = ['Rasio_Rentan', 'Rasio_Miskin', 'Rasio_Disabilitas', 'Persen_Edukasi']
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[features])

    kmeans = KMeans(n_clusters=3, random_state=42, n_init='auto')
    df['Cluster'] = kmeans.fit_predict(X_scaled)
    
    return df
