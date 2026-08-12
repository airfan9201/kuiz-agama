# =========================================================
# TETAPAN REDIS / VERCEL DATABASE (AUTO-DETECT KEY)
# =========================================================
import urllib.parse
import redis
import os
import json
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')
    
# =========================================================
# DATA SOALAN KUIZ (50 SOALAN SETIAP KATEGORI)
# =========================================================
QUIZ_DATA = {
    "rukun": {
        "rukun_iman": [
            {"id": 1, "soalan": "Berapakah bilangan Rukun Iman?", "pilihan": ["5", "6", "7", "10"], "jawapan": 1},
            {"id": 2, "soalan": "Apakah Rukun Iman yang pertama?", "pilihan": ["Beriman kepada Malaikat", "Beriman kepada Allah", "Beriman kepada Kitab", "Beriman kepada Hari Kiamat"], "jawapan": 1},
            {"id": 3, "soalan": "Malaikat manakah yang bertugas membawa wahyu?", "pilihan": ["Malaikat Mikail", "Malaikat Israfil", "Malaikat Jibril", "Malaikat Izrail"], "jawapan": 2},
            {"id": 4, "soalan": "Kitab Al-Quran diturunkan kepada Nabi...", "pilihan": ["Nabi Musa A.S.", "Nabi Isa A.S.", "Nabi Daud A.S.", "Nabi Muhammad S.A.W."], "jawapan": 3},
            {"id": 5, "soalan": "Beriman kepada Qada' dan Qadar merupakan Rukun Iman yang ke-...", "pilihan": ["3", "4", "5", "6"], "jawapan": 3},
            {"id": 6, "soalan": "Malaikat yang bertugas mencatat amal baik ialah...", "pilihan": ["Raqib", "Atid", "Munkar", "Nakir"], "jawapan": 0},
            {"id": 7, "soalan": "Kitab Taurat diturunkan kepada Nabi...", "pilihan": ["Nabi Musa A.S.", "Nabi Isa A.S.", "Nabi Ibrahim A.S.", "Nabi Daud A.S."], "jawapan": 0},
            {"id": 8, "soalan": "Kitab Zabur diturunkan kepada Nabi...", "pilihan": ["Nabi Daud A.S.", "Nabi Isa A.S.", "Nabi Musa A.S.", "Nabi Adam A.S."], "jawapan": 0},
            {"id": 9, "soalan": "Kitab Injil diturunkan kepada Nabi...", "pilihan": ["Nabi Isa A.S.", "Nabi Musa A.S.", "Nabi Yahya A.S.", "Nabi Muhammad S.A.W."], "jawapan": 0},
            {"id": 10, "soalan": "Malaikat yang bertugas mencabut nyawa ialah...", "pilihan": ["Malaikat Izrail", "Malaikat Israfil", "Malaikat Malik", "Malaikat Ridwan"], "jawapan": 0},
            {"id": 11, "soalan": "Malaikat yang meniup sangkakala pada hari kiamat ialah...", "pilihan": ["Malaikat Israfil", "Malaikat Mikail", "Malaikat Jibril", "Malaikat Ridwan"], "jawapan": 0},
            {"id": 12, "soalan": "Malaikat peniup sangkakala, pembagi rezeki, dan penjaga syurga adalah contoh beriman kepada...", "pilihan": ["Malaikat", "Rasul", "Kitab", "Qada' dan Qadar"], "jawapan": 0},
            {"id": 13, "soalan": "Siapakah Nabi dan Rasul yang pertama?", "pilihan": ["Nabi Adam A.S.", "Nabi Nuh A.S.", "Nabi Ibrahim A.S.", "Nabi Muhammad S.A.W."], "jawapan": 0},
            {"id": 14, "soalan": "Berapakah bilangan Rasul yang wajib diketahui?", "pilihan": ["10", "20", "25", "313"], "jawapan": 2},
            {"id": 15, "soalan": "Gelaran 'Ulul Azmi' diberikan kepada Rasul yang...", "pilihan": ["Paling kaya", "Mempunyai ketabahan & kesabaran luar biasa", "Paling panjang umur", "Paling banyak mukjizat"], "jawapan": 1},
            {"id": 16, "soalan": "Berikut adalah Rasul Ulul Azmi KECUALI...", "pilihan": ["Nabi Nuh A.S.", "Nabi Ibrahim A.S.", "Nabi Yunus A.S.", "Nabi Musa A.S."], "jawapan": 2},
            {"id": 17, "soalan": "Percaya bahawa segala yang berlaku adalah ketentuan Allah dinamakan...", "pilihan": ["Qada' dan Qadar", "Tawakal", "Ikhlas", "Redha"], "jawapan": 0},
            {"id": 18, "soalan": "Malaikat yang bertugas menjaga pintu Syurga ialah...", "pilihan": ["Malaikat Ridwan", "Malaikat Malik", "Malaikat Atid", "Malaikat Raqib"], "jawapan": 0},
            {"id": 19, "soalan": "Malaikat yang bertugas menjaga pintu Neraka ialah...", "pilihan": ["Malaikat Malik", "Malaikat Ridwan", "Malaikat Munkar", "Malaikat Nakir"], "jawapan": 0},
            {"id": 20, "soalan": "Hari kebangkitan semula manusia dari kubur dikenali sebagai...", "pilihan": ["Yaumul Ba'ath", "Yaumul Mahsyar", "Yaumul Hisab", "Yaumul Mizan"], "jawapan": 0},
            {"id": 21, "soalan": "Malaikat yang bertugas menyoal mayat di dalam kubur ialah...", "pilihan": ["Munkar dan Nakir", "Raqib dan Atid", "Jibril dan Mikail", "Malik dan Ridwan"], "jawapan": 0},
            {"id": 22, "soalan": "Suhuf diturunkan kepada beberapa orang Nabi. Siapakah yang menerima Suhuf paling banyak?", "pilihan": ["Nabi Syith A.S.", "Nabi Ibrahim A.S.", "Nabi Musa A.S.", "Nabi Idris A.S."], "jawapan": 0},
            {"id": 23, "soalan": "Beriman kepada Kitab bermaksud meyakini bahawa...", "pilihan": ["Allah menurunkan petunjuk melalui wahyu kepada para Rasul", "Semua kitab lama masih boleh diamalkan", "Al-Quran ciptaan manusia", "Kitab suci hanya untuk orang Arab"], "jawapan": 0},
            {"id": 24, "soalan": "Apakah maksud Qada'?", "pilihan": ["Ketentuan Allah sejak azali", "Pelaksanaan ketentuan Allah", "Usaha manusia", "Doa manusia"], "jawapan": 0},
            {"id": 25, "soalan": "Apakah maksud Qadar?", "pilihan": ["Pelaksanaan ketentuan Allah mengikut kadar yang ditetapkan", "Ketetapan azali", "Pasrah tanpa usaha", "Keberhasilan cita-cita"], "jawapan": 0},
            {"id": 26, "soalan": "Timbangan amal kebaikan dan keburukan di akhirat dipanggil...", "pilihan": ["Al-Mizan", "As-Sirat", "Al-Mahsyar", "Al-Hisab"], "jawapan": 0},
            {"id": 27, "soalan": "Titian yang merentasi di atas neraka menuju ke syurga dinamakan...", "pilihan": ["As-Sirat", "Al-Mizan", "Al-Kautsar", "Al-Mahsyar"], "jawapan": 0},
            {"id": 28, "soalan": "Nabi yang mendapat gelaran 'Khalilullah' (Kekasih Allah) ialah...", "pilihan": ["Nabi Ibrahim A.S.", "Nabi Musa A.S.", "Nabi Isa A.S.", "Nabi Muhammad S.A.W."], "jawapan": 0},
            {"id": 29, "soalan": "Nabi yang mendapat gelaran 'Kalimullah' (yang berbicara dengan Allah) ialah...", "pilihan": ["Nabi Musa A.S.", "Nabi Isa A.S.", "Nabi Adam A.S.", "Nabi Nuh A.S."], "jawapan": 0},
            {"id": 30, "soalan": "Hukum beriman kepada semua Rukun Iman adalah...", "pilihan": ["Wajib", "Sunat", "Harus", "Makruh"], "jawapan": 0},
            {"id": 31, "soalan": "Siapakah Malaikat yang bertugas mengurus hujan dan rezeki?", "pilihan": ["Malaikat Mikail", "Malaikat Jibril", "Malaikat Israfil", "Malaikat Izrail"], "jawapan": 0},
            {"id": 32, "soalan": "Malaikat diciptakan daripada...", "pilihan": ["Cahaya (Nur)", "Api (Nar)", "Tanah", "Angin"], "jawapan": 0},
            {"id": 33, "soalan": "Jin dan Iblis diciptakan daripada...", "pilihan": ["Pucuk Api (Nar)", "Cahaya", "Tanah", "Air"], "jawapan": 0},
            {"id": 34, "soalan": "Manusia pertama yang diciptakan oleh Allah SWT ialah...", "pilihan": ["Nabi Adam A.S.", "Nabi Muhammad SAW", "Nabi Ibrahim A.S.", "Nabi Nuh A.S."], "jawapan": 0},
            {"id": 35, "soalan": "Nabi Isa A.S. dikurniakan kitaban suci bernama...", "pilihan": ["Injil", "Taurat", "Zabur", "Al-Quran"], "jawapan": 0},
            {"id": 36, "soalan": "Peristiwa perhimpunan seluruh manusia selepas dibangkitkan semula berlaku di...", "pilihan": ["Padang Mahsyar", "Gua Hira'", "Padang Arafah", "Baitulmaqdis"], "jawapan": 0},
            {"id": 37, "soalan": "Nabi yang membina Bahtera (Kapal Besar) untuk menyelamatkan pengikutnya dari banjir besar ialah...", "pilihan": ["Nabi Nuh A.S.", "Nabi Hud A.S.", "Nabi Saleh A.S.", "Nabi Yunus A.S."], "jawapan": 0},
            {"id": 38, "soalan": "Apakah hukum percaya kepada kewujudan Hari Kiamat?", "pilihan": ["Wajib", "Sunat", "Harus", "Makruh"], "jawapan": 0},
            {"id": 39, "soalan": "Mukjizat terbesar Nabi Muhammad SAW yang kekal hingga ke hari kiamat ialah...", "pilihan": ["Al-Quran", "Pembelahan Bulan", "Air keluar dari jemari", "Isra' Mi'raj"], "jawapan": 0},
            {"id": 40, "soalan": "Nabi yang diuji dengan penyakit kulit yang berat tetapi kekal bersabar ialah...", "pilihan": ["Nabi Ayyub A.S.", "Nabi Yusuf A.S.", "Nabi Yaakub A.S.", "Nabi Harun A.S."], "jawapan": 0},
            {"id": 41, "soalan": "Nabi yang pernah ditelan oleh ikan nun/paus ialah...", "pilihan": ["Nabi Yunus A.S.", "Nabi Ilyas A.S.", "Nabi Zakaria A.S.", "Nabi Yahya A.S."], "jawapan": 0},
            {"id": 42, "soalan": "Berapakah jumlah surah yang terdapat di dalam Al-Quran?", "pilihan": ["114 Surah", "110 Surah", "30 Surah", "66 Surah"], "jawapan": 0},
            {"id": 43, "soalan": "Perkara ghaib yang wajib dipercayai merangkumi perkara berikut KECUALI...", "pilihan": ["Ramalan nasib tukang tilik", "Syurga dan Neraka", "Malaikat", "Siksa Kubur"], "jawapan": 0},
            {"id": 44, "soalan": "Nabi yang mempunyai mukjizat boleh bercakap dengan haiwan dan mengawal angin ialah...", "pilihan": ["Nabi Sulaiman A.S.", "Nabi Daud A.S.", "Nabi Yusuf A.S.", "Nabi Musa A.S."], "jawapan": 0},
            {"id": 45, "soalan": "Sifat wajib bagi Allah 'Al-Alim' bermaksud Allah Maha...", "pilihan": ["Mengetahui", "Melihat", "Mendengar", "Berkuasa"], "jawapan": 0},
            {"id": 46, "soalan": "Sifat wajib bagi Rasul 'Siddiq' bermaksud...", "pilihan": ["Bercakap benar", "Menyampaikan", "Bijaksana", "Amanah"], "jawapan": 0},
            {"id": 47, "soalan": "Sifat wajib bagi Rasul 'Amanah' bermaksud...", "pilihan": ["Jujur / Boleh dipercayai", "Bijaksana", "Pendiam", "Penyabar"], "jawapan": 0},
            {"id": 48, "soalan": "Sifat 'Fatanah' bagi seseorang Rasul bermaksud...", "pilihan": ["Bijaksana", "Jujur", "Tebal sabar", "Kuat tubuh"], "jawapan": 0},
            {"id": 49, "soalan": "Nabi yang dikurniakan ketampanan rupa paras yang luar biasa ialah...", "pilihan": ["Nabi Yusuf A.S.", "Nabi Musa A.S.", "Nabi Isa A.S.", "Nabi Adam A.S."], "jawapan": 0},
            {"id": 50, "soalan": "Syurga tempat ganjaran bagi orang beriman dinamakan...", "pilihan": ["Jannah", "Jahannam", "Barzakh", "Mahsyar"], "jawapan": 0},
            {"id": 51, "soalan": "Sifat wajib bagi Rasul 'Tabligh' bermaksud...", "pilihan": ["Menyampaikan wahyu", "Bercakap benar", "Bijaksana", "Amanah"], "jawapan": 0},
            {"id": 52, "soalan": "Malaikat yang bertugas mencatat amal keburukan ialah...", "pilihan": ["Atid", "Raqib", "Munkar", "Nakir"], "jawapan": 0},
            {"id": 53, "soalan": "Mustahil bagi Allah bersifat 'Jahlun' yang bermaksud...", "pilihan": ["Bodo / Jahil", "Lemah", "Mati", "Tuli"], "jawapan": 0},
            {"id": 54, "soalan": "Alam kehidupan di dalam kubur sementara menunggu hari kiamat dipanggil...", "pilihan": ["Alam Barzakh", "Padang Mahsyar", "Alam Rahim", "Alam Malakut"], "jawapan": 0},
            {"id": 55, "soalan": "Suhuf merupakan lembaran wahyu yang tidak dibukukan. Nabi yang menerima suhuf ialah...", "pilihan": ["Nabi Ibrahim A.S.", "Nabi Muhammad SAW", "Nabi Isa A.S.", "Nabi Nuh A.S."], "jawapan": 0},
            {"id": 56, "soalan": "Qada' yang boleh berubah melalui doa dan usaha manusia dinamakan...", "pilihan": ["Qada' Muallaq", "Qada' Mubram", "Qada' Mutlaq", "Qada' Qadim"], "jawapan": 0},
            {"id": 57, "soalan": "Qada' yang pasti berlaku dan tidak boleh diubah seperti kematian dinamakan...", "pilihan": ["Qada' Mubram", "Qada' Muallaq", "Qada' Harfi", "Qada' Aradi"], "jawapan": 0},
            {"id": 58, "soalan": "Berapakah sifat wajib bagi Allah SWT yang asas perlu diketahui?", "pilihan": ["20 Sifat", "10 Sifat", "99 Sifat", "13 Sifat"], "jawapan": 0},
            {"id": 59, "soalan": "Nabi yang boleh menghidupkan orang mati atas izin Allah ialah...", "pilihan": ["Nabi Isa A.S.", "Nabi Musa A.S.", "Nabi Yahya A.S.", "Nabi Ibrahim A.S."], "jawapan": 0},
            {"id": 60, "soalan": "Nabi yang tongkatnya boleh bertukar menjadi ular besar ialah...", "pilihan": ["Nabi Musa A.S.", "Nabi Harun A.S.", "Nabi Sulaiman A.S.", "Nabi Sholeh A.S."], "jawapan": 0},
            {"id": 61, "soalan": "Peristiwa perisian perhitungan amalan manusia di akhirat dikenali sebagai...", "pilihan": ["Yaumul Hisab", "Yaumul Mizan", "Yaumul Ba'ath", "Yaumul Jaza'"], "jawapan": 0},
            {"id": 62, "soalan": "Apakah nama telaga atau sungai khas untuk Nabi Muhammad SAW di syurga?", "pilihan": ["Al-Kautsar", "Salsabil", "Ma'in", "Tasnim"], "jawapan": 0},
            {"id": 63, "soalan": "Sifat mustahil bagi Rasul 'Kizib' bermaksud...", "pilihan": ["Berdusta", "Kianat", "Menyembunyikan", "Bodoh"], "jawapan": 0},
            {"id": 64, "soalan": "Sifat mustahil bagi Rasul 'Khianat' bermaksud...", "pilihan": ["Pecah amanah", "Berdusta", "Bodoh", "Lupa"], "jawapan": 0},
            {"id": 65, "soalan": "Sifat mustahil bagi Rasul 'Kitman' bermaksud...", "pilihan": ["Menyembunyikan wahyu", "Dusta", "Bodoh", "Pecah amanah"], "jawapan": 0},
            {"id": 66, "soalan": "Sifat mustahil bagi Rasul 'Baladah' bermaksud...", "pilihan": ["Bodoh", "Dusta", "Sombong", "Khianat"], "jawapan": 0},
            {"id": 67, "soalan": "Kejadian luar biasa yang dikurniakan kepada para Nabi dipanggil...", "pilihan": ["Mukjizat", "Karamah", "Irhas", "Ma'unah"], "jawapan": 0},
            {"id": 68, "soalan": "Kejadian luar biasa yang berlaku kepada wali-wali Allah dipanggil...", "pilihan": ["Karamah", "Mukjizat", "Irhas", "Istidraj"], "jawapan": 0},
            {"id": 69, "soalan": "Beriman kepada Rasul ke-25 iaitu Nabi Muhammad SAW bermaksud...", "pilihan": ["Mengikuti syariat baginda sepenuhnya", "Sekadar percaya nama baginda", "Membaca sejarahnya sahaja", "Menganggap baginda tuhan"], "jawapan": 0},
            {"id": 70, "soalan": "Sifat Wujud bagi Allah bermaksud Allah itu...", "pilihan": ["Ada", "Sedia", "Kekal", "Esa"], "jawapan": 0}
        ],
        "rukun_islam": [
            {"id": 1, "soalan": "Berapakah bilangan Rukun Islam?", "pilihan": ["4", "5", "6", "7"], "jawapan": 1},
            {"id": 2, "soalan": "Mengucap dua kalimah syahadah merupakan Rukun Islam yang ke-...", "pilihan": ["Pertama", "Kedua", "Ketiga", "Keempat"], "jawapan": 0},
            {"id": 3, "soalan": "Rukun Islam yang kedua ialah...", "pilihan": ["Mendirikan Solat", "Menunaikan Zakat", "Berpuasa di bulan Ramadan", "Mengerjakan Haji"], "jawapan": 0},
            {"id": 4, "soalan": "Ibadah puasa wajib dijalankan pada bulan...", "pilihan": ["Syawal", "Ramadan", "Rejab", "Syaaban"], "jawapan": 1},
            {"id": 5, "soalan": "Mengerjakan Haji wajib bagi mereka yang...", "pilihan": ["Berilmu tinggi", "Mampu dari segi kewangan & kesihatan", "Berumur 40 tahun ke atas", "Tinggal di Makkah sahaja"], "jawapan": 1},
            {"id": 6, "soalan": "Syahadah terdiri daripada penyaksian kepada...", "pilihan": ["Allah dan Malaikat", "Allah dan Rasul-Nya", "Allah dan Kitab", "Malaikat dan Rasul"], "jawapan": 1},
            {"id": 7, "soalan": "Ibadah yang menjadi 'tiang agama' ialah...", "pilihan": ["Solat", "Zakat", "Puasa", "Haji"], "jawapan": 0},
            {"id": 8, "soalan": "Zakat yang wajib dikeluarkan pada akhir bulan Ramadan dinamakan...", "pilihan": ["Zakat Mal", "Zakat Fitrah", "Zakat Perniagaan", "Zakat Emas"], "jawapan": 1},
            {"id": 9, "soalan": "Apakah syarat wajib ibadah puasa Ramadan?", "pilihan": ["Kaya", "Islam, baligh, dan berakal", "Sudah menunaikan haji", "Menafkahkan harta"], "jawapan": 1},
            {"id": 10, "soalan": "Tempat pelaksanaan ibadah Haji adalah di...", "pilihan": ["Makkah dan kawasan sekitarnya", "Madinah", "Baitulmaqdis", "Kaherah"], "jawapan": 0},
            {"id": 11, "soalan": "Apakah hukum mengucap Dua Kalimah Syahadah bagi seseorang yang mahu memeluk Islam?", "pilihan": ["Wajib", "Sunat", "Harus", "Makruh"], "jawapan": 0},
            {"id": 12, "soalan": "Solat fardu sehari semalam mengandungi berapa rakaat kesemuanya?", "pilihan": ["15 Rakaat", "17 Rakaat", "20 Rakaat", "12 Rakaat"], "jawapan": 1},
            {"id": 13, "soalan": "Zakat harta dikeluarkannya bertujuan untuk...", "pilihan": ["Membersihkan harta dan menyucikan jiwa", "Menunjuk-nunjuk", "Menambah keuntungan perniagaan", "Membayar cukai kerajaan"], "jawapan": 0},
            {"id": 14, "soalan": "Puasa bermaksud menahan diri daripada perkara yang membatalkan puasa bermula dari...", "pilihan": ["Terbit fajar hingga terbenam matahari", "Terbit matahari hingga terbenam matahari", "Subuh hingga Isyak", "Tengah malam hingga petang"], "jawapan": 0},
            {"id": 15, "soalan": "Bulan kesepuluh dalam kalendar Hijrah di mana umat Islam menyambut Hari Raya Aidilfitri ialah...", "pilihan": ["Syawal", "Ramadan", "Zulhijjah", "Muharram"], "jawapan": 0},
            {"id": 16, "soalan": "Apakah ibadah yang dilakukan dengan mengelilingi Kaabah sebanyak 7 kali?", "pilihan": ["Tawaf", "Sa'i", "Wukuf", "Tahallul"], "jawapan": 0},
            {"id": 17, "soalan": "Berlari-lari kecil antara bukit Safa dan Marwah dinamakan...", "pilihan": ["Sa'i", "Tawaf", "Wukuf", "Rami Juamrat"], "jawapan": 0},
            {"id": 18, "soalan": "Kadar zakat fitrah dikeluarkan dalam bentuk makanan asasi seperti...", "pilihan": ["Beras", "Gandum sahaja", "Buah kurma sahaja", "Roti"], "jawapan": 0},
            {"id": 19, "soalan": "Kemuncak ibadah haji di mana para jemaah berkumpul di Padang Arafah dinamakan...", "pilihan": ["Wukuf", "Tawaf Wada'", "Mabit", "Tahallul"], "jawapan": 0},
            {"id": 20, "soalan": "Orang yang berhak menerima zakat dipanggil...", "pilihan": ["Asnaf", "Amil", "Muallaf", "Fakir"], "jawapan": 0},
            {"id": 21, "soalan": "Berapakah bilangan golongan Asnaf yang berhak menerima zakat?", "pilihan": ["8 Golongan", "6 Golongan", "10 Golongan", "5 Golongan"], "jawapan": 0},
            {"id": 22, "soalan": "Menyengaja makan dan minum dengan sengaja semasa berpuasa hukumnya...", "pilihan": ["Membatalkan puasa", "Harus", "Makruh", "Dimaafkan"], "jawapan": 0},
            {"id": 23, "soalan": "Solat yang tidak boleh ditinggalkan dalam apa jua keadaan selagi berakal ialah...", "pilihan": ["Solat Fardu", "Solat Sunat", "Solat Dhuha", "Solat Tahajjud"], "jawapan": 0},
            {"id": 24, "soalan": "Memotong rambut sekurang-kurangnya 3 helai selepas ibadah haji/umrah dipanggil...", "pilihan": ["Tahallul", "Tawaf", "Sa'i", "Ihram"], "jawapan": 0},
            {"id": 25, "soalan": "Niat ihram haji dilakukan di tempat yang ditetapkan yang dipanggil...", "pilihan": ["Miqat", "Maqam Ibrahim", "Hijir Ismail", "Multazam"], "jawapan": 0},
            {"id": 26, "soalan": "Solat sunat yang dipraktikkan khusus pada malam-malam bulan Ramadan ialah...", "pilihan": ["Solat Tarawih", "Solat Witir", "Solat Tahajjud", "Solat Hajat"], "jawapan": 0},
            {"id": 27, "soalan": "Hukum menunaikan ibadah Haji bagi yang berkemampuan adalah wajib sebanyak...", "pilihan": ["Sekali seumur hidup", "Setiap tahun", "Dua kali seumur hidup", "Mengikut kehendak diri"], "jawapan": 0},
            {"id": 28, "soalan": "Niat puasa Ramadan adalah tergolong dalam...", "pilihan": ["Rukun Puasa", "Syarat Sah Puasa", "Sunat Puasa", "Perkara membatalkan puasa"], "jawapan": 0},
            {"id": 29, "soalan": "Mengucapkan dua kalimah syahadah menandakan seseorang itu...", "pilihan": ["Masuk Islam", "Mencapai umur baligh", "Selesai haji", "Mendapat pahala sunat"], "jawapan": 0},
            {"id": 30, "soalan": "Pelaksanaan Rukun Islam membentuk pertalian manusia dengan Allah dan...", "pilihan": ["Sesama manusia", "Malaikat sahaja", "Haiwan sahaja", "Alam ghaib"], "jawapan": 0},
            {"id": 31, "soalan": "Ibadah puasa mengajar umat Islam tentang sifat...", "pilihan": ["Sabar dan empati", "Membazir", "Sombong", "Pentingkan diri"], "jawapan": 0},
            {"id": 32, "soalan": "Bulan yang diwajibkan berpuasa dalam kalendar Islam ialah...", "pilihan": ["Ramadan", "Rejab", "Syaaban", "Muharram"], "jawapan": 0},
            {"id": 33, "soalan": "Malam yang lebih baik daripada 1000 bulan di bulan Ramadan dipanggil...", "pilihan": ["Lailatul Qadar", "Nuzul Al-Quran", "Israk Mikraj", "Malam Isra'"], "jawapan": 0},
            {"id": 34, "soalan": "Perbuatan bersahur sebelum berpuasa hukumnya...", "pilihan": ["Sunat", "Wajib", "Harus", "Makruh"], "jawapan": 0},
            {"id": 35, "soalan": "Memberi makan kepada orang yang berbuka puasa mendapat pahala...", "pilihan": ["Sama seperti pahala orang berpuasa", "Setengah pahala", "Tiada pahala", "Double pahala haji"], "jawapan": 0},
            {"id": 36, "soalan": "Hari Raya Korban/Haji diraikan pada bulan...", "pilihan": ["Zulhijjah", "Syawal", "Ramadan", "Muharram"], "jawapan": 0},
            {"id": 37, "soalan": "Menyembelih binatang ternakan pada 10, 11, 12, dan 13 Zulhijjah dipanggil...", "pilihan": ["Ibadah Korban", "Akikah", "Dam", "Fidyah"], "jawapan": 0},
            {"id": 38, "soalan": "Ibadah penyembelihan ternakan atas kelahiran bayi dipanggil...", "pilihan": ["Akikah", "Korban", "Nazar", "Sedekah"], "jawapan": 0},
            {"id": 39, "soalan": "Pakaian khusus berwarna putih tanpa jahitan bagi jemaah haji lelaki dinamakan...", "pilihan": ["Kain Ihram", "Jubah", "Kain Pelikat", "Samping"], "jawapan": 0},
            {"id": 40, "soalan": "Cukai/bayaran ganti rugi kerana melanggar larangan ihram haji dipanggil...", "pilihan": ["Dam", "Fidyah", "Zakat", "Cukai"], "jawapan": 0},
            {"id": 41, "soalan": "Hari Arafah iaitu hari puncak wukuf jatuh pada date...", "pilihan": ["9 Zulhijjah", "10 Zulhijjah", "1 Syawal", "15 Ramadan"], "jawapan": 0},
            {"id": 42, "soalan": "Membaling batu di Jamrah melambangkan penolakan terhadap...", "pilihan": ["Godaan Syaitan", "Musuh Islam", "Kemiskinan", "Dosa lalu"], "jawapan": 0},
            {"id": 43, "soalan": "Syarat wajib zakat harta antaranya ialah 'Nisab'. Apakah maksud Nisab?", "pilihan": ["Kadar minimum harta yang mewajibkan zakat", "Tempoh pemilikan setahun", "Jenis harta", "Nama penerima zakat"], "jawapan": 0},
            {"id": 44, "soalan": "Apakah maksud 'Haul' dalam syarat zakat?", "pilihan": ["Cukup tempoh pemilikan harta selama setahun", "Cukup berat harta", "Ketiadaan hutang", "Telah mencapai umur dewasa"], "jawapan": 0},
            {"id": 45, "soalan": "Golongan Muallaf adalah antara penerima zakat. Siapakah Muallaf?", "pilihan": ["Orang yang baru memeluk agama Islam", "Orang fakir", "Orang berhutang", "Pengumpul zakat"], "jawapan": 0},
            {"id": 46, "soalan": "Solat Sunat Aidilfitri dikerjakan sebanyak berapa rakaat?", "pilihan": ["2 Rakaat", "4 Rakaat", "3 Rakaat", "1 Rakaat"], "jawapan": 0},
            {"id": 47, "soalan": "Hari yang diharamkan berpuasa ialah pada 1 Syawal dan...", "pilihan": ["Hari Tasyrik (11, 12, 13 Zulhijjah)", "Hari Jumaat", "Hari Isnin", "Hari Arafah"], "jawapan": 0},
            {"id": 48, "soalan": "Puasa enam hari yang disunatkan selepas Ramadan ialah pada bulan...", "pilihan": ["Syawal", "Syaaban", "Zulkaedah", "Muharram"], "jawapan": 0},
            {"id": 49, "soalan": "Tawaf penghormatan terakhir sebelum meninggalkan kota Makkah dipanggil...", "pilihan": ["Tawaf Wada'", "Tawaf Ifadah", "Tawaf Qudum", "Tawaf Sunat"], "jawapan": 0},
            {"id": 50, "soalan": "Ibadah Umrah boleh dikerjakan pada...", "pilihan": ["Bila-bila masa sepanjang tahun", "Bulan Zulhijjah sahaja", "Bulan Ramadan sahaja", "Hari Raya sahaja"], "jawapan": 0},
            {"id": 51, "soalan": "Petugas yang dilantik kerajaan untuk memungut dan mengagihkan zakat dipanggil...", "pilihan": ["Amil", "Muallaf", "Gharimin", "Riqab"], "jawapan": 0},
            {"id": 52, "soalan": "Golongan 'Gharimin' yang berhak menerima zakat ialah orang yang...", "pilihan": ["Berhutang untuk keperluan asas", "Hamba yang ingin memerdekakan diri", "Musafir yang kehabisan bekalan", "Orang miskin"], "jawapan": 0},
            {"id": 53, "soalan": "Antara berikut, binatang yang WAJIB dikeluarkan zakat ternakan ialah...", "pilihan": ["Lembu dan Kambing", "Kuda dan Ayam", "Itik dan Burung", "Ikan dan Udang"], "jawapan": 0},
            {"id": 54, "soalan": "Solat Jumaat diwajibkan ke atas lelaki Muslim secara...", "pilihan": ["Berjamaah", "Bersendirian", "Munfarid", "Sembunyi"], "jawapan": 0},
            {"id": 55, "soalan": "Syarat sah Solat Jumaat antaranya hendaklah didirikan sekurang-kurangnya berapa orang ahli jemaah (menurut mazhab Syafi'i)?", "pilihan": ["40 Orang", "12 Orang", "2 Orang", "100 Orang"], "jawapan": 0},
            {"id": 56, "soalan": "Bermalam di Muzdalifah dan Mina semasa ibadah haji dinamakan...", "pilihan": ["Mabit", "Wukuf", "Tawaf", "Sa'i"], "jawapan": 0},
            {"id": 57, "soalan": "Perbuatan menyapu debu tanah yang suci ke muka dan kedua-dua tangan sebagai ganti wuduk dipanggil...", "pilihan": ["Tayamum", "Istinja'", "Samak", "Sertu"], "jawapan": 0},
            {"id": 58, "soalan": "Tayamum dilakukan untuk menggantikan wuduk apabila...", "pilihan": ["Ketiadaan air / uzur sakit", "Saja nak cepat", "Malas guna air", "Cuaca terlalu panas"], "jawapan": 0},
            {"id": 59, "soalan": "Satu tayamum hanya sah digunakan untuk berapa solat fardu?", "pilihan": ["1 Solat Fardu sahaja", "2 Solat Fardu", "Sepanjang hari", "3 Solat Fardu"], "jawapan": 0},
            {"id": 60, "soalan": "Mengerjakan ibadah Umrah terlebih dahulu sebelum Haji dipanggil Haji...", "pilihan": ["Tamattu'", "Ifrad", "Qiran", "Mabrur"], "jawapan": 0},
            {"id": 61, "soalan": "Mengerjakan ibadah Haji sahaja tanpa Umrah dipanggil Haji...", "pilihan": ["Ifrad", "Tamattu'", "Qiran", "Badal"], "jawapan": 0},
            {"id": 62, "soalan": "Mengerjakan Haji dan Umrah secara serentak dipanggil Haji...", "pilihan": ["Qiran", "Ifrad", "Tamattu'", "Wada'"], "jawapan": 0},
            {"id": 63, "soalan": "Puasa ganti bagi hari-hari Ramadan yang ditinggalkan dipanggil...", "pilihan": ["Puasa Qada'", "Puasa Nazar", "Puasa Kaffarah", "Puasa Sunat"], "jawapan": 0},
            {"id": 64, "soalan": "Denda berupa makanan yang perlu dibayar kerana melepaskan puasa atas sebab tertentu dinamakan...", "pilihan": ["Fidyah", "Dam", "Zakat", "Sedekah"], "jawapan": 0},
            {"id": 65, "soalan": "Puasa yang dijanjikan berniat untuk dilakukan jika sesuatu hajat tercapai dipanggil...", "pilihan": ["Puasa Nazar", "Puasa Sunat", "Puasa Kaffarah", "Puasa Qada'"], "jawapan": 0},
            {"id": 66, "soalan": "Waktu mula berpuasa yang menandakan masuknya waktu imsak biasanya berapa minit sebelum Subuh?", "pilihan": ["10 minit", "30 minit", "1 jam", "5 minit"], "jawapan": 0},
            {"id": 67, "soalan": "Membayar zakat perniagaan dikira berdasarkan nilaian harta perniagaan yang cukup...", "pilihan": ["Nisab dan Haul", "Bilangan pekerja", "Untung bersih sahaja", "Jumlah kedai"], "jawapan": 0},
            {"id": 68, "soalan": "Zakat emas wajib dikeluarkan apabila simpanan emas yang tidak dipakai mencapai nisab...", "pilihan": ["85 Gram", "100 Gram", "50 Gram", "200 Gram"], "jawapan": 0},
            {"id": 69, "soalan": "Syarat sah Syahadah hendaklah difahami maknanya dan...", "pilihan": ["Diyakini dalam hati", "Diucap dengan lisan sahaja", "Ditulis di kertas", "Dihafal cepat"], "jawapan": 0},
            {"id": 70, "soalan": "Ibadah Haji merupakan rukun Islam yang wajib dilaksanakan oleh orang Islam yang mampu sekurang-kurangnya...", "pilihan": ["Sekali seumur hidup", "2 Kali", "5 Kali", "Setiap 5 tahun"], "jawapan": 0}
        ],
        "rukun_solat": [
            {"id": 1, "soalan": "Berapakah jumlah Rukun Solat?", "pilihan": ["12", "13", "14", "15"], "jawapan": 1},
            {"id": 2, "soalan": "Niat dalam solat dilakukan serentak semasa...", "pilihan": ["Takbiratul Ihram", "Membaca Al-Fatihah", "Rukuk", "Sujud"], "jawapan": 0},
            {"id": 3, "soalan": "Membaca Surah Al-Fatihah dalam solat hukumnya...", "pilihan": ["Rukun (Wajib)", "Sunat Ab'ad", "Sunat Hai'ah", "Harus"], "jawapan": 0},
            {"id": 4, "soalan": "Perbuatan berdiri tegak bagi yang mampu termasuk dalam rukun...", "pilihan": ["Rukun Fi'li", "Rukun Qawli", "Rukun Qalbi", "Rukun Sunat"], "jawapan": 0},
            {"id": 5, "soalan": "Membaca Bacaan Tahiyyat Akhir tergolong dalam rukun...", "pilihan": ["Rukun Qawli", "Rukun Fi'li", "Rukun Qalbi", "Rukun Syarat"], "jawapan": 0},
            {"id": 6, "soalan": "Niat dan Tertib dalam solat tergolong dalam rukun...", "pilihan": ["Rukun Qalbi", "Rukun Qawli", "Rukun Fi'li", "Rukun Isyari"], "jawapan": 0},
            {"id": 7, "soalan": "Berapakah anggota sujud yang wajib menyentuh lantai?", "pilihan": ["5 Anggota", "7 Anggota", "8 Anggota", "6 Anggota"], "jawapan": 1},
            {"id": 8, "soalan": "Bertenang seketika semasa rukuk, iktidal, dan sujud dipanggil...", "pilihan": ["Thuma'ninah", "Tawadhu'", "Tabarruk", "Tadarru'"], "jawapan": 0},
            {"id": 9, "soalan": "Membaca Selawat ke atas Nabi SAW dalam Tahiyyat Akhir hukumnya...", "pilihan": ["Rukun Solat", "Sunat Hai'ah", "Membatalkan Solat", "Harus"], "jawapan": 0},
            {"id": 10, "soalan": "Salam yang pertama dalam solat hukumnya...", "pilihan": ["Rukun (Wajib)", "Sunat Hai'ah", "Sunat Ab'ad", "Mubah"], "jawapan": 0},
            {"id": 11, "soalan": "Salam yang kedua dalam solat hukumnya...", "pilihan": ["Sunat", "Rukun", "Wajib", "Haram"], "jawapan": 0},
            {"id": 12, "soalan": "Duduk di antara dua sujud tergolong dalam rukun...", "pilihan": ["Rukun Fi'li", "Rukun Qawli", "Rukun Qalbi", "Rukun Syarat"], "jawapan": 0},
            {"id": 13, "soalan": "Duduk semasa membaca Tahiyyat Akhir dipanggil duduk...", "pilihan": ["Tawarruk", "Iftirasy", "Iq'a'", "Tarabbu'"], "jawapan": 0},
            {"id": 14, "soalan": "Duduk di antara dua sujud dan duduk Tahiyyat Awal dipanggil duduk...", "pilihan": ["Iftirasy", "Tawarruk", "Iq'a'", "Sadl"], "jawapan": 0},
            {"id": 15, "soalan": "Menyusun perbuatan solat mengikut urutan yang betul dinamakan...", "pilihan": ["Tertib", "Tawazun", "Muwalat", "Tartan"], "jawapan": 0},
            {"id": 16, "soalan": "Berikut adalah Rukun Qawli (bacaan) KECUALI...", "pilihan": ["Membaca Doa Qunut", "Takbiratul Ihram", "Membaca Al-Fatihah", "Membaca Tahiyyat Akhir"], "jawapan": 0},
            {"id": 17, "soalan": "Bangkit dari rukuk dan berdiri tegak dinamakan...", "pilihan": ["Iktidal", "Sujud", "Rukuk", "Duduk Iftirasy"], "jawapan": 0},
            {"id": 18, "soalan": "Anggota sujud di bawah adalah wajib disentuhkan ke tempat sujud KECUALI...", "pilihan": ["Siku", "Dahi", "Lutut", "Tapak tangan"], "jawapan": 0},
            {"id": 19, "soalan": "Apakah hukum tidak membaca Basmalah (Bismillah) bagi madzhab Syafi'i semasa Al-Fatihah dalam solat?", "pilihan": ["Tidak sah kerana Basmalah ayat pertama Al-Fatihah", "Sah solatnya", "Sunat sahaja", "Harus ditinggalkan"], "jawapan": 0},
            {"id": 20, "soalan": "Berapakah jumlah Rukun Qawli dalam solat?", "pilihan": ["5", "6", "7", "4"], "jawapan": 0},
            {"id": 21, "soalan": "Berapakah jumlah Rukun Fi'li dalam solat?", "pilihan": ["6", "7", "5", "8"], "jawapan": 0},
            {"id": 22, "soalan": "Berapakah jumlah Rukun Qalbi dalam solat?", "pilihan": ["2 (Niat & Tertib)", "3", "1", "4"], "jawapan": 0},
            {"id": 23, "soalan": "Lupa melakukan Rukun Solat menyebabkan...", "pilihan": ["Solat tidak sah melainkan diganti/diulangi", "Diampunkan terus", "Cukup dengan sujud sahwi tanpa ganti", "Solat jadi sunat"], "jawapan": 0},
            {"id": 24, "soalan": "Sujud yang dilakukan di hujung solat kerana terlupa sunat Ab'ad atau ragu bilangan rakaat dipanggil...", "pilihan": ["Sujud Sahwi", "Sujud Tilawah", "Sujud Syukur", "Sujud Sejadah"], "jawapan": 0},
            {"id": 25, "soalan": "Membongkokkan badan sehingga tapak tangan memegang lutut dipanggil...", "pilihan": ["Rukuk", "Iktidal", "Sujud", "Tawarruk"], "jawapan": 0},
            {"id": 26, "soalan": "Memalingkan muka ke kanan semasa mengucapkan salam pertama hukumnya...", "pilihan": ["Sunat (Mengucapkan salamnya yang rukun)", "Rukun", "Harus", "Makruh"], "jawapan": 0},
            {"id": 27, "soalan": "Apakah ucapan takbir semasa mula-mula mengangkat tangan masuk ke dalam solat?", "pilihan": ["Allahu Akbar", "Subhanallah", "Alhamdulillah", "La ilaha illallah"], "jawapan": 0},
            {"id": 28, "soalan": "Membaca surah pendek selepas Al-Fatihah hukumnya...", "pilihan": ["Sunat Hai'ah", "Rukun Solat", "Sunat Ab'ad", "Wajib"], "jawapan": 0},
            {"id": 29, "soalan": "Membaca Doa Iftitah tergolong dalam...", "pilihan": ["Sunat Hai'ah", "Rukun Qawli", "Sunat Ab'ad", "Syarat Sah"], "jawapan": 0},
            {"id": 30, "soalan": "Solat dimulakan dengan Takbiratul Ihram dan diakhiri dengan...", "pilihan": ["Salam", "Sujud", "Doa", "Dzikir"], "jawapan": 0},
            {"id": 31, "soalan": "Membaca Selawat ke atas keluarga Nabi dalam Tahiyyat Akhir hukumnya...", "pilihan": ["Sunat Ab'ad", "Rukun Solat", "Membatalkan solat", "Harus"], "jawapan": 0},
            {"id": 32, "soalan": "Membaca Surah selepas Al-Fatihah dilakukan pada rakaat...", "pilihan": ["Rakaat Pertama dan Kedua sahaja", "Semua rakaat", "Rakaat Terakhir sahaja", "Rakaat Ketiga sahaja"], "jawapan": 0},
            {"id": 33, "soalan": "Membaca bacaan 'Subhana Rabbiyal Azimi Wa Bihamdih' disunatkan semasa...", "pilihan": ["Rukuk", "Sujud", "Iktidal", "Duduk antara dua sujud"], "jawapan": 0},
            {"id": 34, "soalan": "Membaca 'Subhana Rabbiyal A'la Wa Bihamdih' disunatkan semasa...", "pilihan": ["Sujud", "Rukuk", "Iktidal", "Tahiyyat"], "jawapan": 0},
            {"id": 35, "soalan": "Sujud Sahwi dilakukan...", "pilihan": ["Sebelum atau selepas salam di hujung solat", "Di awal solat", "Semasa rukuk", "Selepas bangun dari solat"], "jawapan": 0},
            {"id": 36, "soalan": "Berapakah bilangan sujud dalam satu rakaat solat?", "pilihan": ["2 Kali Sujud", "1 Kali Sujud", "3 Kali Sujud", "4 Kali Sujud"], "jawapan": 0},
            {"id": 37, "soalan": "Mengangkat kedua-dua tangan semasa Takbiratul Ihram hukumnya...", "pilihan": ["Sunat Hai'ah", "Rukun Solat", "Wajib", "Syarat Sah"], "jawapan": 0},
            {"id": 38, "soalan": "Apakah hukum pergerakan berturut-turut sebanyak 3 kali yang besar dalam solat?", "pilihan": ["Membatalkan solat", "Sunat", "Harus", "Makruh"], "jawapan": 0},
            {"id": 39, "soalan": "Bercakap dengan sengaja walaupun satu perkataan yang faham maknanya...", "pilihan": ["Membatalkan solat", "Dimaafkan", "Sunat sujud sahwi", "Makruh"], "jawapan": 0},
            {"id": 40, "soalan": "Membuka aurat dengan sengaja semasa solat menjadikan solat...", "pilihan": ["Batal", "Sah tetapi makruh", "Sunat", "Harus"], "jawapan": 0},
            {"id": 41, "soalan": "Solat yang tidak didahului dengan wuduk atau tayamum hukumnya...", "pilihan": ["Tidak Sah", "Sah", "Makruh", "Harus"], "jawapan": 0},
            {"id": 42, "soalan": "Apakah kedudukan makmum lelaki seorang berada di sebelah imam?", "pilihan": ["Di sebelah kanan imam belakang sedikit", "Di sebelah kiri", "Di belakang 3 saf", "Di hadapan imam"], "jawapan": 0},
            {"id": 43, "soalan": "Syarat menjadi Imam hendaklah seorang yang...", "pilihan": ["Lebih baik bacaan Al-Quran & faham hukum solat", "Paling tua", "Paling kaya", "Paling tinggi"], "jawapan": 0},
            {"id": 44, "soalan": "Solat Gerhana Matahari dipanggil solat sunat...", "pilihan": ["Kusuf", "Khusuf", "Istisqa'", "Istikharah"], "jawapan": 0},
            {"id": 45, "soalan": "Solat Gerhana Bulan dipanggil solat sunat...", "pilihan": ["Khusuf", "Kusuf", "Dhuha", "Awwabin"], "jawapan": 0},
            {"id": 46, "soalan": "Solat sunat memohon hujan dipanggil solat sunat...", "pilihan": ["Istisqa'", "Istikharah", "Hajat", "Tahajjud"], "jawapan": 0},
            {"id": 47, "soalan": "Solat sunat untuk memohon petunjuk pilihan dipanggil...", "pilihan": ["Istikharah", "Hajat", "Tasbih", "Tarawih"], "jawapan": 0},
            {"id": 48, "soalan": "Arah Kiblat bagi umat Islam di seluruh dunia ialah menghadap ke...", "pilihan": ["Kaabah di Makkah", "Masjid Al-Aqsa", "Baitulmaqdis", "Madinah"], "jawapan": 0},
            {"id": 49, "soalan": "Niat diletakkan di dalam...", "pilihan": ["Hati", "Mulut sahaja", "Telinga", "Mata"], "jawapan": 0},
            {"id": 50, "soalan": "Lafaz 'Sami'Allahu Liman Hamidah' dibaca semasa...", "pilihan": ["Bangkit dari rukuk menuju iktidal", "Mahu sujud", "Semasa rukuk", "Semasa duduk antara dua sujud"], "jawapan": 0},
            {"id": 51, "soalan": "Membaca Doa Qunut pada iktidal rakaat kedua solat Subuh mengikut Mazhab Syafi'i tergolong dalam...", "pilihan": ["Sunat Ab'ad", "Rukun Qawli", "Sunat Hai'ah", "Syarat Sah"], "jawapan": 0},
            {"id": 52, "soalan": "Jika tertinggal Sunat Ab'ad (seperti Tahiyyat Awal), solatnya tetap sah tetapi disunatkan...", "pilihan": ["Sujud Sahwi", "Solat semula", "Sujud Syukur", "Membaca Istighfar"], "jawapan": 0},
            {"id": 53, "soalan": "Membaca Tahiyyat Awal tergolong dalam...", "pilihan": ["Sunat Ab'ad", "Rukun Solat", "Sunat Hai'ah", "Harus"], "jawapan": 0},
            {"id": 54, "soalan": "Membaca bacaan 'Rabbighfirli warhamni...' disunatkan semasa...", "pilihan": ["Duduk di antara dua sujud", "Sujud", "Rukuk", "Iktidal"], "jawapan": 0},
            {"id": 55, "soalan": "Membaca 'Amin' secara lantang selepas imam selesai Al-Fatihah hukumnya...", "pilihan": ["Sunat Hai'ah", "Rukun Solat", "Wajib", "Makruh"], "jawapan": 0},
            {"id": 56, "soalan": "Solat empat rakaat yang dipendekkan menjadi dua rakaat semasa musafir dipanggil Solat...", "pilihan": ["Qasar", "Jamak", "Witr", "Dhuha"], "jawapan": 0},
            {"id": 57, "soalan": "Mengkombinasikan dua solat fardu dalam satu waktu semasa musafir dipanggil Solat...", "pilihan": ["Jamak", "Qasar", "Tahajjud", "Hajat"], "jawapan": 0},
            {"id": 58, "soalan": "Menghimpunkan Solat Zohor dan Asar dalam waktu Zohor dipanggil Jamak...", "pilihan": ["Taqdim", "Takhir", "Qasar", "Muntaha"], "jawapan": 0},
            {"id": 59, "soalan": "Menghimpunkan Solat Maghrib dan Isyak dalam waktu Isyak dipanggil Jamak...", "pilihan": ["Takhir", "Taqdim", "Mu'ajjal", "Kamil"], "jawapan": 0},
            {"id": 60, "soalan": "Solat Fardu yang Boleh di-Qasarkan (dipendekkan rakaatnya) ialah...", "pilihan": ["Zohor, Asar, dan Isyak", "Maghrib dan Subuh", "Subuh sahaja", "Semua solat fardu"], "jawapan": 0},
            {"id": 61, "soalan": "Syarat sah solat antaranya ialah suci daripada hadas kecil dan besar serta suci daripada...", "pilihan": ["Najis pada badan, pakaian, dan tempat", "Hutang", "Masa lalu", "Semua dosa"], "jawapan": 0},
            {"id": 62, "soalan": "Menutup aurat merupakan antara...", "pilihan": ["Syarat Sah Solat", "Rukun Solat", "Sunat Solat", "Perkara Makruh"], "jawapan": 0},
            {"id": 63, "soalan": "Aurat lelaki di dalam solat ialah di antara...", "pilihan": ["Pusat hingga lutut", "Dada hingga buku lali", "Bahu hingga lutut", "Seluruh badan"], "jawapan": 0},
            {"id": 64, "soalan": "Aurat wanita di dalam solat ialah seluruh badan KECUALI...", "pilihan": ["Muka dan kedua-dua tapak tangan", "Rambut dan kaki", "Muka dan leher", "Tapak tangan sahaja"], "jawapan": 0},
            {"id": 65, "soalan": "Melihat ke arah langit/atas semasa sedang solat hukumnya...", "pilihan": ["Makruh", "Harus", "Sunat", "Membatalkan solat"], "jawapan": 0},
            {"id": 66, "soalan": "Mencekak pinggang semasa bersolat hukumnya...", "pilihan": ["Makruh", "Batal", "Sunat", "Wajib"], "jawapan": 0},
            {"id": 67, "soalan": "Solat Jenazah mengandungi berapa kali takbir?", "pilihan": ["4 Kali Takbir", "2 Kali Takbir", "5 Kali Takbir", "7 Kali Takbir"], "jawapan": 0},
            {"id": 68, "soalan": "Solat Jenazah dilakukan tanpa perbuatan...", "pilihan": ["Rukuk dan Sujud", "Takbir", "Membaca Al-Fatihah", "Salam"], "jawapan": 0},
            {"id": 69, "soalan": "Membaca Selawat ke atas Nabi dalam Solat Jenazah dilakukan selepas...", "pilihan": ["Takbir Kedua", "Takbir Pertama", "Takbir Ketiga", "Takbir Keempat"], "jawapan": 0},
            {"id": 70, "soalan": "Mendoakan mayat dalam Solat Jenazah dilakukan khusus selepas...", "pilihan": ["Takbir Ketiga", "Takbir Pertama", "Takbir Kedua", "Takbir Keempat"], "jawapan": 0}
        ],
        "rukun_wuduk": [
            {"id": 1, "soalan": "Berapakah bilangan Rukun Wuduk?", "pilihan": ["4", "5", "6", "8"], "jawapan": 2},
            {"id": 2, "soalan": "Rukun wuduk yang pertama ialah...", "pilihan": ["Niat", "Membasuh Muka", "Membasuh Tangan", "Membaca Bismillah"], "jawapan": 0},
            {"id": 3, "soalan": "Batas membasuh muka adalah dari...", "pilihan": ["Tempat tumbuh rambut kepala hingga bawah dagu", "Dahi hingga mulut sahaja", "Telinga kanan ke telinga kiri sahaja", "Hidung hingga dagu"], "jawapan": 0},
            {"id": 4, "soalan": "Membasuh kedua-dua tangan semasa berwuduk hendaklah sampai ke...", "pilihan": ["Pergelangan tangan", "Siku", "Bahu", "Jari-jemari sahaja"], "jawapan": 1},
            {"id": 5, "soalan": "Menyapu sebahagian kepala termasuk dalam...", "pilihan": ["Rukun Wuduk", "Sunat Wuduk", "Syarat Wuduk", "Perkara membatalkan wuduk"], "jawapan": 0},
            {"id": 6, "soalan": "Membasuh kedua-dua kaki dalam wuduk hendaklah meliputi hingga ke...", "pilihan": ["Buku lali", "Lutut", "Paha", "Jari kaki sahaja"], "jawapan": 0},
            {"id": 7, "soalan": "Melakukan amalan wuduk mengikut urutan dipanggil...", "pilihan": ["Tertib", "Muwalat", "Niat", "Istinja'"], "jawapan": 0},
            {"id": 8, "soalan": "Berikut adalah perkara SUNAT dalam wuduk KECUALI...", "pilihan": ["Membasuh muka", "Membaca Bismillah", "Berkumur-kumur", "Memasukkan air ke dalam hidung"], "jawapan": 0},
            {"id": 9, "soalan": "Membasuh telinga dalam berwuduk hukumnya adalah...", "pilihan": ["Sunat", "Rukun", "Wajib", "Harus"], "jawapan": 0},
            {"id": 10, "soalan": "Membasuh setiap anggota wuduk sebanyak 3 kali hukumnya...", "pilihan": ["Sunat", "Rukun", "Wajib", "Makruh"], "jawapan": 0},
            {"id": 11, "soalan": "Apakah hukum mengambil wuduk menggunakan air mutanajjis (air terkena najis)?", "pilihan": ["Tidak sah", "Sah", "Makruh", "Harus"], "jawapan": 0},
            {"id": 12, "soalan": "Keluar sesuatu dari jalan hadapan (qubul) atau belakang (dubur) hukumnya...", "pilihan": ["Membatalkan wuduk", "Sunat wuduk semula", "Tidak merosakkan wuduk", "Harus"], "jawapan": 0},
            {"id": 13, "soalan": "Tidur yang bagaimanakah TIDAK membatalkan wuduk?", "pilihan": ["Tidur tetap punggungnya di atas lantai", "Tidur terlentang", "Tidur miring", "Tidur nyenyak bersandar"], "jawapan": 0},
            {"id": 14, "soalan": "Hilang ingatan disebabkan gila, pengsan, atau mabuk hukumnya...", "pilihan": ["Membatalkan wuduk", "Tidak membatalkan wuduk", "Sunat dibasuh muka sahaja", "Harus"], "jawapan": 0},
            {"id": 15, "soalan": "Bersentuhan kulit antara lelaki dan perempuan ajnabi tanpa lapik (mengikut Madzhab Syafi'i)...", "pilihan": ["Membatalkan wuduk", "Tidak membatalkan wuduk", "Harus", "Sunat diulangi"], "jawapan": 0},
            {"id": 16, "soalan": "Air yang suci dan boleh digunakan untuk bersuci dipanggil...", "pilihan": ["Air Mutlaq", "Air Musta'mal", "Air Musyammas", "Air Mutanajjis"], "jawapan": 0},
            {"id": 17, "soalan": "Air yang kurang dari 2 kolah dan telah digunakan untuk basuhan wajib dipanggil...", "pilihan": ["Air Musta'mal", "Air Mutlaq", "Air Musyammas", "Air Najis"], "jawapan": 0},
            {"id": 18, "soalan": "Air yang dipanaskan di bawah terik matahari dalam bekas logam yang boleh berkarat dipanggil...", "pilihan": ["Air Musyammas", "Air Musta'mal", "Air Mutlaq", "Air Lumpur"], "jawapan": 0},
            {"id": 19, "soalan": "Berapakah kadar sukatan anggaran air dua kolah mengikut liter moden?", "pilihan": ["Sekitar 216 Liter", "Sekitar 50 Liter", "Sekitar 500 Liter", "Sekitar 1000 Liter"], "jawapan": 0},
            {"id": 20, "soalan": "Mendahulukan anggota kanan daripada anggota kiri semasa berwuduk hukumnya...", "pilihan": ["Sunat", "Rukun", "Wajib", "Makruh"], "jawapan": 0},
            {"id": 21, "soalan": "Menyapu air ke seluruh kepala (bukan sebahagian) hukumnya...", "pilihan": ["Sunat", "Rukun", "Membatalkan wuduk", "Harus"], "jawapan": 0},
            {"id": 22, "soalan": "Menyelit jari-jemari tangan dan kaki semasa berwuduk dipanggil...", "p```python
            {"id": 22, "soalan": "Menyelit jari-jemari tangan dan kaki semasa berwuduk dipanggil...", "pilihan": ["Takhlil", "Istinja'", "Tahallul", "Tathir"], "jawapan": 0},
            {"id": 23, "soalan": "Membasuh atau membersihkan dua jalan (qubul dan dubur) selepas membuang air dipanggil...", "pilihan": ["Istinja'", "Istisqa'", "Istikharah", "I'tikaf"], "jawapan": 0},
            {"id": 24, "soalan": "Bahan yang paling afdal dan utama digunakan untuk beristinja' ialah...", "pilihan": ["Air Mutlaq", "Batu", "Tisu", "Daun Kering"], "jawapan": 0},
            {"id": 25, "soalan": "Apakah hukum berwuduk dalam keadaan bertelanjang / tanpa pakaian?", "pilihan": ["Sah tetapi makruh", "Batal", "Harus tanpa makruh", "Sunat"], "jawapan": 0},
            {"id": 26, "soalan": "Menyapu air ke atas balutan luka di anggota wuduk dinamakan...", "pilihan": ["Masa' ala al-Jabirah", "Tayamum", "Samak", "Sertu"], "jawapan": 0},
            {"id": 27, "soalan": "Perbuatan mengelap kering anggota wuduk dengan tuala selepas berwuduk hukumnya...", "pilihan": ["Makruh (Kecuali ada hajat seperti sejuk)", "Sunat", "Membatalkan wuduk", "Wajib"], "jawapan": 0},
            {"id": 28, "soalan": "Meneliti dan memastikan tiada bahan menghalang air sampai ke kulit (seperti cat/penggilap kuku) tergolong dalam...", "pilihan": ["Syarat Sah Wuduk", "Rukun Wuduk", "Sunat Wuduk", "Perkara Makruh"], "jawapan": 0},
            {"id": 29, "soalan": "Membaca doa selepas selesai berwuduk hukumnya...", "pilihan": ["Sunat", "Rukun", "Wajib", "Membatalkan wuduk"], "jawapan": 0},
            {"id": 30, "soalan": "Menyapu air ke atas Khuffain (kasut kulit khusus) menggantikan basuhan kaki dipanggil...", "pilihan": ["Al-Mash 'ala al-Khuffain", "Tayamum", "Istinja'", "Jabirah"], "jawapan": 0},
            {"id": 31, "soalan": "Tempoh keharusan menyapu Khuffain bagi orang yang bermukim (tidak musafir) ialah...", "pilihan": ["Sehari semalam (24 jam)", "3 hari 3 malam", "Seminggu", "12 jam"], "jawapan": 0},
            {"id": 32, "soalan": "Tempoh keharusan menyapu Khuffain bagi musafir ialah...", "pilihan": ["3 hari 3 malam", "Sehari semalam", "2 hari 2 malam", "5 hari"], "jawapan": 0},
            {"id": 33, "soalan": "Rukun wuduk yang mengkehendaki niat dibaca serentak dengan...", "pilihan": ["Permulaan basuhan muka", "Membasuh tangan ke siku", "Berkumur-kumur", "Membasuh kaki"], "jawapan": 0},
            {"id": 34, "soalan": "Rukun Wuduk ke-5 ialah...", "pilihan": ["Membasuh kedua-dua kaki hingga buku lali", "Menyapu kepala", "Membasuh muka", "Tertib"], "jawapan": 0},
            {"id": 35, "soalan": "Niat wuduk di dalam hati dilafazkan contohnya: 'Sahaja aku mengangkat hadas kecil kerana Allah Taala'. Hadas kecil disucikan dengan...", "pilihan": ["Wuduk atau Tayamum", "Mandi Wajib sahaja", "Istinja' sahaja", "Basuh muka sahaja"], "jawapan": 0},
            {"id": 36, "soalan": "Memilih tempat yang suci dan menghadap kiblat semasa berwuduk hukumnya...", "pilihan": ["Sunat", "Rukun", "Wajib", "Harus"], "jawapan": 0},
            {"id": 37, "soalan": "Menghembus air keluar dari hidung selepas memasukkannya (Istinshaq) dipanggil...", "pilihan": ["Istinthar", "Istinja'", "Takhlil", "Istisqa'"], "jawapan": 0},
            {"id": 38, "soalan": "Membasuh janggut yang tebal sehingga ke pangkal kulit hukumnya...", "pilihan": ["Sunat (Cukup menyapu bahagian luar)", "Wajib", "Batal wuduk", "Harus"], "jawapan": 0},
            {"id": 39, "soalan": "Membasuh janggut yang nipis yang nampak kulit di bawahnya hukumnya...", "pilihan": ["Wajib menyampaikan air ke kulit", "Sunat sahaja", "Harus", "Makruh"], "jawapan": 0},
            {"id": 40, "soalan": "Membazir air semasa berwuduk hukumnya...", "pilihan": ["Makruh", "Haram", "Sunat", "Harus"], "jawapan": 0},
            {"id": 41, "soalan": "Mandi yang wajib dilakukan selepas berhadas besar (seperti haid/junub) dipanggil...", "pilihan": ["Mandi Wajib / Mandi Janabah", "Mandi Sunat Jumaat", "Mandi Wiladah", "Mandi Ihram"], "jawapan": 0},
            {"id": 42, "soalan": "Rukun Mandi Wajib ada dua iaitu Niat dan...", "pilihan": ["Meratakan air ke seluruh anggota badan dan rambut", "Membasuh kepala 3 kali", "Berwuduk", "Tertib"], "jawapan": 0},
            {"id": 43, "soalan": "Menyucikan najis mughallazah (anjing/babi) hendaklah dibasuh 7 kali dan salah satunya dengan...", "pilihan": ["Tanah yang suci (Sertu)", "Sabun", "Kapur", "Cuka"], "jawapan": 0},
            {"id": 44, "soalan": "Menyucikan pakaian yang terkena najis babi/anjing dinamakan...", "pilihan": ["Sertu", "Samak", "Tayamum", "Istinja'"], "jawapan": 0},
            {"id": 45, "soalan": "Menyucikan kulit haiwan yang disembelih atau bangkai (selain anjing/babi) dinamakan...", "pilihan": ["Samak", "Sertu", "Tahallul", "Tathir"], "jawapan": 0},
            {"id": 46, "soalan": "Najis ringan seperti air kencing bayi lelaki bawah 2 tahun yang hanya minum susu ibu dipanggil...", "pilihan": ["Najis Mukhaffafah", "Najis Mutawassitah", "Najis Mughallazah", "Najis Hukmiyah"], "jawapan": 0},
            {"id": 47, "soalan": "Cara menyucikan Najis Mukhaffafah ialah dengan...", "pilihan": ["Percikkan air mutlaq ke tempat najis", "Basuh 7 kali dengan tanah", "Basuh sehingga hilang bau, warna dan rasa", "Lap dengan kain kering"], "jawapan": 0},
            {"id": 48, "soalan": "Najis pertengahan seperti darah, muntah, dan tahi dipanggil...", "pilihan": ["Najis Mutawassitah", "Najis Mukhaffafah", "Najis Mughallazah", "Najis 'Ainiyah"], "jawapan": 0},
            {"id": 49, "soalan": "Cara menyucikan Najis Mutawassitah ialah dengan membasuhnya menggunakan air sehingga hilang...", "pilihan": ["Bau, warna, dan rasa", "Bentuk sahaja", "Bau sahaja", "Warna sahaja"], "jawapan": 0},
            {"id": 50, "soalan": "Najis berat seperti anjing dan babi serta keturunannya dipanggil...", "pilihan": ["Najis Mughallazah", "Najis Mutawassitah", "Najis Mukhaffafah", "Najis Hukmiyah"], "jawapan": 0},
            {"id": 51, "soalan": "Hadas terbahagi kepada dua iaitu Hadas Kecil dan...", "pilihan": ["Hadas Besar", "Hadas Sedang", "Hadas Berat", "Hadas Ringan"], "jawapan": 0},
            {"id": 52, "soalan": "Hadas kecil disucikan dengan wuduk, manakala Hadas Besar disucikan dengan...", "pilihan": ["Mandi Wajib", "Wuduk 3 kali", "Istinja'", "Samak"], "jawapan": 0},
            {"id": 53, "soalan": "Berikut adalah sebab-sebab yang mewajibkan mandi wajib KECUALI...", "pilihan": ["Buang air kecil", "Keluar mani", "Bersetubuh (Jima')", "Selesai haid dan nifas"], "jawapan": 0},
            {"id": 54, "soalan": "Darah yang keluar dari rahim wanita selepas melahirkan anak dipanggil...", "pilihan": ["Darah Nifas", "Darah Haid", "Darah Istihadah", "Darah Wiladah"], "jawapan": 0},
            {"id": 55, "soalan": "Darah penyakit yang keluar luar biasa dari rahim wanita dinamakan...", "pilihan": ["Darah Istihadah", "Darah Haid", "Darah Nifas", "Darah Wiladah"], "jawapan": 0},
            {"id": 56, "soalan": "Wanita yang keluar Darah Istihadah wajib...", "pilihan": ["Tetap bersolat dan berpuasa selepas bersuci", "Dilarang bersolat", "Dilarang berpuasa", "Mandi wajib setiap waktu"], "jawapan": 0},
            {"id": 57, "soalan": "Tempoh maksimum kebiasaan darah Haid mengikut Mazhab Syafi'i ialah...", "pilihan": ["15 Hari 15 Malam", "7 Hari 7 Malam", "10 Hari", "40 Hari"], "jawapan": 0},
            {"id": 58, "soalan": "Tempoh maksimum darah Nifas bagi wanita selepas bersalin ialah...", "pilihan": ["60 Hari", "40 Hari", "30 Hari", "15 Hari"], "jawapan": 0},
            {"id": 59, "soalan": "Apakah hukum membaca Al-Quran bagi orang yang berada dalam keadaan janabah/berhadas besar?", "pilihan": ["Haram (kecuali niat zikir/doa)", "Harus", "Sunat", "Makruh"], "jawapan": 0},
            {"id": 60, "soalan": "Pegang atau menyentuh mushaf Al-Quran tanpa wuduk hukumnya...", "pilihan": ["Haram", "Makruh", "Harus", "Sunat"], "jawapan": 0},
            {"id": 61, "soalan": "Syarat sah wuduk antaranya hendaklah menggunakan air yang...", "pilihan": ["Suci lagi menyucikan (Air Mutlaq)", "Suci tetapi tidak menyucikan", "Berwarna jernih sahaja", "Air suam sahaja"], "jawapan": 0},
            {"id": 62, "soalan": "Air teh, air kopi, dan air sirap tergolong dalam jenis...", "pilihan": ["Air Suci tetapi tidak menyucikan", "Air Mutlaq", "Air Mutanajjis", "Air Musyammas"], "jawapan": 0},
            {"id": 63, "soalan": "Bolehkah mengambil wuduk menggunakan air teh atau kopi?", "pilihan": ["Tidak boleh", "Boleh", "Makruh", "Harus jika darurat"], "jawapan": 0},
            {"id": 64, "soalan": "Air embun, air salji, dan air hujan tergolong dalam jenis...", "pilihan": ["Air Mutlaq", "Air Musta'mal", "Air Mutanajjis", "Air Musyammas"], "jawapan": 0},
            {"id": 65, "soalan": "Air laut hukumnya...", "pilihan": ["Suci dan menyucikan (Boleh buat berwuduk)", "Harus untuk minum sahaja", "Najis", "Makruh"], "jawapan": 0},
            {"id": 66, "soalan": "Membaca Bismillah di awal wuduk tergolong dalam...", "pilihan": ["Sunat Wuduk", "Rukun Wuduk", "Syarat Sah Wuduk", "Perkara Membatalkan Wuduk"], "jawapan": 0},
            {"id": 67, "soalan": "Menyapu air ke telinga dilakukan dengan menggunakan air yang...", "pilihan": ["Baharu (Bukan air lebihan sapuan kepala)", "Bekas membasuh kaki", "Air sabun", "Air teh"], "jawapan": 0},
            {"id": 68, "soalan": "Perbuatan berturut-turut membasuh anggota wuduk tanpa selang masa yang lama dinamakan...", "pilihan": ["Muwalat", "Tertib", "Takhlil", "Istinja'"], "jawapan": 0},
            {"id": 69, "soalan": "Menyentuh kemaluan sendiri atau orang lain dengan tapak tangan tanpa lapik...", "pilihan": ["Membatalkan wuduk", "Tidak membatalkan wuduk", "Sunat dibasuh tangan sahaja", "Makruh"], "jawapan": 0},
            {"id": 70, "soalan": "Rukun terakhir dalam Rukun Wuduk ialah...", "pilihan": ["Tertib", "Membasuh Kaki", "Menyapu Kepala", "Niat"], "jawapan": 0}
        ],
        "rukun_nikah": [
            {"id": 1, "soalan": "Berapakah jumlah Rukun Nikah?", "pilihan": ["4", "5", "6", "7"], "jawapan": 1},
            {"id": 2, "soalan": "Berikut merupakan Rukun Nikah KECUALI...", "pilihan": ["Hantaran / Mas Kahwin", "Pengantin Lelaki", "Pengantin Perempuan", "Wali"], "jawapan": 0},
            {"id": 3, "soalan": "Lafaz penyerahan dari pihak wali dan penerimaan dari pihak lelaki dinamakan...", "pilihan": ["Ijab dan Kabul", "Khitbah", "Walimatulurus", "Mahar"], "jawapan": 0},
            {"id": 4, "soalan": "Berapakah bilangan saksi lelaki yang wajib ada dalam majlis akad nikah?", "pilihan": ["2 Orang Saksi", "1 Orang Saksi", "3 Orang Saksi", "4 Orang Saksi"], "jawapan": 0},
            {"id": 5, "soalan": "Pemberian wajib daripada suami kepada isteri disebabkan ikatan perkahwinan dinamakan...", "pilihan": ["Mahar / Mas Kahwin", "Hantaran", "Sedekah", "Hadiah"], "jawapan": 0},
            {"id": 6, "soalan": "Wali utama bagi seseorang wanita (bapa kandung) dinamakan...", "pilihan": ["Wali Nasab / Wali Aqrab", "Wali Hakim", "Wali Raja", "Wali Ab'ad"], "jawapan": 0},
            {"id": 7, "soalan": "Siapakah yang berhak menjadi Wali Mujbir (berkuasa mengahwinkan anak gadis)?", "pilihan": ["Bapa atau Datuk sebelah bapa", "Abang kandung", "Bapa saudara", "Ibu kandung"], "jawapan": 0},
            {"id": 8, "soalan": "Wali yang dilantik oleh pihak berkuasa agama apabila tiada wali nasab dipanggil...", "pilihan": ["Wali Hakim / Wali Raja", "Wali Mujbir", "Wali Ab'ad", "Wali Aqrab"], "jawapan": 0},
            {"id": 9, "soalan": "Apakah hukum perkahwinan tanpa kehadiran wali bagi pengantin perempuan?", "pilihan": ["Tidak Sah", "Sah", "Makruh", "Harus"], "jawapan": 0},
            {"id": 10, "soalan": "Syarat saksi nikah hendaklah beragama Islam, baligh, berakal, dan...", "pilihan": ["Lelaki dan Adil", "Perempuan sahaja", "Kaya", "Saudara mara sahaja"], "jawapan": 0},
            {"id": 11, "soalan": "Lafaz 'Aku nikahkan dikau dengan anakku...' dinamakan lafaz...", "pilihan": ["Ijab", "Kabul", "Taklik", "Khitbah"], "jawapan": 0},
            {"id": 12, "soalan": "Lafaz 'Aku terima nikahnya...' oleh pengantin lelaki dinamakan lafaz...", "pilihan": ["Kabul", "Ijab", "Fasakh", "Khuluk"], "jawapan": 0},
            {"id": 13, "soalan": "Pinangan atau lamaran sebelum perkahwinan dinamakan...", "pilihan": ["Khitbah", "Walimah", "Rujuk", "Talak"], "jawapan": 0},
            {"id": 14, "soalan": "Kenduri perkahwinan yang disunatkan dalam Islam dinamakan...", "pilihan": ["Walimatulurus", "Akikah", "Sadaqah", "Tahlil"], "jawapan": 0},
            {"id": 15, "soalan": "Wanita yang haram dikahwini selamanya dinamakan...", "pilihan": ["Mahram", "Ajnabi", "Muallaf", "Bioloji"], "jawapan": 0},
            {"id": 16, "soalan": "Ibu kandung, anak perempuan, dan saudara perempuan tergolong dalam...", "pilihan": ["Mahram Muabbad (Haram selamanya)", "Ajnabi", "Mahram Muaqqat", "Bukan mahram"], "jawapan": 0},
            {"id": 17, "soalan": "Adik ipar perempuan merupakan contoh Mahram Muaqqat yang bermaksud...", "pilihan": ["Haram dikahwini sementara (semasa isteri masih sah)", "Haram selamanya", "Boleh dikahwini bila-bila", "Halal digabung sekali"], "jawapan": 0},
            {"id": 18, "soalan": "Penceraian yang dilafazkan suami kepada isteri dinamakan...", "pilihan": ["Talak", "Fasakh", "Khuluk", "Lian"], "jawapan": 0},
            {"id": 19, "soalan": "Pembubaran perkahwinan melalui keputusan mahkamah atas sebab tertentu dipanggil...", "pilihan": ["Fasakh", "Talak", "Khuluk", "Ila'"], "jawapan": 0},
            {"id": 20, "soalan": "Penceraian atas tebus talak oleh isteri dengan membayar ganti rugi kepada suami dipanggil...", "pilihan": ["Khuluk", "Fasakh", "Lian", "Zihar"], "jawapan": 0},
            {"id": 21, "soalan": "Tempoh larangan berkahwin bagi wanita selepas bercerai atau kematian suami dipanggil...", "pilihan": ["Iddah", "Ihram", "Isti'zah", "Rujuk"], "jawapan": 0},
            {"id": 22, "soalan": "Tempoh iddah bagi wanita kematian suami (tidak hamil) ialah...", "pilihan": ["4 Bulan 10 Hari", "3 Bulan", "100 Hari", "3 Kali Suci"], "jawapan": 0},
            {"id": 23, "soalan": "Tempoh iddah bagi wanita bercerai hidup yang ada haid (tidak hamil) ialah...", "pilihan": ["3 Kali Suci (Quru')", "4 Bulan 10 Hari", "1 Bulan", "100 Hari"], "jawapan": 0},
            {"id": 24, "soalan": "Tempoh iddah bagi wanita hamil yang bercerai atau kematian suami ialah sehingga...", "pilihan": ["Melahirkan anak", "4 Bulan 10 Hari", "3 Bulan", "2 Tahun"], "jawapan": 0},
            {"id": 25, "soalan": "Mengembalikan ikatan perkahwinan dalam tempoh iddah talak raj'i tanpa akad baharu dipanggil...", "pilihan": ["Rujuk", "Nikah semula", "Fasakh", "Ijab"], "jawapan": 0},
            {"id": 26, "soalan": "Talak satu dan talak dua yang masih membolehkan suami merujuk isteri dalam iddah dipanggil...", "pilihan": ["Talak Raj'i", "Talak Ba'in Kubra", "Talak Ba'in Sughra", "Talak Taklik"], "jawapan": 0},
            {"id": 27, "soalan": "Talak tiga yang mengharamkan suami merujuk semula isteri melainkan selepas isteri berkahwin dengan lelaki lain dipanggil...", "pilihan": ["Talak Ba'in Kubra", "Talak Raj'i", "Talak Sunnah", "Talak Bid'i"], "jawapan": 0},
            {"id": 28, "soalan": "Perbuatan suami menyamakan belakang isterinya dengan ibunya dinamakan...", "pilihan": ["Zihar", "Lian", "Ila'", "Khuluk"], "jawapan": 0},
            {"id": 29, "soalan": "Sumpah suami menuduh isteri berzina tanpa 4 orang saksi dipanggil...", "pilihan": ["Lian", "Zihar", "Ila'", "Taklik"], "jawapan": 0},
            {"id": 30, "soalan": "Sumpah suami tidak akan menyetubuhi isterinya dalam tempoh lebih 4 bulan dipanggil...", "pilihan": ["Ila'", "Zihar", "Lian", "Khuluk"], "jawapan": 0},
            {"id": 31, "soalan": "Syarat pengantin lelaki antaranya mestilah beragama Islam, baligh, berakal, dan...", "pilihan": ["Bukan mahram kepada calon isteri & pilihan sendiri", "Kaya dan berpangkat", "Mempunyai rumah sendiri", "Persetujuan ibu bapa sahaja"], "jawapan": 0},
            {"id": 32, "soalan": "Apakah hukum wali berkahwin dengan perempuan di bawah jagaannya jika tiada halangan?", "pilihan": ["Harus (dengan syarat bukan mahram)", "Haram", "Wajib", "Makruh"], "jawapan": 0},
            {"id": 33, "soalan": "Susunan wali nasab yang paling berhak selepas bapa ialah...", "pilihan": ["Datuk sebelah bapa ke atas", "Saudara lelaki seibu sebapa", "Bapa saudara", "Anak lelaki"], "jawapan": 0},
            {"id": 34, "soalan": "Sekiranya bapa enggan menjadi wali tanpa alasan yang sah mengikut syarak, wali tersebut dipanggil...", "pilihan": ["Wali 'Adil / Wali Enggan", "Wali Ab'ad", "Wali Mujbir", "Wali Fasik"], "jawapan": 0},
            {"id": 35, "soalan": "Hak perkahwinan bagi wali 'adil (enggan) akan berpindah kepada...", "pilihan": ["Wali Hakim", "Ibu pengantin", "Wali Ab'ad", "Tok Cadi sahaja"], "jawapan": 0},
            {"id": 36, "soalan": "Mahar yang ditentukan jumlah dan jenisnya semasa akad nikah dipanggil...", "pilihan": ["Mahar Musamma", "Mahar Misil", "Mahar Mut'ah", "Mahar Hantaran"], "jawapan": 0},
            {"id": 37, "soalan": "Mahar yang nilainya diukur mengikut kadar mas kahwin saudara perempuan pengantin dinamakan...", "pilihan": ["Mahar Misil", "Mahar Musamma", "Mahar Tunai", "Mahar Utang"], "jawapan": 0},
            {"id": 38, "soalan": "Pemberian saguhati daripada suami kepada isteri yang diceraikan tanpa sebab dipanggil...", "pilihan": ["Mut'ah", "Nafkah", "Mahar", "Hadiah"], "jawapan": 0},
            {"id": 39, "soalan": "Nafkah zahir yang wajib disediakan oleh suami untuk isteri meliputi...", "pilihan": ["Makanan, pakaian, dan tempat tinggal", "Kereta mewah sahaja", "Barang kemas sahaja", "Wang simpanan sahaja"], "jawapan": 0},
            {"id": 40, "soalan": "Perbuatan isteri menderhaka atau tidak mematuhi perintah suami yang sah dinamakan...", "pilihan": ["Nusyuz", "Khuluk", "Fasakh", "Zihar"], "jawapan": 0},
            {"id": 41, "soalan": "Isteri yang nusyuz akan kehilangan hak...", "pilihan": ["Nafkah zahir dan batin", "Hak jagaan anak selamanya", "Mas kahwin", "Gelaran isteri"], "jawapan": 0},
            {"id": 42, "soalan": "Hak menjaga dan mengasuh anak yang masih kecil selepas bercerai dipanggil...", "pilihan": ["Hadanah", "Nusyuz", "Fasakh", "Rujuk"], "jawapan": 0},
            {"id": 43, "soalan": "Orang yang paling berhak mendapat hak Hadanah (jagaan anak kecil) ialah...", "pilihan": ["Ibu kandung", "Bapa kandung", "Nenek sebelah bapa", "Bapa saudara"], "jawapan": 0},
            {"id": 44, "soalan": "Apakah hukum poligami (berkahwin lebih daripada satu sehingga empat isteri) dalam Islam?", "pilihan": ["Harus (dengan syarat adil)", "Wajib", "Haram", "Sunat mutlak"], "jawapan": 0},
            {"id": 45, "soalan": "Maksimum isteri yang boleh dihimpunkan oleh seorang lelaki Muslim dalam satu masa ialah...", "pilihan": ["4 Orang Isteri", "2 Orang Isteri", "3 Orang Isteri", "7 Orang Isteri"], "jawapan": 0},
            {"id": 46, "soalan": "Pernikahan yang diikat dengan tempoh masa tertentu (contoh: seminggu/sebulan) dinamakan...", "pilihan": ["Nikah Mut'ah (Haram)", "Nikah Sunnah", "Nikah Khuluk", "Nikah Shighar"], "jawapan": 0},
            {"id": 47, "soalan": "Apakah hukum Nikah Mut'ah (nikah kontrak) dalam Islam?", "pilihan": ["Haram dan tidak sah", "Harus", "Sunat", "Makruh"], "jawapan": 0},
            {"id": 48, "soalan": "Anak yang lahir hasil hubungan luar nikah dinamakan...", "pilihan": ["Anak Tak Saraf / Anak Zina", "Anak Angkat", "Anak Tiri", "Anak Susuan"], "jawapan": 0},
            {"id": 49, "soalan": "Anak tidak sah taraf TIDAK BOLEH dinisbahkan (bin/binti) kepada...", "pilihan": ["Bapa biologinya", "Ibu kandungnya", "Masyarakat", "Negara"], "jawapan": 0},
            {"id": 50, "soalan": "Apakah hukum bapa biologi menjadi wali nikah kepada anak perempuan tidak sah tarafnya?", "pilihan": ["Tidak Boleh (Wajib guna Wali Hakim)", "Boleh", "Sunat", "Harus"], "jawapan": 0},
            {"id": 51, "soalan": "Anak susuan menjadi mahram kepada ibu susuan apabila menyusu sekurang-kurangnya berapa kali kenyang?", "pilihan": ["5 Kali menyusu kenyang", "3 Kali menyusu", "1 Kali sahaja", "10 Kali"], "jawapan": 0},
            {"id": 52, "soalan": "Umur anak susuan yang dikira membentuk hukum mahram hendaklah di bawah...", "pilihan": ["2 Tahun", "5 Tahun", "1 Tahun", "7 Tahun"], "jawapan": 0},
            {"id": 53, "soalan": "Lafaz janji/syarat yang diucapkan suami selepas akad nikah yang boleh membatalkan perkahwinan jika dilanggar dipanggil...", "pilihan": ["Lafaz Taklik", "Ijab", "Kabul", "Rujuk"], "jawapan": 0},
            {"id": 54, "soalan": "Persetujuan nikah bagi janda hendaklah dinyatakan melalui...", "pilihan": ["Ucapan lisan yang jelas", "Diam sahaja", "Senyuman", "Isyarat mata"], "jawapan": 0},
            {"id": 55, "soalan": "Persetujuan nikah bagi anak gadis (perawan) boleh dinyatakan melalui...", "pilihan": ["Lisan atau diamnya (tanda malu)", "Surat rasmi sahaja", "Bercakap lantang sahaja", "Tepuk tangan"], "jawapan": 0},
            {"id": 56, "soalan": "Perempuan yang sedang dalam ihram haji atau umrah...", "pilihan": ["Dilarang bernikah atau dinikahkan", "Boleh bernikah seperti biasa", "Sunat bernikah", "Harus bernikah di Makkah"], "jawapan": 0},
            {"id": 57, "soalan": "Penyaksi nikah yang fasik (selalu melakukan dosa besar)...", "pilihan": ["Tidak sah menjadi saksi nikah", "Sah menjadi saksi", "Harus", "Mewajibkan hantaran tinggi"], "jawapan": 0},
            {"id": 58, "soalan": "Lafaz Ijab dan Kabul hendaklah diucapkan dalam...", "pilihan": ["Satu majlis (pasti bersambung)", "Dua hari berbeza", "Melalui surat pos", "Masa berasingan"], "jawapan": 0},
            {"id": 59, "soalan": "Pertunangan yang diputuskan oleh sebelah pihak tanpa sebab munasabah hukumnya...", "pilihan": ["Makruh dan dicela", "Haram mutlak", "Wajib bayar denda 10 kali ganda", "Batal iman"], "jawapan": 0},
            {"id": 60, "soalan": "Tunang orang lain HARAM dipinang mengikut hukum syarak jika...", "pilihan": ["Pinangan pertama belum dibatalkan/ditolak", "Sudah kaya", "Dapat keizinan kawan", "Pinangan dilakukan secara sembunyi"], "jawapan": 0},
            {"id": 61, "soalan": "Tujuan utama perkahwinan dalam Islam adalah untuk membina keluarga yang...", "pilihan": ["Sakinah, Mawaddah, dan Rahmah", "Kaya raya dan megah", "Popular", "Ditakuti musuh"], "jawapan": 0},
            {"id": 62, "soalan": "Seseorang lelaki yang tidak mampu menafkahkan isteri dan dikhuatiri menganiaya isteri, hukum berkahwin baginya ialah...", "pilihan": ["Haram", "Wajib", "Sunat", "Harus"], "jawapan": 0},
            {"id": 63, "soalan": "Lelaki yang mampu dari segi batin dan zahir serta takut terjebak dalam zina, hukum berkahwin baginya ialah...", "pilihan": ["Wajib", "Harus", "Makruh", "Sunat"], "jawapan": 0},
            {"id": 64, "soalan": "Hukum asal perkahwinan bagi orang yang tiada desakan dan mampu ialah...", "pilihan": ["Harus", "Wajib", "Sunat", "Makruh"], "jawapan": 0},
            {"id": 65, "soalan": "Siapakah yang menanggung semua perbelanjaan nafkah keluarga?", "pilihan": ["Suami", "Isteri", "Ibu bapa isteri", "Kerajaan"], "jawapan": 0},
            {"id": 66, "soalan": "Hukum membantu suami membuat kerja rumah bagi isteri adalah...", "pilihan": ["Sunat dan amalan terpuji", "Wajib mutlak", "Haram", "Batal nikah"], "jawapan": 0},
            {"id": 67, "soalan": "Talak yang diucapkan secara jelas seperti 'Aku ceraikan kau' dipanggil...", "pilihan": ["Talak Sarih", "Talak Kinayah", "Talak Taklik", "Talak Bad'i"], "jawapan": 0},
            {"id": 68, "soalan": "Talak yang menggunakan perkataan kiasan/sindiran dipanggil...", "pilihan": ["Talak Kinayah (Perlu Niat)", "Talak Sarih", "Talak Raj'i", "Talak Mutlaq"], "jawapan": 0},
            {"id": 69, "soalan": "Talak Kinayah memerlukan kepada...", "pilihan": ["Niat suami semasa melafazkan", "Dua orang saksi terus", "Bayaran mahar", "Persetujuan wali"], "jawapan": 0},
            {"id": 70, "soalan": "Talak yang dilafazkan semasa isteri dalam keadaan suci yang belum disetubuhi dipanggil...", "pilihan": ["Talak Sunni", "Talak Bid'i", "Talak Haram", "Talak Makruh"], "jawapan": 0}
        ]
    }
}

# =========================================================
# FUNGSI MEMPEROLEH SAMBUNGAN REDIS (DYNAMIC CONNECT)
# =========================================================
def get_redis_client():
    # Mengambil URL dari Environment Variable
    redis_url = (
        os.environ.get("kuizdb_REDIS_URL") or 
        os.environ.get("REDIS_URL") or
        os.environ.get("KV_URL")
    )
    
    if not redis_url:
        print("⚠️ TIADA REDIS_URL DIJUMPAI")
        return None

    try:
        # Cipta client sambungan setiap kali dipanggil jika perlu
        client = redis.Redis.from_url(
            redis_url, 
            decode_responses=True,
            socket_timeout=3,
            socket_connect_timeout=3
        )
        client.ping()
        return client
    except Exception as e:
        print("❌ AGENT REDIS ERROR:", str(e))
        return None

LOCAL_LEADERBOARD = []

# =========================================================
# API ENDPOINTS
# =========================================================
@app.route('/api/soalan', methods=['GET'])
def get_soalan():
    kategori = request.args.get('kategori')
    sub = request.args.get('sub')
    
    if kategori == 'rukun' and sub:
        questions = QUIZ_DATA.get('rukun', {}).get(sub, [])
    else:
        questions = QUIZ_DATA.get(kategori, [])
        
    return jsonify({"data": questions})

@app.route('/api/leaderboard', methods=['GET', 'POST'])
def handle_leaderboard():
    global LOCAL_LEADERBOARD
    LEADERBOARD_KEY = "global_leaderboard"
    
    # Buka sambungan ke Redis
    r_db = get_redis_client()

    if request.method == 'POST':
        data = request.json or {}
        nama = data.get("nama", "Anon").strip()[:15]
        skor = int(data.get("skor", 0))
        masa = int(data.get("masa", 0))
        kategori = data.get("kategori", "Umum")

        entry = {
            "nama": nama,
            "skor": skor,
            "masa": masa,
            "kategori": kategori
        }

        # 1. Simpan ke Redis Cloud jika sambungan wujud
        if r_db:
            try:
                composite_score = (skor * 1000) + (1000 - masa)
                # ZADD hantar data ke Sorted Set Redis
                r_db.zadd(LEADERBOARD_KEY, {json.dumps(entry): composite_score})
                return jsonify({"status": "success", "message": "Skor berjaya disimpan ke Redis Cloud!"})
            except Exception as e:
                print("Redis Save Error:", e)

        # 2. Fallback tempatan jika Redis bermasalah
        LOCAL_LEADERBOARD.append(entry)
        LOCAL_LEADERBOARD = sorted(LOCAL_LEADERBOARD, key=lambda x: (-x['skor'], x['masa']))[:10]

        return jsonify({"status": "success", "message": "Skor disimpan secara tempatan sementara!"})

    else:
        # GET: Ambil 10 teratas dari Redis Cloud
        if r_db:
            try:
                raw_list = r_db.zrevrange(LEADERBOARD_KEY, 0, 9)
                db_data = []
                for item in raw_list:
                    try:
                        db_data.append(json.loads(item))
                    except:
                        pass
                if db_data:
                    return jsonify({"data": db_data})
            except Exception as e:
                print("Redis Fetch Error:", e)

        return jsonify({"data": LOCAL_LEADERBOARD})

if __name__ == '__main__':
    app.run(debug=True, port=5000)