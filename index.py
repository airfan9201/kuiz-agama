# =========================================================
# TETAPAN REDIS / VERCEL DATABASE (AUTO-DETECT KEY)
# =========================================================
import redis
import os
import json
import re
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
            {"id": 1, "soalan": "Berapakah bilangan Rukun Iman?", "pilihan": ["7", "6", "10", "5"], "jawapan": 1},
            {"id": 2, "soalan": "Apakah Rukun Iman yang pertama?", "pilihan": ["Beriman kepada Hari Kiamat", "Beriman kepada Kitab", "Beriman kepada Malaikat", "Beriman kepada Allah"], "jawapan": 3},
            {"id": 3, "soalan": "Malaikat manakah yang bertugas membawa wahyu?", "pilihan": ["Malaikat Israfil", "Malaikat Izrail", "Malaikat Jibril", "Malaikat Mikail"], "jawapan": 2},
            {"id": 4, "soalan": "Kitab Al-Quran diturunkan kepada Nabi...", "pilihan": ["Nabi Isa A.S.", "Nabi Daud A.S.", "Nabi Musa A.S.", "Nabi Muhammad S.A.W."], "jawapan": 3},
            {"id": 5, "soalan": "Beriman kepada Qada' dan Qadar merupakan Rukun Iman yang ke-...", "pilihan": ["4", "5", "6", "3"], "jawapan": 2},
            {"id": 6, "soalan": "Malaikat yang bertugas mencatat amal baik ialah...", "pilihan": ["Atid", "Nakir", "Munkar", "Raqib"], "jawapan": 3},
            {"id": 7, "soalan": "Kitab Taurat diturunkan kepada Nabi...", "pilihan": ["Nabi Ibrahim A.S.", "Nabi Isa A.S.", "Nabi Musa A.S.", "Nabi Daud A.S."], "jawapan": 2},
            {"id": 8, "soalan": "Kitab Zabur diturunkan kepada Nabi...", "pilihan": ["Nabi Isa A.S.", "Nabi Adam A.S.", "Nabi Daud A.S.", "Nabi Musa A.S."], "jawapan": 2},
            {"id": 9, "soalan": "Kitab Injil diturunkan kepada Nabi...", "pilihan": ["Nabi Isa A.S.", "Nabi Yahya A.S.", "Nabi Musa A.S.", "Nabi Muhammad S.A.W."], "jawapan": 0},
            {"id": 10, "soalan": "Malaikat yang bertugas mencabut nyawa ialah...", "pilihan": ["Malaikat Malik", "Malaikat Ridwan", "Malaikat Izrail", "Malaikat Israfil"], "jawapan": 2},
            {"id": 11, "soalan": "Malaikat yang meniup sangkakala pada hari kiamat ialah...", "pilihan": ["Malaikat Jibril", "Malaikat Mikail", "Malaikat Ridwan", "Malaikat Israfil"], "jawapan": 3},
            {"id": 12, "soalan": "Malaikat peniup sangkakala, pembagi rezeki, dan penjaga syurga adalah contoh beriman kepada...", "pilihan": ["Qada' dan Qadar", "Kitab", "Rasul", "Malaikat"], "jawapan": 3},
            {"id": 13, "soalan": "Siapakah Nabi dan Rasul yang pertama?", "pilihan": ["Nabi Muhammad S.A.W.", "Nabi Nuh A.S.", "Nabi Adam A.S.", "Nabi Ibrahim A.S."], "jawapan": 2},
            {"id": 14, "soalan": "Berapakah bilangan Rasul yang wajib diketahui?", "pilihan": ["25", "313", "20", "10"], "jawapan": 0},
            {"id": 15, "soalan": "Gelaran 'Ulul Azmi' diberikan kepada Rasul yang...", "pilihan": ["Paling kaya", "Mempunyai ketabahan & kesabaran luar biasa", "Paling banyak mukjizat", "Paling panjang umur"], "jawapan": 1},
            {"id": 16, "soalan": "Berikut adalah Rasul Ulul Azmi KECUALI...", "pilihan": ["Nabi Musa A.S.", "Nabi Nuh A.S.", "Nabi Yunus A.S.", "Nabi Ibrahim A.S."], "jawapan": 2},
            {"id": 17, "soalan": "Percaya bahawa segala yang berlaku adalah ketentuan Allah dinamakan...", "pilihan": ["Tawakal", "Redha", "Ikhlas", "Qada' dan Qadar"], "jawapan": 3},
            {"id": 18, "soalan": "Malaikat yang bertugas menjaga pintu Syurga ialah...", "pilihan": ["Malaikat Malik", "Malaikat Raqib", "Malaikat Ridwan", "Malaikat Atid"], "jawapan": 2},
            {"id": 19, "soalan": "Malaikat yang bertugas menjaga pintu Neraka ialah...", "pilihan": ["Malaikat Nakir", "Malaikat Munkar", "Malaikat Ridwan", "Malaikat Malik"], "jawapan": 3},
            {"id": 20, "soalan": "Hari kebangkitan semula manusia dari kubur dikenali sebagai...", "pilihan": ["Yaumul Ba'ath", "Yaumul Mahsyar", "Yaumul Hisab", "Yaumul Mizan"], "jawapan": 0},
            {"id": 21, "soalan": "Malaikat yang bertugas menyoal mayat di dalam kubur ialah...", "pilihan": ["Munkar dan Nakir", "Jibril dan Mikail", "Malik dan Ridwan", "Raqib dan Atid"], "jawapan": 0},
            {"id": 22, "soalan": "Suhuf diturunkan kepada beberapa orang Nabi. Siapakah yang menerima Suhuf paling banyak?", "pilihan": ["Nabi Syith A.S.", "Nabi Idris A.S.", "Nabi Musa A.S.", "Nabi Ibrahim A.S."], "jawapan": 0},
            {"id": 23, "soalan": "Beriman kepada Kitab bermaksud meyakini bahawa...", "pilihan": ["Semua kitab lama masih boleh diamalkan", "Kitab suci hanya untuk orang Arab", "Al-Quran ciptaan manusia", "Allah menurunkan petunjuk melalui wahyu kepada para Rasul"], "jawapan": 3},
            {"id": 24, "soalan": "Apakah maksud Qada'?", "pilihan": ["Usaha manusia", "Doa manusia", "Ketentuan Allah sejak azali", "Pelaksanaan ketentuan Allah"], "jawapan": 2},
            {"id": 25, "soalan": "Apakah maksud Qadar?", "pilihan": ["Pasrah tanpa usaha", "Pelaksanaan ketentuan Allah mengikut kadar yang ditetapkan", "Ketetapan azali", "Keberhasilan cita-cita"], "jawapan": 1},
            {"id": 26, "soalan": "Timbangan amal kebaikan dan keburukan di akhirat dipanggil...", "pilihan": ["As-Sirat", "Al-Hisab", "Al-Mizan", "Al-Mahsyar"], "jawapan": 2},
            {"id": 27, "soalan": "Titian yang merentasi di atas neraka menuju ke syurga dinamakan...", "pilihan": ["Al-Mahsyar", "Al-Kautsar", "Al-Mizan", "As-Sirat"], "jawapan": 3},
            {"id": 28, "soalan": "Nabi yang mendapat gelaran 'Khalilullah' (Kekasih Allah) ialah...", "pilihan": ["Nabi Musa A.S.", "Nabi Muhammad S.A.W.", "Nabi Ibrahim A.S.", "Nabi Isa A.S."], "jawapan": 2},
            {"id": 29, "soalan": "Nabi yang mendapat gelaran 'Kalimullah' (yang berbicara dengan Allah) ialah...", "pilihan": ["Nabi Nuh A.S.", "Nabi Isa A.S.", "Nabi Musa A.S.", "Nabi Adam A.S."], "jawapan": 2},
            {"id": 30, "soalan": "Hukum beriman kepada semua Rukun Iman adalah...", "pilihan": ["Wajib", "Sunat", "Harus", "Makruh"], "jawapan": 0},
            {"id": 31, "soalan": "Siapakah Malaikat yang bertugas mengurus hujan dan rezeki?", "pilihan": ["Malaikat Israfil", "Malaikat Mikail", "Malaikat Izrail", "Malaikat Jibril"], "jawapan": 1},
            {"id": 32, "soalan": "Malaikat diciptakan daripada...", "pilihan": ["Cahaya (Nur)", "Angin", "Tanah", "Api (Nar)"], "jawapan": 0},
            {"id": 33, "soalan": "Jin dan Iblis diciptakan daripada...", "pilihan": ["Pucuk Api (Nar)", "Cahaya", "Tanah", "Air"], "jawapan": 0},
            {"id": 34, "soalan": "Manusia pertama yang diciptakan oleh Allah SWT ialah...", "pilihan": ["Nabi Muhammad SAW", "Nabi Nuh A.S.", "Nabi Adam A.S.", "Nabi Ibrahim A.S."], "jawapan": 2},
            {"id": 35, "soalan": "Nabi Isa A.S. dikurniakan kitaban suci bernama...", "pilihan": ["Taurat", "Zabur", "Injil", "Al-Quran"], "jawapan": 2},
            {"id": 36, "soalan": "Peristiwa perhimpunan seluruh manusia selepas dibangkitkan semula berlaku di...", "pilihan": ["Gua Hira'", "Padang Arafah", "Baitulmaqdis", "Padang Mahsyar"], "jawapan": 3},
            {"id": 37, "soalan": "Nabi yang membina Bahtera (Kapal Besar) untuk menyelamatkan pengikutnya dari banjir besar ialah...", "pilihan": ["Nabi Hud A.S.", "Nabi Nuh A.S.", "Nabi Saleh A.S.", "Nabi Yunus A.S."], "jawapan": 1},
            {"id": 38, "soalan": "Apakah hukum percaya kepada kewujudan Hari Kiamat?", "pilihan": ["Wajib", "Harus", "Sunat", "Makruh"], "jawapan": 0},
            {"id": 39, "soalan": "Mukjizat terbesar Nabi Muhammad SAW yang kekal hingga ke hari kiamat ialah...", "pilihan": ["Pembelahan Bulan", "Al-Quran", "Isra' Mi'raj", "Air keluar dari jemari"], "jawapan": 1},
            {"id": 40, "soalan": "Nabi yang diuji dengan penyakit kulit yang berat tetapi kekal bersabar ialah...", "pilihan": ["Nabi Harun A.S.", "Nabi Yusuf A.S.", "Nabi Yaakub A.S.", "Nabi Ayyub A.S."], "jawapan": 3},
            {"id": 41, "soalan": "Nabi yang pernah ditelan oleh ikan nun/paus ialah...", "pilihan": ["Nabi Yahya A.S.", "Nabi Ilyas A.S.", "Nabi Yunus A.S.", "Nabi Zakaria A.S."], "jawapan": 2},
            {"id": 42, "soalan": "Berapakah jumlah surah yang terdapat di dalam Al-Quran?", "pilihan": ["30 Surah", "110 Surah", "114 Surah", "66 Surah"], "jawapan": 2},
            {"id": 43, "soalan": "Perkara ghaib yang wajib dipercayai merangkumi perkara berikut KECUALI...", "pilihan": ["Siksa Kubur", "Syurga dan Neraka", "Malaikat", "Ramalan nasib tukang tilik"], "jawapan": 3},
            {"id": 44, "soalan": "Nabi yang mempunyai mukjizat boleh bercakap dengan haiwan dan mengawal angin ialah...", "pilihan": ["Nabi Musa A.S.", "Nabi Sulaiman A.S.", "Nabi Yusuf A.S.", "Nabi Daud A.S."], "jawapan": 1},
            {"id": 45, "soalan": "Sifat wajib bagi Allah 'Al-Alim' bermaksud Allah Maha...", "pilihan": ["Melihat", "Mengetahui", "Berkuasa", "Mendengar"], "jawapan": 1},
            {"id": 46, "soalan": "Sifat wajib bagi Rasul 'Siddiq' bermaksud...", "pilihan": ["Bijaksana", "Bercakap benar", "Amanah", "Menyampaikan"], "jawapan": 1},
            {"id": 47, "soalan": "Sifat wajib bagi Rasul 'Amanah' bermaksud...", "pilihan": ["Penyabar", "Bijaksana", "Pendiam", "Jujur / Boleh dipercayai"], "jawapan": 3},
            {"id": 48, "soalan": "Sifat 'Fatanah' bagi seseorang Rasul bermaksud...", "pilihan": ["Jujur", "Tebal sabar", "Bijaksana", "Kuat tubuh"], "jawapan": 2},
            {"id": 49, "soalan": "Nabi yang dikurniakan ketampanan rupa paras yang luar biasa ialah...", "pilihan": ["Nabi Adam A.S.", "Nabi Yusuf A.S.", "Nabi Musa A.S.", "Nabi Isa A.S."], "jawapan": 1},
            {"id": 50, "soalan": "Syurga tempat ganjaran bagi orang beriman dinamakan...", "pilihan": ["Jahannam", "Barzakh", "Mahsyar", "Jannah"], "jawapan": 3},
            {"id": 51, "soalan": "Sifat wajib bagi Rasul 'Tabligh' bermaksud...", "pilihan": ["Amanah", "Bercakap benar", "Bijaksana", "Menyampaikan wahyu"], "jawapan": 3},
            {"id": 52, "soalan": "Malaikat yang bertugas mencatat amal keburukan ialah...", "pilihan": ["Raqib", "Nakir", "Munkar", "Atid"], "jawapan": 3},
            {"id": 53, "soalan": "Mustahil bagi Allah bersifat 'Jahlun' yang bermaksud...", "pilihan": ["Bodoh / Jahil", "Tuli", "Mati", "Lemah"], "jawapan": 0},
            {"id": 54, "soalan": "Alam kehidupan di dalam kubur sementara menunggu hari kiamat dipanggil...", "pilihan": ["Alam Barzakh", "Alam Rahim", "Alam Malakut", "Padang Mahsyar"], "jawapan": 0},
            {"id": 55, "soalan": "Suhuf merupakan lembaran wahyu yang tidak dibukukan. Nabi yang menerima suhuf ialah...", "pilihan": ["Nabi Nuh A.S.", "Nabi Ibrahim A.S.", "Nabi Isa A.S.", "Nabi Muhammad SAW"], "jawapan": 1},
            {"id": 56, "soalan": "Qada' yang boleh berubah melalui doa dan usaha manusia dinamakan...", "pilihan": ["Qada' Muallaq", "Qada' Qadim", "Qada' Mubram", "Qada' Mutlaq"], "jawapan": 0},
            {"id": 57, "soalan": "Qada' yang pasti berlaku dan tidak boleh diubah seperti kematian dinamakan...", "pilihan": ["Qada' Mubram", "Qada' Muallaq", "Qada' Harfi", "Qada' Aradi"], "jawapan": 0},
            {"id": 58, "soalan": "Berapakah sifat wajib bagi Allah SWT yang asas perlu diketahui?", "pilihan": ["10 Sifat", "99 Sifat", "13 Sifat", "20 Sifat"], "jawapan": 3},
            {"id": 59, "soalan": "Nabi yang boleh menghidupkan orang mati atas izin Allah ialah...", "pilihan": ["Nabi Yahya A.S.", "Nabi Ibrahim A.S.", "Nabi Musa A.S.", "Nabi Isa A.S."], "jawapan": 3},
            {"id": 60, "soalan": "Nabi yang tongkatnya boleh bertukar menjadi ular besar ialah...", "pilihan": ["Nabi Sholeh A.S.", "Nabi Musa A.S.", "Nabi Sulaiman A.S.", "Nabi Harun A.S."], "jawapan": 1},
            {"id": 61, "soalan": "Perisian perhitungan amalan manusia di akhirat dikenali sebagai...", "pilihan": ["Yaumul Mizan", "Yaumul Ba'ath", "Yaumul Jaza'", "Yaumul Hisab"], "jawapan": 3},
            {"id": 62, "soalan": "Apakah nama telaga atau sungai khas untuk Nabi Muhammad SAW di syurga?", "pilihan": ["Tasnim", "Ma'in", "Al-Kautsar", "Salsabil"], "jawapan": 2},
            {"id": 63, "soalan": "Sifat mustahil bagi Rasul 'Kizib' bermaksud...", "pilihan": ["Kianat", "Bodoh", "Berdusta", "Menyembunyikan"], "jawapan": 2},
            {"id": 64, "soalan": "Sifat mustahil bagi Rasul 'Khianat' bermaksud...", "pilihan": ["Pecah amanah", "Berdusta", "Lupa", "Bodoh"], "jawapan": 0},
            {"id": 65, "soalan": "Sifat mustahil bagi Rasul 'Kitman' bermaksud...", "pilihan": ["Pecah amanah", "Menyembunyikan wahyu", "Bodoh", "Dusta"], "jawapan": 1},
            {"id": 66, "soalan": "Sifat mustahil bagi Rasul 'Baladah' bermaksud...", "pilihan": ["Sombong", "Dusta", "Bodoh", "Khianat"], "jawapan": 2},
            {"id": 67, "soalan": "Kejadian luar biasa yang dikurniakan kepada para Nabi dipanggil...", "pilihan": ["Karamah", "Irhas", "Mukjizat", "Ma'unah"], "jawapan": 2},
            {"id": 68, "soalan": "Kejadian luar biasa yang berlaku kepada wali-wali Allah dipanggil...", "pilihan": ["Istidraj", "Mukjizat", "Irhas", "Karamah"], "jawapan": 3},
            {"id": 69, "soalan": "Beriman kepada Rasul ke-25 iaitu Nabi Muhammad SAW bermaksud...", "pilihan": ["Mengikuti syariat baginda sepenuhnya", "Menganggap baginda tuhan", "Sekadar percaya nama baginda", "Membaca sejarahnya sahaja"], "jawapan": 0},
            {"id": 70, "soalan": "Sifat Wujud bagi Allah bermaksud Allah itu...", "pilihan": ["Sedia", "Ada", "Kekal", "Esa"], "jawapan": 1}
        ],
        "rukun_islam": [
            {"id": 1, "soalan": "Berapakah bilangan Rukun Islam?", "pilihan": ["4", "5", "6", "7"], "jawapan": 1},
            {"id": 2, "soalan": "Mengucap dua kalimah syahadah merupakan Rukun Islam yang ke-...", "pilihan": ["Pertama", "Kedua", "Ketiga", "Keempat"], "jawapan": 0},
            {"id": 3, "soalan": "Rukun Islam yang kedua ialah...", "pilihan": ["Menunaikan Zakat", "Mendirikan Solat", "Berpuasa di bulan Ramadan", "Mengerjakan Haji"], "jawapan": 1},
            {"id": 4, "soalan": "Ibadah puasa wajib dijalankan pada bulan...", "pilihan": ["Syawal", "Rejab", "Ramadan", "Syaaban"], "jawapan": 2},
            {"id": 5, "soalan": "Mengerjakan Haji wajib bagi mereka yang...", "pilihan": ["Berilmu tinggi", "Berumur 40 tahun ke atas", "Mampu dari segi kewangan & kesihatan", "Tinggal di Makkah sahaja"], "jawapan": 2},
            {"id": 6, "soalan": "Syahadah terdiri daripada penyaksian kepada...", "pilihan": ["Allah dan Malaikat", "Allah dan Kitab", "Allah dan Rasul-Nya", "Malaikat dan Rasul"], "jawapan": 2},
            {"id": 7, "soalan": "Ibadah yang menjadi 'tiang agama' ialah...", "pilihan": ["Zakat", "Solat", "Puasa", "Haji"], "jawapan": 1},
            {"id": 8, "soalan": "Zakat yang wajib dikeluarkan pada akhir bulan Ramadan dinamakan...", "pilihan": ["Zakat Mal", "Zakat Perniagaan", "Zakat Fitrah", "Zakat Emas"], "jawapan": 2},
            {"id": 9, "soalan": "Apakah syarat wajib ibadah puasa Ramadan?", "pilihan": ["Kaya", "Islam, baligh, dan berakal", "Sudah menunaikan haji", "Menafkahkan harta"], "jawapan": 1},
            {"id": 10, "soalan": "Tempat pelaksanaan ibadah Haji adalah di...", "pilihan": ["Madinah", "Baitulmaqdis", "Makkah dan kawasan sekitarnya", "Kaherah"], "jawapan": 2},
            {"id": 11, "soalan": "Apakah hukum mengucap Dua Kalimah Syahadah bagi seseorang yang mahu memeluk Islam?", "pilihan": ["Wajib", "Sunat", "Harus", "Makruh"], "jawapan": 0},
            {"id": 12, "soalan": "Solat fardu sehari semalam mengandungi berapa rakaat kesemuanya?", "pilihan": ["15 Rakaat", "20 Rakaat", "17 Rakaat", "12 Rakaat"], "jawapan": 2},
            {"id": 13, "soalan": "Zakat harta dikeluarkannya bertujuan untuk...", "pilihan": ["Menunjuk-nunjuk", "Membersihkan harta dan menyucikan jiwa", "Menambah keuntungan perniagaan", "Membayar cukai kerajaan"], "jawapan": 1},
            {"id": 14, "soalan": "Puasa bermaksud menahan diri daripada perkara yang membatalkan puasa bermula dari...", "pilihan": ["Terbit fajar hingga terbenam matahari", "Terbit matahari hingga terbenam matahari", "Subuh hingga Isyak", "Tengah malam hingga petang"], "jawapan": 0},
            {"id": 15, "soalan": "Bulan kesepuluh dalam kalendar Hijrah di mana umat Islam menyambut Hari Raya Aidilfitri ialah...", "pilihan": ["Ramadan", "Syawal", "Zulhijjah", "Muharram"], "jawapan": 1},
            {"id": 16, "soalan": "Apakah ibadah yang dilakukan dengan mengelilingi Kaabah sebanyak 7 kali?", "pilihan": ["Sa'i", "Wukuf", "Tawaf", "Tahallul"], "jawapan": 2},
            {"id": 17, "soalan": "Berlari-lari kecil antara bukit Safa dan Marwah dinamakan...", "pilihan": ["Tawaf", "Sa'i", "Wukuf", "Rami Juamrat"], "jawapan": 1},
            {"id": 18, "soalan": "Kadar zakat fitrah dikeluarkan dalam bentuk makanan asasi seperti...", "pilihan": ["Gandum sahaja", "Buah kurma sahaja", "Beras", "Roti"], "jawapan": 2},
            {"id": 19, "soalan": "Kemuncak ibadah haji di mana para jemaah berkumpul di Padang Arafah dinamakan...", "pilihan": ["Tawaf Wada'", "Wukuf", "Mabit", "Tahallul"], "jawapan": 1},
            {"id": 20, "soalan": "Orang yang berhak menerima zakat dipanggil...", "pilihan": ["Amil", "Muallaf", "Asnaf", "Fakir"], "jawapan": 2},
            {"id": 21, "soalan": "Berapakah bilangan golongan Asnaf yang berhak menerima zakat?", "pilihan": ["6 Golongan", "8 Golongan", "10 Golongan", "5 Golongan"], "jawapan": 1},
            {"id": 22, "soalan": "Menyengaja makan dan minum dengan sengaja semasa berpuasa hukumnya...", "pilihan": ["Harus", "Makruh", "Membatalkan puasa", "Dimaafkan"], "jawapan": 2},
            {"id": 23, "soalan": "Solat yang tidak boleh ditinggalkan dalam apa jua keadaan selagi berakal ialah...", "pilihan": ["Solat Sunat", "Solat Fardu", "Solat Dhuha", "Solat Tahajjud"], "jawapan": 1},
            {"id": 24, "soalan": "Memotong rambut sekurang-kurangnya 3 helai selepas ibadah haji/umrah dipanggil...", "pilihan": ["Tawaf", "Tahallul", "Sa'i", "Ihram"], "jawapan": 1},
            {"id": 25, "soalan": "Niat ihram haji dilakukan di tempat yang ditetapkan yang dipanggil...", "pilihan": ["Maqam Ibrahim", "Hijir Ismail", "Miqat", "Multazam"], "jawapan": 2},
            {"id": 26, "soalan": "Solat sunat yang dipraktikkan khusus pada malam-malam bulan Ramadan ialah...", "pilihan": ["Solat Witir", "Solat Tarawih", "Solat Tahajjud", "Solat Hajat"], "jawapan": 1},
            {"id": 27, "soalan": "Hukum menunaikan ibadah Haji bagi yang berkemampuan adalah wajib sebanyak...", "pilihan": ["Setiap tahun", "Sekali seumur hidup", "Dua kali seumur hidup", "Mengikut kehendak diri"], "jawapan": 1},
            {"id": 28, "soalan": "Niat puasa Ramadan adalah tergolong dalam...", "pilihan": ["Syarat Sah Puasa", "Rukun Puasa", "Sunat Puasa", "Perkara membatalkan puasa"], "jawapan": 1},
            {"id": 29, "soalan": "Mengucapkan dua kalimah syahadah menandakan seseorang itu...", "pilihan": ["Mencapai umur baligh", "Selesai haji", "Masuk Islam", "Mendapat pahala sunat"], "jawapan": 2},
            {"id": 30, "soalan": "Pelaksanaan Rukun Islam membentuk pertalian manusia dengan Allah dan...", "pilihan": ["Malaikat sahaja", "Sesama manusia", "Haiwan sahaja", "Alam ghaib"], "jawapan": 1},
            {"id": 31, "soalan": "Ibadah puasa mengajar umat Islam tentang sifat...", "pilihan": ["Membazir", "Sabar dan empati", "Sombong", "Pentingkan diri"], "jawapan": 1},
            {"id": 32, "soalan": "Bulan yang diwajibkan berpuasa dalam kalendar Islam ialah...", "pilihan": ["Rejab", "Ramadan", "Syaaban", "Muharram"], "jawapan": 1},
            {"id": 33, "soalan": "Malam yang lebih baik daripada 1000 bulan di bulan Ramadan dipanggil...", "pilihan": ["Nuzul Al-Quran", "Lailatul Qadar", "Israk Mikraj", "Malam Isra'"], "jawapan": 1},
            {"id": 34, "soalan": "Perbuatan bersahur sebelum berpuasa hukumnya...", "pilihan": ["Wajib", "Harus", "Sunat", "Makruh"], "jawapan": 2},
            {"id": 35, "soalan": "Memberi makan kepada orang yang berbuka puasa mendapat pahala...", "pilihan": ["Setengah pahala", "Sama seperti pahala orang berpuasa", "Tiada pahala", "Double pahala haji"], "jawapan": 1},
            {"id": 36, "soalan": "Hari Raya Korban/Haji diraikan pada bulan...", "pilihan": ["Syawal", "Zulhijjah", "Ramadan", "Muharram"], "jawapan": 1},
            {"id": 37, "soalan": "Menyembelih binatang ternakan pada 10, 11, 12, dan 13 Zulhijjah dipanggil...", "pilihan": ["Akikah", "Dam", "Ibadah Korban", "Fidyah"], "jawapan": 2},
            {"id": 38, "soalan": "Ibadah penyembelihan ternakan atas kelahiran bayi dipanggil...", "pilihan": ["Korban", "Akikah", "Nazar", "Sedekah"], "jawapan": 1},
            {"id": 39, "soalan": "Pakaian khusus berwarna putih tanpa jahitan bagi jemaah haji lelaki dinamakan...", "pilihan": ["Jubah", "Kain Pelikat", "Kain Ihram", "Samping"], "jawapan": 2},
            {"id": 40, "soalan": "Cukai/bayaran ganti rugi kerana melanggar larangan ihram haji dipanggil...", "pilihan": ["Fidyah", "Dam", "Zakat", "Cukai"], "jawapan": 1},
            {"id": 41, "soalan": "Hari Arafah iaitu hari puncak wukuf jatuh pada date...", "pilihan": ["10 Zulhijjah", "9 Zulhijjah", "1 Syawal", "15 Ramadan"], "jawapan": 1},
            {"id": 42, "soalan": "Membaling batu di Jamrah melambangkan penolakan terhadap...", "pilihan": ["Godaan Syaitan", "Musuh Islam", "Kemiskinan", "Dosa lalu"], "jawapan": 0},
            {"id": 43, "soalan": "Syarat wajib zakat harta antaranya ialah 'Nisab'. Apakah maksud Nisab?", "pilihan": ["Tempoh pemilikan setahun", "Kadar minimum harta yang mewajibkan zakat", "Jenis harta", "Nama penerima zakat"], "jawapan": 1},
            {"id": 44, "soalan": "Apakah maksud 'Haul' dalam syarat zakat?", "pilihan": ["Cukup berat harta", "Ketiadaan hutang", "Cukup tempoh pemilikan harta selama setahun", "Telah mencapai umur dewasa"], "jawapan": 2},
            {"id": 45, "soalan": "Golongan Muallaf adalah antara penerima zakat. Siapakah Muallaf?", "pilihan": ["Orang fakir", "Orang berhutang", "Orang yang baru memeluk agama Islam", "Pengumpul zakat"], "jawapan": 2},
            {"id": 46, "soalan": "Solat Sunat Aidilfitri dikerjakan sebanyak berapa rakaat?", "pilihan": ["4 Rakaat", "2 Rakaat", "3 Rakaat", "1 Rakaat"], "jawapan": 1},
            {"id": 47, "soalan": "Hari yang diharamkan berpuasa ialah pada 1 Syawal dan...", "pilihan": ["Hari Jumaat", "Hari Isnin", "Hari Tasyrik (11, 12, 13 Zulhijjah)", "Hari Arafah"], "jawapan": 2},
            {"id": 48, "soalan": "Puasa enam hari yang disunatkan selepas Ramadan ialah pada bulan...", "pilihan": ["Syaaban", "Syawal", "Zulkaedah", "Muharram"], "jawapan": 1},
            {"id": 49, "soalan": "Tawaf penghormatan terakhir sebelum meninggalkan kota Makkah dipanggil...", "pilihan": ["Tawaf Ifadah", "Tawaf Qudum", "Tawaf Wada'", "Tawaf Sunat"], "jawapan": 2},
            {"id": 50, "soalan": "Ibadah Umrah boleh dikerjakan pada...", "pilihan": ["Bila-bila masa sepanjang tahun", "Bulan Zulhijjah sahaja", "Bulan Ramadan sahaja", "Hari Raya sahaja"], "jawapan": 0},
            {"id": 51, "soalan": "Petugas yang dilantik kerajaan untuk memungut dan mengagihkan zakat dipanggil...", "pilihan": ["Muallaf", "Amil", "Gharimin", "Riqab"], "jawapan": 1},
            {"id": 52, "soalan": "Golongan 'Gharimin' yang berhak menerima zakat ialah orang yang...", "pilihan": ["Hamba yang ingin memerdekakan diri", "Berhutang untuk keperluan asas", "Musafir yang kehabisan bekalan", "Orang miskin"], "jawapan": 1},
            {"id": 53, "soalan": "Antara berikut, binatang yang WAJIB dikeluarkan zakat ternakan ialah...", "pilihan": ["Kuda dan Ayam", "Itik dan Burung", "Lembu dan Kambing", "Ikan dan Udang"], "jawapan": 2},
            {"id": 54, "soalan": "Solat Jumaat diwajibkan ke atas lelaki Muslim secara...", "pilihan": ["Bersendirian", "Berjamaah", "Munfarid", "Sembunyi"], "jawapan": 1},
            {"id": 55, "soalan": "Syarat sah Solat Jumaat antaranya hendaklah didirikan sekurang-kurangnya berapa orang ahli jemaah (menurut mazhab Syafi'i)?", "pilihan": ["12 Orang", "40 Orang", "2 Orang", "100 Orang"], "jawapan": 1},
            {"id": 56, "soalan": "Bermalam di Muzdalifah dan Mina semasa ibadah haji dinamakan...", "pilihan": ["Wukuf", "Tawaf", "Mabit", "Sa'i"], "jawapan": 2},
            {"id": 57, "soalan": "Perbuatan menyapu debu tanah yang suci ke muka dan kedua-dua tangan sebagai ganti wuduk dipanggil...", "pilihan": ["Istinja'", "Tayamum", "Samak", "Sertu"], "jawapan": 1},
            {"id": 58, "soalan": "Tayamum dilakukan untuk menggantikan wuduk apabila...", "pilihan": ["Saja nak cepat", "Ketiadaan air / uzur sakit", "Malas guna air", "Cuaca terlalu panas"], "jawapan": 1},
            {"id": 59, "soalan": "Satu tayamum hanya sah digunakan untuk berapa solat fardu?", "pilihan": ["2 Solat Fardu", "1 Solat Fardu sahaja", "Sepanjang hari", "3 Solat Fardu"], "jawapan": 1},
            {"id": 60, "soalan": "Mengerjakan ibadah Umrah terlebih dahulu sebelum Haji dipanggil Haji...", "pilihan": ["Ifrad", "Qiran", "Tamattu'", "Mabrur"], "jawapan": 2},
            {"id": 61, "soalan": "Mengerjakan ibadah Haji sahaja tanpa Umrah dipanggil Haji...", "pilihan": ["Tamattu'", "Ifrad", "Qiran", "Badal"], "jawapan": 1},
            {"id": 62, "soalan": "Mengerjakan Haji dan Umrah secara serentak dipanggil Haji...", "pilihan": ["Ifrad", "Qiran", "Tamattu'", "Wada'"], "jawapan": 1},
            {"id": 63, "soalan": "Puasa ganti bagi hari-hari Ramadan yang ditinggalkan dipanggil...", "pilihan": ["Puasa Nazar", "Puasa Qada'", "Puasa Kaffarah", "Puasa Sunat"], "jawapan": 1},
            {"id": 64, "soalan": "Denda berupa makanan yang perlu dibayar kerana melepaskan puasa atas sebab tertentu dinamakan...", "pilihan": ["Dam", "Fidyah", "Zakat", "Sedekah"], "jawapan": 1},
            {"id": 65, "soalan": "Puasa yang dijanjikan berniat untuk dilakukan jika sesuatu hajat tercapai dipanggil...", "pilihan": ["Puasa Sunat", "Puasa Kaffarah", "Puasa Nazar", "Puasa Qada'"], "jawapan": 2},
            {"id": 66, "soalan": "Waktu mula berpuasa yang menandakan masuknya waktu imsak biasanya berapa minit sebelum Subuh?", "pilihan": ["30 minit", "10 minit", "1 jam", "5 minit"], "jawapan": 1},
            {"id": 67, "soalan": "Membayar zakat perniagaan dikira berdasarkan nilaian harta perniagaan yang cukup...", "pilihan": ["Bilangan pekerja", "Nisab dan Haul", "Untung bersih sahaja", "Jumlah kedai"], "jawapan": 1},
            {"id": 68, "soalan": "Zakat emas wajib dikeluarkan apabila simpanan emas yang tidak dipakai mencapai nisab...", "pilihan": ["100 Gram", "85 Gram", "50 Gram", "200 Gram"], "jawapan": 1},
            {"id": 69, "soalan": "Syarat sah Syahadah hendaklah difahami maknanya dan...", "pilihan": ["Diucap dengan lisan sahaja", "Diyakini dalam hati", "Ditulis di kertas", "Dihafal cepat"], "jawapan": 1},
            {"id": 70, "soalan": "Ibadah Haji merupakan rukun Islam yang wajib dilaksanakan oleh orang Islam yang mampu sekurang-kurangnya...", "pilihan": ["2 Kali", "Sekali seumur hidup", "5 Kali", "Setiap 5 tahun"], "jawapan": 1}
        ],
        "rukun_solat":[
            {"id": 1, "soalan": "Berapakah jumlah Rukun Solat?", "pilihan": ["12", "13", "14", "15"], "jawapan": 1},
            {"id": 2, "soalan": "Niat dalam solat dilakukan serentak semasa...", "pilihan": ["Membaca Al-Fatihah", "Rukuk", "Takbiratul Ihram", "Sujud"], "jawapan": 2},
            {"id": 3, "soalan": "Membaca Surah Al-Fatihah dalam solat hukumnya...", "pilihan": ["Sunat Ab'ad", "Wajib", "Sunat Hai'ah", "Harus"], "jawapan": 1},
            {"id": 4, "soalan": "Perbuatan berdiri tegak bagi yang mampu termasuk dalam rukun...", "pilihan": ["Rukun Qawli", "Rukun Qalbi", "Rukun Fi'li", "Rukun Sunat"], "jawapan": 2},
            {"id": 5, "soalan": "Membaca Bacaan Tahiyyat Akhir tergolong dalam rukun...", "pilihan": ["Rukun Qawli", "Rukun Fi'li", "Rukun Qalbi", "Rukun Syarat"], "jawapan": 0},
            {"id": 6, "soalan": "Niat dan Tertib dalam solat tergolong dalam rukun...", "pilihan": ["Rukun Qawli", "Rukun Qalbi", "Rukun Fi'li", "Rukun Isyari"], "jawapan": 1},
            {"id": 7, "soalan": "Berapakah anggota sujud yang wajib menyentuh lantai?", "pilihan": ["5 Anggota", "7 Anggota", "8 Anggota", "6 Anggota"], "jawapan": 1},
            {"id": 8, "soalan": "Bertenang seketika semasa rukuk, iktidal, dan sujud dipanggil...", "pilihan": ["Tawadhu'", "Tabarruk", "Thuma'ninah", "Tadarru'"], "jawapan": 2},
            {"id": 9, "soalan": "Membaca Selawat ke atas Nabi SAW dalam Tahiyyat Akhir hukumnya...", "pilihan": ["Sunat Hai'ah", "Rukun Solat", "Membatalkan Solat", "Harus"], "jawapan": 1},
            {"id": 10, "soalan": "Salam yang pertama dalam solat hukumnya...", "pilihan": ["Sunat Hai'ah", "Wajib", "Sunat Ab'ad", "Mubah"], "jawapan": 1},
            {"id": 11, "soalan": "Salam yang kedua dalam solat hukumnya...", "pilihan": ["Rukun", "Wajib", "Sunat", "Haram"], "jawapan": 2},
            {"id": 12, "soalan": "Duduk di antara dua sujud tergolong dalam rukun...", "pilihan": ["Rukun Qawli", "Rukun Qalbi", "Rukun Fi'li", "Rukun Syarat"], "jawapan": 2},
            {"id": 13, "soalan": "Duduk semasa membaca Tahiyyat Akhir dipanggil duduk...", "pilihan": ["Iftirasy", "Tawarruk", "Iq'a'", "Tarabbu'"], "jawapan": 1},
            {"id": 14, "soalan": "Duduk di antara dua sujud dan duduk Tahiyyat Awal dipanggil duduk...", "pilihan": ["Tawarruk", "Iftirasy", "Iq'a'", "Sadl"], "jawapan": 1},
            {"id": 15, "soalan": "Menyusun perbuatan solat mengikut urutan yang betul dinamakan...", "pilihan": ["Tawazun", "Tertib", "Muwalat", "Tartan"], "jawapan": 1},
            {"id": 16, "soalan": "Berikut adalah Rukun Qawli (bacaan) KECUALI...", "pilihan": ["Takbiratul Ihram", "Membaca Al-Fatihah", "Membaca Doa Qunut", "Membaca Tahiyyat Akhir"], "jawapan": 2},
            {"id": 17, "soalan": "Bangkit dari rukuk dan berdiri tegak dinamakan...", "pilihan": ["Sujud", "Iktidal", "Rukuk", "Duduk Iftirasy"], "jawapan": 1},
            {"id": 18, "soalan": "Anggota sujud di bawah adalah wajib disentuhkan ke tempat sujud KECUALI...", "pilihan": ["Dahi", "Lutut", "Siku", "Tapak tangan"], "jawapan": 2},
            {"id": 19, "soalan": "Apakah hukum tidak membaca Basmalah (Bismillah) bagi madzhab Syafi'i semasa Al-Fatihah dalam solat?", "pilihan": ["Sah solatnya", "Tidak sah kerana Basmalah ayat pertama Al-Fatihah", "Sunat sahaja", "Harus ditinggalkan"], "jawapan": 1},
            {"id": 20, "soalan": "Berapakah jumlah Rukun Qawli dalam solat?", "pilihan": ["6", "7", "5", "4"], "jawapan": 2},
            {"id": 21, "soalan": "Berapakah jumlah Rukun Fi'li dalam solat?", "pilihan": ["6", "5", "8", "7"], "jawapan": 0},
            {"id": 22, "soalan": "Berapakah jumlah Rukun Qalbi dalam solat?", "pilihan": ["3", "2 (Niat & Tertib)", "1", "4"], "jawapan": 1},
            {"id": 23, "soalan": "Lupa melakukan Rukun Solat menyebabkan...", "pilihan": ["Diampunkan terus", "Solat tidak sah melainkan diganti/diulangi", "Cukup dengan sujud sahwi tanpa ganti", "Solat jadi sunat"], "jawapan": 1},
            {"id": 24, "soalan": "Sujud yang dilakukan di hujung solat kerana terlupa sunat Ab'ad atau ragu bilangan rakaat dipanggil...", "pilihan": ["Sujud Sahwi", "Sujud Tilawah", "Sujud Syukur", "Sujud Sejadah"], "jawapan": 0},
            {"id": 25, "soalan": "Membongkokkan badan sehingga tapak tangan memegang lutut dipanggil...", "pilihan": ["Iktidal", "Rukuk", "Sujud", "Tawarruk"], "jawapan": 1},
            {"id": 26, "soalan": "Memalingkan muka ke kanan semasa mengucapkan salam pertama hukumnya...", "pilihan": ["Rukun", "Harus", "Sunat (Mengucapkan salamnya yang rukun)", "Makruh"], "jawapan": 2},
            {"id": 27, "soalan": "Apakah ucapan takbir semasa mula-mula mengangkat tangan masuk ke dalam solat?", "pilihan": ["Subhanallah", "Allahu Akbar", "Alhamdulillah", "La ilaha illallah"], "jawapan": 1},
            {"id": 28, "soalan": "Membaca surah pendek selepas Al-Fatihah hukumnya...", "pilihan": ["Rukun Solat", "Sunat Hai'ah", "Sunat Ab'ad", "Wajib"], "jawapan": 1},
            {"id": 29, "soalan": "Membaca Doa Iftitah tergolong dalam...", "pilihan": ["Rukun Qawli", "Sunat Hai'ah", "Sunat Ab'ad", "Syarat Sah"], "jawapan": 1},
            {"id": 30, "soalan": "Solat dimulakan dengan Takbiratul Ihram dan diakhiri dengan...", "pilihan": ["Sujud", "Salam", "Doa", "Dzikir"], "jawapan": 1},
            {"id": 31, "soalan": "Membaca Selawat ke atas keluarga Nabi dalam Tahiyyat Akhir hukumnya...", "pilihan": ["Rukun Solat", "Sunat Ab'ad", "Membatalkan solat", "Harus"], "jawapan": 1},
            {"id": 32, "soalan": "Membaca Surah selepas Al-Fatihah dilakukan pada rakaat...", "pilihan": ["Semua rakaat", "Rakaat Pertama dan Kedua sahaja", "Rakaat Terakhir sahaja", "Rakaat Ketiga sahaja"], "jawapan": 1},
            {"id": 33, "soalan": "Membaca bacaan 'Subhana Rabbiyal Azimi Wa Bihamdih' disunatkan semasa...", "pilihan": ["Rukuk", "Sujud", "Iktidal", "Duduk antara dua sujud"], "jawapan": 0},
            {"id": 34, "soalan": "Membaca 'Subhana Rabbiyal A'la Wa Bihamdih' disunatkan semasa...", "pilihan": ["Rukuk", "Sujud", "Iktidal", "Tahiyyat"], "jawapan": 1},
            {"id": 35, "soalan": "Sujud Sahwi dilakukan...", "pilihan": ["Di awal solat", "Sebelum atau selepas salam di hujung solat", "Semasa rukuk", "Selepas bangun dari solat"], "jawapan": 1},
            {"id": 36, "soalan": "Berapakah bilangan sujud dalam satu rakaat solat?", "pilihan": ["1 Kali Sujud", "2 Kali Sujud", "3 Kali Sujud", "4 Kali Sujud"], "jawapan": 1},
            {"id": 37, "soalan": "Mengangkat kedua-dua tangan semasa Takbiratul Ihram hukumnya...", "pilihan": ["Rukun Solat", "Sunat Hai'ah", "Wajib", "Syarat Sah"], "jawapan": 1},
            {"id": 38, "soalan": "Apakah hukum pergerakan berturut-turut sebanyak 3 kali yang besar dalam solat?", "pilihan": ["Sunat", "Membatalkan solat", "Harus", "Makruh"], "jawapan": 1},
            {"id": 39, "soalan": "Bercakap dengan sengaja walaupun satu perkataan yang faham maknanya...", "pilihan": ["Dimaafkan", "Membatalkan solat", "Sunat sujud sahwi", "Makruh"], "jawapan": 1},
            {"id": 40, "soalan": "Membuka aurat dengan sengaja semasa solat menjadikan solat...", "pilihan": ["Sah tetapi makruh", "Batal", "Sunat", "Harus"], "jawapan": 1},
            {"id": 41, "soalan": "Solat yang tidak didahului dengan wuduk atau tayamum hukumnya...", "pilihan": ["Sah", "Tidak Sah", "Makruh", "Harus"], "jawapan": 1},
            {"id": 42, "soalan": "Apakah kedudukan makmum lelaki seorang berada di sebelah imam?", "pilihan": ["Di sebelah kiri", "Di sebelah kanan imam belakang sedikit", "Di belakang 3 saf", "Di hadapan imam"], "jawapan": 1},
            {"id": 43, "soalan": "Syarat menjadi Imam hendaklah seorang yang...", "pilihan": ["Paling tua", "Lebih baik bacaan Al-Quran & faham hukum solat", "Paling kaya", "Paling tinggi"], "jawapan": 1},
            {"id": 44, "soalan": "Solat Gerhana Matahari dipanggil solat sunat...", "pilihan": ["Kusuf", "Khusuf", "Istisqa'", "Istikharah"], "jawapan": 0},
            {"id": 45, "soalan": "Solat Gerhana Bulan dipanggil solat sunat...", "pilihan": ["Kusuf", "Khusuf", "Dhuha", "Awwabin"], "jawapan": 1},
            {"id": 46, "soalan": "Solat sunat memohon hujan dipanggil solat sunat...", "pilihan": ["Istikharah", "Hajat", "Istisqa'", "Tahajjud"], "jawapan": 2},
            {"id": 47, "soalan": "Solat sunat untuk memohon petunjuk pilihan dipanggil...", "pilihan": ["Hajat", "Istikharah", "Tasbih", "Tarawih"], "jawapan": 1},
            {"id": 48, "soalan": "Arah Kiblat bagi umat Islam di seluruh dunia ialah menghadap ke...", "pilihan": ["Masjid Al-Aqsa", "Kaabah di Makkah", "Baitulmaqdis", "Madinah"], "jawapan": 1},
            {"id": 49, "soalan": "Niat diletakkan di dalam...", "pilihan": ["Mulut sahaja", "Hati", "Telinga", "Mata"], "jawapan": 1},
            {"id": 50, "soalan": "Lafaz 'Sami'Allahu Liman Hamidah' dibaca semasa...", "pilihan": ["Mahu sujud", "Semasa rukuk", "Bangkit dari rukuk menuju iktidal", "Semasa duduk antara dua sujud"], "jawapan": 2},
            {"id": 51, "soalan": "Membaca Doa Qunut pada iktidal rakaat kedua solat Subuh mengikut Mazhab Syafi'i tergolong dalam...", "pilihan": ["Rukun Qawli", "Sunat Ab'ad", "Sunat Hai'ah", "Syarat Sah"], "jawapan": 1},
            {"id": 52, "soalan": "Jika tertinggal Sunat Ab'ad (seperti Tahiyyat Awal), solatnya tetap sah tetapi disunatkan...", "pilihan": ["Solat semula", "Sujud Sahwi", "Sujud Syukur", "Membaca Istighfar"], "jawapan": 1},
            {"id": 53, "soalan": "Membaca Tahiyyat Awal tergolong dalam...", "pilihan": ["Rukun Solat", "Sunat Ab'ad", "Sunat Hai'ah", "Harus"], "jawapan": 1},
            {"id": 54, "soalan": "Membaca bacaan 'Rabbighfirli warhamni...' disunatkan semasa...", "pilihan": ["Sujud", "Rukuk", "Duduk di antara dua sujud", "Iktidal"], "jawapan": 2},
            {"id": 55, "soalan": "Membaca 'Amin' secara lantang selepas imam selesai Al-Fatihah hukumnya...", "pilihan": ["Rukun Solat", "Sunat Hai'ah", "Wajib", "Makruh"], "jawapan": 1},
            {"id": 56, "soalan": "Solat empat rakaat yang dipendekkan menjadi dua rakaat semasa musafir dipanggil Solat...", "pilihan": ["Jamak", "Qasar", "Witr", "Dhuha"], "jawapan": 1},
            {"id": 57, "soalan": "Mengkombinasikan dua solat fardu dalam satu waktu semasa musafir dipanggil Solat...", "pilihan": ["Qasar", "Jamak", "Tahajjud", "Hajat"], "jawapan": 1},
            {"id": 58, "soalan": "Menghimpunkan Solat Zohor dan Asar dalam waktu Zohor dipanggil Jamak...", "pilihan": ["Taqdim", "Takhir", "Qasar", "Muntaha"], "jawapan": 0},
            {"id": 59, "soalan": "Menghimpunkan Solat Maghrib dan Isyak dalam waktu Isyak dipanggil Jamak...", "pilihan": ["Taqdim", "Takhir", "Mu'ajjal", "Kamil"], "jawapan": 1},
            {"id": 60, "soalan": "Solat Fardu yang Boleh di-Qasarkan (dipendekkan rakaatnya) ialah...", "pilihan": ["Maghrib dan Subuh", "Zohor, Asar, dan Isyak", "Subuh sahaja", "Semua solat fardu"], "jawapan": 1},
            {"id": 61, "soalan": "Syarat sah solat antaranya ialah suci daripada hadas kecil dan besar serta suci daripada...", "pilihan": ["Hutang", "Najis pada badan, pakaian, dan tempat", "Masa lalu", "Semua dosa"], "jawapan": 1},
            {"id": 62, "soalan": "Menutup aurat merupakan antara...", "pilihan": ["Rukun Solat", "Syarat Sah Solat", "Sunat Solat", "Perkara Makruh"], "jawapan": 1},
            {"id": 63, "soalan": "Aurat lelaki di dalam solat ialah di antara...", "pilihan": ["Dada hingga buku lali", "Pusat hingga lutut", "Bahu hingga lutut", "Seluruh badan"], "jawapan": 1},
            {"id": 64, "soalan": "Aurat wanita di dalam solat ialah seluruh badan KECUALI...", "pilihan": ["Rambut dan kaki", "Muka dan kedua-dua tapak tangan", "Muka dan leher", "Tapak tangan sahaja"], "jawapan": 1},
            {"id": 65, "soalan": "Melihat ke arah langit/atas semasa sedang solat hukumnya...", "pilihan": ["Harus", "Makruh", "Sunat", "Membatalkan solat"], "jawapan": 1},
            {"id": 66, "soalan": "Mencekak pinggang semasa bersolat hukumnya...", "pilihan": ["Batal", "Makruh", "Sunat", "Wajib"], "jawapan": 1},
            {"id": 67, "soalan": "Solat Jenazah mengandungi berapa kali takbir?", "pilihan": ["2 Kali Takbir", "4 Kali Takbir", "5 Kali Takbir", "7 Kali Takbir"], "jawapan": 1},
            {"id": 68, "soalan": "Solat Jenazah dilakukan tanpa perbuatan...", "pilihan": ["Takbir", "Rukuk dan Sujud", "Membaca Al-Fatihah", "Salam"], "jawapan": 1},
            {"id": 69, "soalan": "Membaca Selawat ke atas Nabi dalam Solat Jenazah dilakukan selepas...", "pilihan": ["Takbir Pertama", "Takbir Kedua", "Takbir Ketiga", "Takbir Keempat"], "jawapan": 1},
            {"id": 70, "soalan": "Mendoakan mayat dalam Solat Jenazah dilakukan khusus selepas...", "pilihan": ["Takbir Pertama", "Takbir Kedua", "Takbir Ketiga", "Takbir Keempat"], "jawapan": 2}
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
            {"id": 1, "soalan": "Berapakah jumlah Rukun Nikah?", "pilihan": ["4", "6", "5", "7"], "jawapan": 2},
            {"id": 2, "soalan": "Berikut merupakan Rukun Nikah KECUALI...", "pilihan": ["Pengantin Lelaki", "Hantaran / Mas Kahwin", "Pengantin Perempuan", "Wali"], "jawapan": 1},
            {"id": 3, "soalan": "Lafaz penyerahan dari pihak wali dan penerimaan dari pihak lelaki dinamakan...", "pilihan": ["Khitbah", "Ijab dan Kabul", "Walimatulurus", "Mahar"], "jawapan": 1},
            {"id": 4, "soalan": "Berapakah bilangan saksi lelaki yang wajib ada dalam majlis akad nikah?", "pilihan": ["1 Orang Saksi", "3 Orang Saksi", "2 Orang Saksi", "4 Orang Saksi"], "jawapan": 2},
            {"id": 5, "soalan": "Pemberian wajib daripada suami kepada isteri disebabkan ikatan perkahwinan dinamakan...", "pilihan": ["Hantaran", "Sedekah", "Mahar / Mas Kahwin", "Hadiah"], "jawapan": 2},
            {"id": 6, "soalan": "Wali utama bagi seseorang wanita (bapa kandung) dinamakan...", "pilihan": ["Wali Hakim", "Wali Nasab / Wali Aqrab", "Wali Raja", "Wali Ab'ad"], "jawapan": 1},
            {"id": 7, "soalan": "Siapakah yang berhak menjadi Wali Mujbir (berkuasa mengahwinkan anak gadis)?", "pilihan": ["Abang kandung", "Bapa saudara", "Ibu kandung", "Bapa atau Datuk sebelah bapa"], "jawapan": 3},
            {"id": 8, "soalan": "Wali yang dilantik oleh pihak berkuasa agama apabila tiada wali nasab dipanggil...", "pilihan": ["Wali Mujbir", "Wali Hakim / Wali Raja", "Wali Ab'ad", "Wali Aqrab"], "jawapan": 1},
            {"id": 9, "soalan": "Apakah hukum perkahwinan tanpa kehadiran wali bagi pengantin perempuan?", "pilihan": ["Sah", "tidak Sah", "Makruh", "Harus"], "jawapan": 1},
            {"id": 10, "soalan": "Syarat saksi nikah hendaklah beragama Islam, baligh, berakal, dan...", "pilihan": ["Lelaki dan Adil", "Perempuan sahaja", "Kaya", "Saudara mara sahaja"], "jawapan": 0},
            {"id": 11, "soalan": "Lafaz 'Aku nikahkan dikau dengan anakku...' dinamakan lafaz...", "pilihan": ["Kabul", "Ijab", "Taklik", "Khitbah"], "jawapan": 1},
            {"id": 12, "soalan": "Lafaz 'Aku terima nikahnya...' oleh pengantin lelaki dinamakan lafaz...", "pilihan": ["Ijab", "Kabul", "Fasakh", "Khuluk"], "jawapan": 1},
            {"id": 13, "soalan": "Pinangan atau lamaran sebelum perkahwinan dinamakan...", "pilihan": ["Walimah", "Khitbah", "Rujuk", "Talak"], "jawapan": 1},
            {"id": 14, "soalan": "Kenduri perkahwinan yang disunatkan dalam Islam dinamakan...", "pilihan": ["Akikah", "Sadaqah", "Walimatulurus", "Tahlil"], "jawapan": 2},
            {"id": 15, "soalan": "Wanita yang haram dikahwini selamanya dinamakan...", "pilihan": ["Ajnabi", "Mahram", "Muallaf", "Bioloji"], "jawapan": 1},
            {"id": 16, "soalan": "Ibu kandung, anak perempuan, dan saudara perempuan tergolong dalam...", "pilihan": ["Ajnabi", "Mahram Muaqqat", "Mahram Muabbad (Haram selamanya)", "Bukan mahram"], "jawapan": 2},
            {"id": 17, "soalan": "Adik ipar perempuan merupakan contoh Mahram Muaqqat yang bermaksud...", "pilihan": ["Haram selamanya", "Haram dikahwini sementara (semasa isteri masih sah)", "Boleh dikahwini bila-bila", "Halal digabung sekali"], "jawapan": 1},
            {"id": 18, "soalan": "Penceraian yang dilafazkan suami kepada isteri dinamakan...", "pilihan": ["Fasakh", "Talak", "Khuluk", "Lian"], "jawapan": 1},
            {"id": 19, "soalan": "Pembubaran perkahwinan melalui keputusan mahkamah atas sebab tertentu dipanggil...", "pilihan": ["Talak", "Khuluk", "Fasakh", "Ila'"], "jawapan": 2},
            {"id": 20, "soalan": "Penceraian atas tebus talak oleh isteri dengan membayar ganti rugi kepada suami dipanggil...", "pilihan": ["Khuluk", "Fasakh", "Lian", "Zihar"], "jawapan": 0},
            {"id": 21, "soalan": "Tempoh larangan berkahwin bagi wanita selepas bercerai atau kematian suami dipanggil...", "pilihan": ["Ihram", "Iddah", "Isti'zah", "Rujuk"], "jawapan": 1},
            {"id": 22, "soalan": "Tempoh iddah bagi wanita kematian suami (tidak hamil) ialah...", "pilihan": ["3 Bulan", "100 Hari", "4 Bulan 10 Hari", "3 Kali Suci"], "jawapan": 2},
            {"id": 23, "soalan": "Tempoh iddah bagi wanita bercerai hidup yang ada haid (tidak hamil) ialah...", "pilihan": ["4 Bulan 10 Hari", "3 Kali Suci (Quru')", "1 Bulan", "100 Hari"], "jawapan": 1},
            {"id": 24, "soalan": "Tempoh iddah bagi wanita hamil yang bercerai atau kematian suami ialah sehingga...", "pilihan": ["4 Bulan 10 Hari", "3 Bulan", "Melahirkan anak", "2 Tahun"], "jawapan": 2},
            {"id": 25, "soalan": "Mengembalikan ikatan perkahwinan dalam tempoh iddah talak raj'i tanpa akad baharu dipanggil...", "pilihan": ["Nikah semula", "Rujuk", "Fasakh", "Ijab"], "jawapan": 1},
            {"id": 26, "soalan": "Talak satu dan talak dua yang masih membolehkan suami merujuk isteri dalam iddah dipanggil...", "pilihan": ["Talak Ba'in Kubra", "Talak Raj'i", "Talak Ba'in Sughra", "Talak Taklik"], "jawapan": 1},
            {"id": 27, "soalan": "Talak tiga yang mengharamkan suami merujuk semula isteri melainkan selepas isteri berkahwin dengan lelaki lain dipanggil...", "pilihan": ["Talak Raj'i", "Talak Sunnah", "Talak Ba'in Kubra", "Talak Bid'i"], "jawapan": 2},
            {"id": 28, "soalan": "Perbuatan suami menyamakan belakang isterinya dengan ibunya dinamakan...", "pilihan": ["Lian", "Zihar", "Ila'", "Khuluk"], "jawapan": 1},
            {"id": 29, "soalan": "Sumpah suami menuduh isteri berzina tanpa 4 orang saksi dipanggil...", "pilihan": ["Zihar", "Ila'", "Lian", "Taklik"], "jawapan": 2},
            {"id": 30, "soalan": "Sumpah suami tidak akan menyetubuhi isterinya dalam tempoh lebih 4 bulan dipanggil...", "pilihan": ["Zihar", "Ila'", "Lian", "Khuluk"], "jawapan": 1},
            {"id": 31, "soalan": "Syarat pengantin lelaki antaranya mestilah beragama Islam, baligh, berakal, dan...", "pilihan": ["Kaya dan berpangkat", "Mempunyai rumah sendiri", "Bukan mahram kepada calon isteri & pilihan sendiri", "Persetujuan ibu bapa sahaja"], "jawapan": 2},
            {"id": 32, "soalan": "Apakah hukum wali berkahwin dengan perempuan di bawah jagaannya jika tiada halangan?", "pilihan": ["Haram", "Wajib", "Harus (dengan syarat bukan mahram)", "Makruh"], "jawapan": 2},
            {"id": 33, "soalan": "Susunan wali nasab yang paling berhak selepas bapa ialah...", "pilihan": ["Datuk sebelah bapa ke atas", "Saudara lelaki seibu sebapa", "Bapa saudara", "Anak lelaki"], "jawapan": 0},
            {"id": 34, "soalan": "Sekiranya bapa enggan menjadi wali tanpa alasan yang sah mengikut syarak, wali tersebut dipanggil...", "pilihan": ["Wali Ab'ad", "Wali 'Adil / Wali Enggan", "Wali Mujbir", "Wali Fasik"], "jawapan": 1},
            {"id": 35, "soalan": "Hak perkahwinan bagi wali 'adil (enggan) akan berpindah kepada...", "pilihan": ["Ibu pengantin", "Wali Ab'ad", "Wali Hakim", "Tok Cadi sahaja"], "jawapan": 2},
            {"id": 36, "soalan": "Mahar yang ditentukan jumlah dan jenisnya semasa akad nikah dipanggil...", "pilihan": ["Mahar Musamma", "Mahar Misil", "Mahar Mut'ah", "Mahar Hantaran"], "jawapan": 0},
            {"id": 37, "soalan": "Mahar yang nilainya diukur mengikut kadar mas kahwin saudara perempuan pengantin dinamakan...", "pilihan": ["Mahar Musamma", "Mahar Misil", "Mahar Tunai", "Mahar Utang"], "jawapan": 1},
            {"id": 38, "soalan": "Pemberian saguhati daripada suami kepada isteri yang diceraikan tanpa sebab dipanggil...", "pilihan": ["Nafkah", "Mahar", "Mut'ah", "Hadiah"], "jawapan": 2},
            {"id": 39, "soalan": "Nafkah zahir yang wajib disediakan oleh suami untuk isteri meliputi...", "pilihan": ["Kereta mewah sahaja", "Makanan, pakaian, dan tempat tinggal", "Barang kemas sahaja", "Wang simpanan sahaja"], "jawapan": 1},
            {"id": 40, "soalan": "Perbuatan isteri menderhaka atau tidak mematuhi perintah suami yang sah dinamakan...", "pilihan": ["Khuluk", "Nusyuz", "Fasakh", "Zihar"], "jawapan": 1},
            {"id": 41, "soalan": "Isteri yang nusyuz akan kehilangan hak...", "pilihan": ["Hak jagaan anak selamanya", "Mas kahwin", "Nafkah zahir dan batin", "Gelaran isteri"], "jawapan": 2},
            {"id": 42, "soalan": "Hak menjaga dan mengasuh anak yang masih kecil selepas bercerai dipanggil...", "pilihan": ["Nusyuz", "Fasakh", "Hadanah", "Rujuk"], "jawapan": 2},
            {"id": 43, "soalan": "Orang yang paling berhak mendapat hak Hadanah (jagaan anak kecil) ialah...", "pilihan": ["Bapa kandung", "Ibu kandung", "Nenek sebelah bapa", "Bapa saudara"], "jawapan": 1},
            {"id": 44, "soalan": "Apakah hukum poligami (berkahwin lebih daripada satu sehingga empat isteri) dalam Islam?", "pilihan": ["Wajib", "Haram", "Harus (dengan syarat adil)", "Sunat mutlak"], "jawapan": 2},
            {"id": 45, "soalan": "Maksimum isteri yang boleh dihimpunkan oleh seorang lelaki Muslim dalam satu masa ialah...", "pilihan": ["2 Orang Isteri", "4 Orang Isteri", "3 Orang Isteri", "7 Orang Isteri"], "jawapan": 1},
            {"id": 46, "soalan": "Pernikahan yang diikat dengan tempoh masa tertentu (contoh: seminggu/sebulan) dinamakan...", "pilihan": ["Nikah Sunnah", "Nikah Mut'ah (Haram)", "Nikah Khuluk", "Nikah Shighar"], "jawapan": 1},
            {"id": 47, "soalan": "Apakah hukum Nikah Mut'ah (nikah kontrak) dalam Islam?", "pilihan": ["Harus", "Sunat", "Haram dan tidak sah", "Makruh"], "jawapan": 2},
            {"id": 48, "soalan": "Anak yang lahir hasil hubungan luar nikah dinamakan...", "pilihan": ["Anak Angkat", "Anak Tak Saraf / Anak Zina", "Anak Tiri", "Anak Susuan"], "jawapan": 1},
            {"id": 49, "soalan": "Anak tidak sah taraf TIDAK BOLEH dinisbahkan (bin/binti) kepada...", "pilihan": ["Ibu kandungnya", "Masyarakat", "Bapa biologinya", "Negara"], "jawapan": 2},
            {"id": 50, "soalan": "Apakah hukum bapa biologi menjadi wali nikah kepada anak perempuan tidak sah tarafnya?", "pilihan": ["Tidak Boleh (Wajib guna Wali Hakim)", "Boleh", "Sunat", "Harus"], "jawapan": 0},
            {"id": 51, "soalan": "Anak susuan menjadi mahram kepada ibu susuan apabila menyusu sekurang-kurangnya berapa kali kenyang?", "pilihan": ["3 Kali menyusu", "1 Kali sahaja", "5 Kali menyusu kenyang", "10 Kali"], "jawapan": 2},
            {"id": 52, "soalan": "Umur anak susuan yang dikira membentuk hukum mahram hendaklah di bawah...", "pilihan": ["5 Tahun", "2 Tahun", "1 Tahun", "7 Tahun"], "jawapan": 1},
            {"id": 53, "soalan": "Lafaz janji/syarat yang diucapkan suami selepas akad nikah yang boleh membatalkan perkahwinan jika dilanggar dipanggil...", "pilihan": ["Ijab", "Lafaz Taklik", "Kabul", "Rujuk"], "jawapan": 1},
            {"id": 54, "soalan": "Persetujuan nikah bagi janda hendaklah dinyatakan melalui...", "pilihan": ["Diam sahaja", "Senyuman", "Ucapan lisan yang jelas", "Isyarat mata"], "jawapan": 2},
            {"id": 55, "soalan": "Persetujuan nikah bagi anak gadis (perawan) boleh dinyatakan melalui...", "pilihan": ["Surat rasmi sahaja", "Lisan atau diamnya (tanda malu)", "Bercakap lantang sahaja", "Tepuk tangan"], "jawapan": 1},
            {"id": 56, "soalan": "Perempuan yang sedang dalam ihram haji atau umrah...", "pilihan": ["Boleh bernikah seperti biasa", "Dilarang bernikah atau dinikahkan", "Sunat bernikah", "Harus bernikah di Makkah"], "jawapan": 1},
            {"id": 57, "soalan": "Penyaksi nikah yang fasik (selalu melakukan dosa besar)...", "pilihan": ["Sah menjadi saksi", "Tidak sah menjadi saksi nikah", "Harus", "Mewajibkan hantaran tinggi"], "jawapan": 1},
            {"id": 58, "soalan": "Lafaz Ijab dan Kabul hendaklah diucapkan dalam...", "pilihan": ["Dua hari berbeza", "Melalui surat pos", "Satu majlis (pasti bersambung)", "Masa berasingan"], "jawapan": 2},
            {"id": 59, "soalan": "Pertunangan yang diputuskan oleh sebelah pihak tanpa sebab munasabah hukumnya...", "pilihan": ["Haram mutlak", "Makruh dan dicela", "Wajib bayar denda 10 kali ganda", "Batal iman"], "jawapan": 1},
            {"id": 60, "soalan": "Tunang orang lain HARAM dipinang mengikut hukum syarak jika...", "pilihan": ["Sudah kaya", "Dapat keizinan kawan", "Pinangan pertama belum dibatalkan/ditolak", "Pinangan dilakukan secara sembunyi"], "jawapan": 2},
            {"id": 61, "soalan": "Tujuan utama perkahwinan dalam Islam adalah untuk membina keluarga yang...", "pilihan": ["Kaya raya dan megah", "Sakinah, Mawaddah, dan Rahmah", "Popular", "Ditakuti musuh"], "jawapan": 1},
            {"id": 62, "soalan": "Seseorang lelaki yang tidak mampu menafkahkan isteri dan dikhuatiri menganiaya isteri, hukum berkahwin baginya ialah...", "pilihan": ["Wajib", "Sunat", "Haram", "Harus"], "jawapan": 2},
            {"id": 63, "soalan": "Lelaki yang mampu dari segi batin dan zahir serta takut terjebak dalam zina, hukum berkahwin baginya ialah...", "pilihan": ["Wajib", "Harus", "Makruh", "Sunat"], "jawapan": 0},
            {"id": 64, "soalan": "Hukum asal perkahwinan bagi orang yang tiada desakan dan mampu ialah...", "pilihan": ["Wajib", "Harus", "Sunat", "Makruh"], "jawapan": 1},
            {"id": 65, "soalan": "Siapakah yang menanggung semua perbelanjaan nafkah keluarga?", "pilihan": ["Isteri", "Suami", "Ibu bapa isteri", "Kerajaan"], "jawapan": 1},
            {"id": 66, "soalan": "Hukum membantu suami membuat kerja rumah bagi isteri adalah...", "pilihan": ["Wajib mutlak", "Haram", "Sunat dan amalan terpuji", "Batal nikah"], "jawapan": 2},
            {"id": 67, "soalan": "Talak yang diucapkan secara jelas seperti 'Aku ceraikan kau' dipanggil...", "pilihan": ["Talak Kinayah", "Talak Sarih", "Talak Taklik", "Talak Bad'i"], "jawapan": 1},
            {"id": 68, "soalan": "Talak yang menggunakan perkataan kiasan/sindiran dipanggil...", "pilihan": ["Talak Sarih", "Talak Kinayah (Perlu Niat)", "Talak Raj'i", "Talak Mutlaq"], "jawapan": 1},
            {"id": 69, "soalan": "Talak Kinayah memerlukan kepada...", "pilihan": ["Dua orang saksi terus", "Niat suami semasa melafazkan", "Bayaran mahar", "Persetujuan wali"], "jawapan": 1},
            {"id": 70, "soalan": "Talak yang dilafazkan semasa isteri dalam keadaan suci yang belum disetubuhi dipanggil...", "pilihan": ["Talak Bid'i", "Talak Sunni", "Talak Haram", "Talak Makruh"], "jawapan": 1}
        ]
    },
    "sejarah": [
            {"id": 1, "soalan": "Apakah tarikh kelahiran Nabi Muhammad SAW?", "pilihan": ["17 Ramadan", "12 Rabiulawal", "1 Muharram", "10 Zulhijjah"], "jawapan": 1},
            {"id": 2, "soalan": "Siapakah nama ibu kepada Nabi Muhammad SAW?", "pilihan": ["Khadijah", "Halimah", "Aminah", "Aisyah"], "jawapan": 2},
            {"id": 3, "soalan": "Di manakah tempat lahir Nabi Muhammad SAW?", "pilihan": ["Madinah", "Taif", "Yerusalem", "Makkah"], "jawapan": 3},
            {"id": 4, "soalan": "Siapakah nama bapa kepada Nabi Muhammad SAW?", "pilihan": ["Abu Talib", "Abdul Muttalib", "Abdullah", "Hamzah"], "jawapan": 2},
            {"id": 5, "soalan": "Siapakah nama datuk yang memelihara Nabi Muhammad SAW selepas ibunya meninggal?", "pilihan": ["Abu Talib", "Abdul Muttalib", "Abu Lahab", "Abbas"], "jawapan": 1},
            {"id": 6, "soalan": "Siapakah ibu susuan Nabi Muhammad SAW yang terkenal?", "pilihan": ["Thuwaibah", "Halimatus Sa'diyah", "Ummu Aiman", "Barakah"], "jawapan": 1},
            {"id": 7, "soalan": "Apakah gelaran yang diberikan kepada Nabi Muhammad SAW kerana kejujurannya?", "pilihan": ["Al-Farooq", "As-Siddiq", "Al-Amin", "Saifullah"], "jawapan": 2},
            {"id": 8, "soalan": "Siapakah isteri pertama Nabi Muhammad SAW?", "pilihan": ["Aisyah binti Abu Bakar", "Hafsah binti Umar", "Khadijah binti Khuwailid", "Saudah binti Zam'ah"], "jawapan": 2},
            {"id": 9, "soalan": "Berapakah umur Nabi Muhammad SAW semasa menerima wahyu pertama?", "pilihan": ["25 Tahun", "30 Tahun", "63 Tahun", "40 Tahun"], "jawapan": 3},
            {"id": 10, "soalan": "Di manakah wahyu pertama diturunkan kepada Nabi Muhammad SAW?", "pilihan": ["Gua Hira'", "Gua Thawr", "Masjidil Haram", "Bukit Uhud"], "jawapan": 0},
            {"id": 11, "soalan": "Apakah surah dan ayat pertama yang diturunkan kepada Nabi SAW?", "pilihan": ["Surah Al-Fatiha", "Surah Al-Alaq (Ayat 1-5)", "Surah Al-Baqarah", "Surah Al-Ikhlas"], "jawapan": 1},
            {"id": 12, "soalan": "Siapakah lelaki dewasa pertama yang memeluk Islam?", "pilihan": ["Umar bin Al-Khattab", "Abu Bakar As-Siddiq", "Ali bin Abi Talib", "Uthman bin Affan"], "jawapan": 1},
            {"id": 13, "soalan": "Siapakah kanak-kanak pertama yang memeluk Islam?", "pilihan": ["Zaid bin Harithah", "Ali bin Abi Talib", "Usamah bin Zaid", "Hassan bin Ali"], "jawapan": 1},
            {"id": 14, "soalan": "Siapakah wanita pertama yang memeluk agama Islam?", "pilihan": ["Sumayyah", "Fatimah binti Muhammad", "Khadijah binti Khuwailid", "Aisyah"], "jawapan": 2},
            {"id": 15, "soalan": "Peristiwa perjalanan malam Nabi SAW dari Makkah ke Baitulmaqdis dan naik ke langit dipanggil...", "pilihan": ["Hijrah", "Isra' dan Mi'raj", "Fathul Makkah", "Badar"], "jawapan": 1},
            {"id": 16, "soalan": "Dalam peristiwa Isra' Mi'raj, ibadah apakah yang difardukan secara terus kepada Nabi SAW?", "pilihan": ["Puasa Ramadan", "Solat 5 Waktu", "Zakat", "Haji"], "jawapan": 1},
            {"id": 17, "soalan": "Penghijrahan Nabi Muhammad SAW bersama umat Islam adalah dari Makkah ke...", "pilihan": ["Taif", "Habsyah", "Yathrib (Madinah)", "Syam"], "jawapan": 2},
            {"id": 18, "soalan": "Siapakah sahabat yang menemani Nabi SAW bersembunyi di Gua Thawr semasa Hijrah?", "pilihan": ["Umar bin Al-Khattab", "Abu Bakar As-Siddiq", "Ali bin Abi Talib", "Uthman bin Affan"], "jawapan": 1},
            {"id": 19, "soalan": "Apakah peperangan pertama yang berlaku dalam sejarah Islam pada 17 Ramadan?", "pilihan": ["Perang Uhud", "Perang Badar", "Perang Khandaq", "Perang Hunain"], "jawapan": 1},
            {"id": 20, "soalan": "Dalam Perang Uhud, bapa saudara Nabi SAW yang gugur syahid ialah...", "pilihan": ["Abbas", "Hamzah bin Abdul Muttalib", "Abu Talib", "Ja'far bin Abi Talib"], "jawapan": 1},
            {"id": 21, "soalan": "Strategi menggali parit dalam Perang Khandaq dicadangkan oleh sahabat bernama...", "pilihan": ["Khalid bin Al-Walid", "Abu Ubaidah", "Salman Al-Farisi", "Bilal bin Rabah"], "jawapan": 2},
            {"id": 22, "soalan": "Peristiwa pembukaan semula Kota Makkah tanpa pertumpahan darah dipanggil...", "pilihan": ["Sulh Hudaibiyah", "Fathul Makkah", "Ghazwah Makkah", "Hijrah Makkah"], "jawapan": 1},
            {"id": 23, "soalan": "Siapakah muazin (pelaung azan) pertama dalam Islam?", "pilihan": ["Abdullah bin Ummi Maktum", "Abu Hurairah", "Bilal bin Rabah", "Zaid bin Thabit"], "jawapan": 2},
            {"id": 24, "soalan": "Masjid pertama yang dibina oleh Nabi Muhammad SAW ialah...", "pilihan": ["Masjid Nabawi", "Masjid Quba'", "Masjidil Haram", "Masjid Al-Aqsa"], "jawapan": 1},
            {"id": 25, "soalan": "Anak perempuan Baginda Nabi SAW yang berkahwin dengan Ali bin Abi Talib ialah...", "pilihan": ["Ruqayyah", "Umm Kalthum", "Fatimah Az-Zahra", "Zainab"], "jawapan": 2},
            {"id": 26, "soalan": "Tahun kematian Khadijah R.A dan Abu Talib dikenali dalam sejarah sebagai...", "pilihan": ["Amul Huzni (Tahun Duka Cita)", "Amul Fil (Tahun Gajah)", "Amul Jamaah", "Amul Wufud"], "jawapan": 0},
            {"id": 27, "soalan": "Nabi Muhammad SAW diutus daripada keturunan kaum...", "pilihan": ["Tamim", "Ansar", "Quraisy", "Khazraj"], "jawapan": 2},
            {"id": 28, "soalan": "Perjanjian damai antara pihak Islam Madinah dan Quraisy Makkah dinamakan...", "pilihan": ["Bay'atur Ridwan", "Perjanjian Hudaibiyah", "Piagam Madinah", "Perjanjian Aqabah"], "jawapan": 1},
            {"id": 29, "soalan": "Berapakah umur Nabi Muhammad SAW semasa Baginda wafat?", "pilihan": ["60 Tahun", "65 Tahun", "63 Tahun", "70 Tahun"], "jawapan": 2},
            {"id": 30, "soalan": "Di manakah Makam Baginda Nabi Muhammad SAW terletak sekarang?", "pilihan": ["Masjidil Haram, Makkah", "Masjid Nabawi, Madinah", "Perkuburan Baqi'", "Gua Hira'"], "jawapan": 1},
            {"id": 31, "soalan": "Apakah nama bapa saudara Nabi SAW yang paling keras menentang dakwah Islam?", "pilihan": ["Abu Talib", "Hamzah", "Abu Lahab", "Abbas"], "jawapan": 2},
            {"id": 32, "soalan": "Peristiwa tentera gajah menyerang Kaabah berlaku pada tahun kelahiran Nabi SAW yang dipanggil...", "pilihan": ["Amul Huzni", "Amul Fil (Tahun Gajah)", "Tahun Hijrah", "Tahun Fathul"], "jawapan": 1},
            {"id": 33, "soalan": "Raja Habsyah yang adil dan melindungi umat Islam yang berhijrah ke sana bernama...", "pilihan": ["Raja Najasyi (Negus)", "Raja Heraklius", "Raja Muqawqis", "Raja Kisra"], "jawapan": 0},
            {"id": 34, "soalan": "Siapakah nama sahabat yang digelar 'Al-Farooq' (Pemisah Antara Hak & Batil)?", "pilihan": ["Abu Bakar As-Siddiq", "Umar bin Al-Khattab", "Uthman bin Affan", "Ali bin Abi Talib"], "jawapan": 1},
            {"id": 35, "soalan": "Siapakah sahabat yang digelar 'Zun Nurain' (Pemilik Dua Cahaya)?", "pilihan": ["Ali bin Abi Talib", "Zaid bin Harithah", "Uthman bin Affan", "Talhah bin Ubaidillah"], "jawapan": 2},
            {"id": 36, "soalan": "Siapakah sahabat yang digelar 'Saifullah' (Pedang Allah yang Terhunus)?", "pilihan": ["Hamzah bin Abdul Muttalib", "Sa'ad bin Abi Waqqas", "Abu Ubaidah", "Khalid bin Al-Walid"], "jawapan": 3},
            {"id": 37, "soalan": "Perjanjian taat setia para sahabat kepada Nabi SAW di bawah pokok sebelum Perjanjian Hudaibiyah dipanggil...", "pilihan": ["Piagam Madinah", "Bay'atur Ridwan", "Perjanjian Aqabah", "Bay'at'ul Nisa'"], "jawapan": 1},
            {"id": 38, "soalan": "Sahabat dari kalangan penduduk asal Madinah yang menyambut orang Makkah dipanggil kaum...", "pilihan": ["Muhajirin", "Quraisy", "Ansar", "Khazraj"], "jawapan": 2},
            {"id": 39, "soalan": "Umat Islam dari Makkah yang berhijrah ke Madinah dipanggil kaum...", "pilihan": ["Ansar", "Muhajirin", "Bani Nadhir", "Bani Qainuqa'"], "jawapan": 1},
            {"id": 40, "soalan": "Perlembagaan bertulis pertama di dunia yang digubal oleh Nabi SAW di Madinah ialah...", "pilihan": ["Piagam Makkah", "Perjanjian Taif", "Khutbah Wada'", "Piagam Madinah (Sahifah Madinah)"], "jawapan": 3},
            {"id": 41, "soalan": "Nabi SAW pergi berdakwah ke Kota Taif tetapi dibalas dengan...", "pilihan": ["Sambutan hangat", "Lontaran batu dan penghinaan", "Hadiah emas", "Sokongan tentera"], "jawapan": 1},
            {"id": 42, "soalan": "Nabi Muhammad SAW berkahwin dengan Aisyah R.A yang merupakan anak perempuan kepada...", "pilihan": ["Umar bin Al-Khattab", "Abu Bakar As-Siddiq", "Uthman bin Affan", "Ali bin Abi Talib"], "jawapan": 1},
            {"id": 43, "soalan": "Nabi Muhammad SAW mempunyai berapa orang anak kesemuanya?", "pilihan": ["5 Orang", "7 Orang (3 Lelaki, 4 Perempuan)", "4 Orang", "10 Orang"], "jawapan": 1},
            {"id": 44, "soalan": "Berikut adalah anak-anak lelaki Nabi SAW yang meninggal dunia semasa kecil KECUALI...", "pilihan": ["Qasim", "Abdullah", "Ibrahim", "Hassan"], "jawapan": 3},
            {"id": 45, "soalan": "Perang terakhir yang disertai oleh Nabi Muhammad SAW ialah...", "pilihan": ["Perang Badar", "Perang Uhud", "Perang Tabuk", "Perang Khaibar"], "jawapan": 2},
            {"id": 46, "soalan": "Haji terakhir yang dilaksanakan oleh Baginda Nabi SAW dinamakan...", "pilihan": ["Haji Akbar", "Haji Wada' (Haji Perpisahan)", "Haji Qiran", "Haji Tamattu'"], "jawapan": 1},
            {"id": 47, "soalan": "Khalifah pertama yang memimpin umat Islam selepas kewafatan Nabi SAW ialah...", "pilihan": ["Abu Bakar As-Siddiq", "Umar bin Al-Khattab", "Uthman bin Affan", "Ali bin Abi Talib"], "jawapan": 0},
            {"id": 48, "soalan": "Empat sahabat utama yang memimpin selepas kewafatan Nabi SAW digelar sebagai...", "pilihan": ["Al-Asyarah Al-Mubasysyarun", "Khulafa' Ar-Rasyidin", "Ahlul Bait", "Ansar"], "jawapan": 1},
            {"id": 49, "soalan": "Mukjizat Nabi SAW membelah bulan berlaku untuk membuktikan kenabian kepada kaum...", "pilihan": ["Yahudi Madinah", "Raja Rom", "Parsi", "Musyrikin Quraisy"], "jawapan": 3},
            {"id": 50, "soalan": "Pekerjaan awal Nabi Muhammad SAW semasa zaman remaja bersama bapa saudaranya ialah...", "pilihan": ["Petani", "Pengembala kambing & Peniaga", "Nelayan", "Tukang Besi"], "jawapan": 1}
        ],
    "solat_fardu": [
        {"id": 1, "soalan": "Berapakah jumlah rakaat bagi solat Subuh?", "pilihan": ["3 Rakaat", "2 Rakaat", "4 Rakaat", "5 Rakaat"], "jawapan": 1},
        {"id": 2, "soalan": "Apakah solat fardu yang dikerjakan pada waktu petang?", "pilihan": ["Zohor", "Asar", "Maghrib", "Isyak"], "jawapan": 1},
        {"id": 3, "soalan": "Berapakah rakaat solat Maghrib?", "pilihan": ["2 Rakaat", "4 Rakaat", "3 Rakaat", "1 Rakaat"], "jawapan": 2},
        {"id": 4, "soalan": "Solat fardu manakah yang dikerjakan apabila bayang-bayang objek sama panjang dengan objeknya?", "pilihan": ["Zohor", "Asar", "Maghrib", "Subuh"], "jawapan": 1},
        {"id": 5, "soalan": "Waktu solat Subuh bermula apabila terbit...", "pilihan": ["Matahari", "Fajar Kazib", "Fajar Sadiq", "Bintang"], "jawapan": 2},
        {"id": 6, "soalan": "Solat Zohor, Asar, dan Isyak masing-masing mengandungi berapakah rakaat?", "pilihan": ["3 Rakaat", "2 Rakaat", "5 Rakaat", "4 Rakaat"], "jawapan": 3},
        {"id": 7, "soalan": "Membaca Doa Qunut disunatkan (mengikut Madzhab Syafi'i) pada rakaat kedua solat...", "pilihan": ["Zohor", "Subuh", "Maghrib", "Isyak"], "jawapan": 1},
        {"id": 8, "soalan": "Hukum menunaikan Solat Fardu lima waktu bagi setiap Muslim mukallaf adalah...", "pilihan": ["Fardu Kifayah", "Sunat Muakkad", "Fardu Ain", "Harus"], "jawapan": 2},
        {"id": 9, "soalan": "Seruan atau panggilan menandakan telah masuk waktu solat dinamakan...", "pilihan": ["Iqamah", "Azan", "Takbir", "Tasbih"], "jawapan": 1},
        {"id": 10, "soalan": "Isyarat bahawa solat berjemaah akan dimulakan dipanggil...", "pilihan": ["Azan", "Iqamah", "Khutbah", "Tarhim"], "jawapan": 1},
        {"id": 11, "soalan": "Menghadap ke arah manakah syarat sah solat?", "pilihan": ["Timur", "Barat Daya", "Baitulmaqdis", "Kiblat (Kaabah)"], "jawapan": 3},
        {"id": 12, "soalan": "Perbuatan menyucikan diri daripada hadas kecil dinamakan...", "pilihan": ["Mandi Wajib", "Berwuduk", "Bertayamum", "Beristinja'"], "jawapan": 1},
        {"id": 13, "soalan": "Perbuatan menyucikan diri daripada hadas besar dinamakan...", "pilihan": ["Berwuduk", "Beristinja'", "Mandi Wajib (Janabah)", "Basuh kaki"], "jawapan": 2},
        {"id": 14, "soalan": "Menyembunyikan aurat merupakan salah satu daripada...", "pilihan": ["Rukun Solat", "Syarat Sah Solat", "Sunat Solat", "Perkara membatalkan solat"], "jawapan": 1},
        {"id": 15, "soalan": "Apakah batas aurat lelaki semasa menunaikan solat?", "pilihan": ["Seluruh badan kecuali muka dan tapak tangan", "Dada hingga kaki", "Pusat hingga lutut", "Pusat hingga buku lali"], "jawapan": 2},
        {"id": 16, "soalan": "Apakah batas aurat perempuan semasa menunaikan solat?", "pilihan": ["Pusat hingga lutut", "Seluruh badan kecuali muka dan kedua tapak tangan", "Kepala hingga dada", "Seluruh badan tanpa pengecualian"], "jawapan": 1},
        {"id": 17, "soalan": "Solat fardu secara berkumpulan dengan ada Imam dan Makmum dinamakan...", "pilihan": ["Solat Jamak", "Solat Qasar", "Solat Berjemaah", "Solat Munfarid"], "jawapan": 2},
        {"id": 18, "soalan": "Solat secara bersendirian dinamakan solat...", "pilihan": ["Berjemaah", "Jamak", "Munfarid", "Khauf"], "jawapan": 2},
        {"id": 19, "soalan": "Ganjaran pahala solat berjemaah berbanding solat bersendirian ialah...", "pilihan": ["10 Kali ganda", "27 Kali ganda", "50 Kali ganda", "5 Kali ganda"], "jawapan": 1},
        {"id": 20, "soalan": "Mengerjakan dua solat fardu dalam satu waktu dipanggil solat...", "pilihan": ["Qasar", "Jamak", "Hajat", "Istikharah"], "jawapan": 1},
        {"id": 21, "soalan": "Memendekkan solat 4 rakaat menjadi 2 rakaat semasa musafir dipanggil solat...", "pilihan": ["Jamak", "Witr", "Qasar", "Tahajjud"], "jawapan": 2},
        {"id": 22, "soalan": "Solat apakah yang Boleh di-Qasarkan (dipendekkan rakaatnya)?", "pilihan": ["Subuh dan Maghrib", "Zohor, Asar, dan Isyak", "Semua solat fardu", "Maghrib dan Isyak sahaja"], "jawapan": 1},
        {"id": 23, "soalan": "Mengumpulkan Solat Zohor dan Asar lalu dikerjakan dalam waktu Zohor dipanggil...", "pilihan": ["Jamak Ta'khir", "Qasar", "Jamak Harus", "Jamak Taqdim"], "jawapan": 3},
        {"id": 24, "soalan": "Mengumpulkan Solat Maghrib dan Isyak lalu dikerjakan dalam waktu Isyak dipanggil...", "pilihan": ["Jamak Taqdim", "Jamak Ta'khir", "Qasar Ta'khir", "Solat Qadha'"], "jawapan": 1},
        {"id": 25, "soalan": "Apakah hukum Solat Jumaat bagi setiap lelaki Muslim yang cukup syarat?", "pilihan": ["Fardu Kifayah", "Sunat Muakkad", "Harus", "Fardu Ain"], "jawapan": 3},
        {"id": 26, "soalan": "Berapakah rakaat solat Fardu Jumaat?", "pilihan": ["4 Rakaat", "2 Rakaat", "3 Rakaat", "1 Rakaat"], "jawapan": 1},
        {"id": 27, "soalan": "Syarat utama sebelum mendirikan Solat Jumaat ialah mendengarkan...", "pilihan": ["Ceramah umum", "Bacaan Al-Quran", "Dua Khutbah", "Zikir"], "jawapan": 2},
        {"id": 28, "soalan": "Bercakap-cakap semasa khatib sedang membaca khutbah Jumaat hukumnya...", "pilihan": ["Membatalkan solat Jumaat", "Laghaw (Pahala Jumaat berkurang / Makruh)", "Harus", "Sunat"], "jawapan": 1},
        {"id": 29, "soalan": "Makmum yang terlambat dan tidak sempat membaca Al-Fatihah bersama imam dipanggil makmum...", "pilihan": ["Muwafiq", "Munfarid", "Masbuq", "Lateh"], "jawapan": 2},
        {"id": 30, "soalan": "Makmum yang sempat membaca surah Al-Fatihah dengan sempurna bersama imam dipanggil makmum...", "pilihan": ["Masbuq", "Qada'", "Muwafiq", "Mutaba'ah"], "jawapan": 2},
        {"id": 31, "soalan": "Apakah hukum menunaikan Solat Asar selepas terbenam matahari tanpa keuzuran?", "pilihan": ["Harus", "Haram & Berdosa besar (Perlu Qada')", "Sunat", "Makruh"], "jawapan": 1},
        {"id": 32, "soalan": "Solat yang tidak ada rakaat sunat Ba'diyyah (selepasnya) ialah...", "pilihan": ["Solat Zohor", "Solat Maghrib", "Solat Subuh dan Solat Asar", "Solat Isyak"], "jawapan": 2},
        {"id": 33, "soalan": "Solat sunat yang mengiringi solat fardu (sebelum atau selepas) dipanggil solat sunat...", "pilihan": ["Tahajjud", "Rawatib", "Dhuha", "Witir"], "jawapan": 1},
        {"id": 34, "soalan": "Solat sunat Rawatib sebelum solat fardu dipanggil...", "pilihan": ["Ba'diyyah", "Tarawih", "Qabliyyah", "Tahiyyatul Masjid"], "jawapan": 2},
        {"id": 35, "soalan": "Solat sunat Rawatib selepas solat fardu dipanggil...", "pilihan": ["Qabliyyah", "Witir", "Ba'diyyah", "Dhuha"], "jawapan": 2},
        {"id": 36, "soalan": "Solat sunat menghormati masjid sebaik sahaja masuk ke dalamnya dipanggil...", "pilihan": ["Dhuha", "Tahiyyatul Masjid", "Istikharah", "Awwabin"], "jawapan": 1},
        {"id": 37, "soalan": "Apakah hukum melaungkan Azan bagi solat fardu?", "pilihan": ["Wajib Ain", "Harus", "Sunat Muakkad (Bagi lelaki)", "Makruh"], "jawapan": 2},
        {"id": 38, "soalan": "Lafaz tambahan dalam Azan Subuh 'As-Salatu Khairum Minan Naum' bermaksud...", "pilihan": ["Marilah menuju kejayaan", "Solat itu lebih baik daripada tidur", "Allah Maha Besar", "Masa solat telah tiba"], "jawapan": 1},
        {"id": 39, "soalan": "Solat sunat yang dikerjakan pada waktu pagi apabila matahari terbit anggaran setinggi penggalah ialah...", "pilihan": ["Solat Tahajjud", "Solat Witir", "Solat Tasbih", "Solat Dhuha"], "jawapan": 3},
        {"id": 40, "soalan": "Solat sunat penutup bagi solat-solat malam yang mempunyai bilangan rakaat ganjil dipanggil...", "pilihan": ["Solat Dhuha", "Solat Witir", "Solat Hajat", "Solat Taubat"], "jawapan": 1},
        {"id": 41, "soalan": "Solat sunat yang dikerjakan pada waktu malam selepas bangun daripada tidur dipanggil...", "pilihan": ["Solat Tarawih", "Solat Witir", "Solat Tahajjud", "Solat Dhuha"], "jawapan": 2},
        {"id": 42, "soalan": "Apakah tindakan makmum jika imam tersilap perbuatan dalam solat (bagi lelaki)?", "pilihan": ["Menepuk tangan", "Bercakap menegur imam", "Membaca Al-Fatihah nyaring", "Membaca 'Subhanallah'"], "jawapan": 3},
        {"id": 43, "soalan": "Apakah tindakan makmum perempuan jika imam tersilap dalam solat?", "pilihan": ["Membaca Subhanallah", "Menepuk belakang tangan kanan pada tapak tangan kiri", "Bercakap", "Menjerit"], "jawapan": 1},
        {"id": 44, "soalan": "Solat jenazah mengandungi berapakah bilangan rukun Takbir?", "pilihan": ["2 Kali Takbir", "5 Kali Takbir", "4 Kali Takbir", "3 Kali Takbir"], "jawapan": 2},
        {"id": 45, "soalan": "Adakah terdapat perbuatan Rukuk dan Sujud dalam Solat Jenazah?", "pilihan": ["Ada 2 rukuk", "Tiada (Hanya berdiri dan takbir)", "Ada 4 sujud", "Sama seperti solat biasa"], "jawapan": 1},
        {"id": 46, "soalan": "Membaca doa untuk mayat dalam solat Jenazah dilakukan selepas takbir yang ke-...", "pilihan": ["Pertama", "Kedua", "Ketiga & Keempat", "Ketiga dan Ketujuh"], "jawapan": 2},
        {"id": 47, "soalan": "Membaca Selawat ke atas Nabi SAW dalam solat Jenazah dilakukan selepas takbir yang ke-...", "pilihan": ["Pertama", "Ketiga", "Keempat", "Kedua"], "jawapan": 3},
        {"id": 48, "soalan": "Hukum menguruskan dan menunaikan Solat Jenazah bagi masyarakat Muslim ialah...", "pilihan": ["Fardu Ain", "Fardu Kifayah", "Sunat Muakkad", "Harus"], "jawapan": 1},
        {"id": 49, "soalan": "Jarak perjalanan musafir yang mengharuskan Solat Jamak dan Qasar mengikut mazhab Syafi'i ialah anggaran...", "pilihan": ["10km", "50km", "2 Marhalah (Anggaran 81km - 89km)", "200km"], "jawapan": 2},
        {"id": 50, "soalan": "Tempoh keharusan solat Jamak dan Qasar bagi musafir yang menetap di sesuatu tempat (tidak berniat tinggal tetap) ialah...", "pilihan": ["3 Hari 3 Malam (tidak termasuk hari sampai & keluar)", "1 Hari", "10 Hari", "Seminggu"], "jawapan": 0},
        {"id": 51, "soalan": "Apakah hukum bersuara secara tidak sengaja seperti terbatuk kecil hingga mengeluarkan dua huruf yang difahami maknanya semasa solat?", "pilihan": ["Sunat Sujud Sahwi", "Harus dan dimaafkan", "Makruh tetapi sah", "Membatalkan solat"], "jawapan": 3},
        {"id": 52, "soalan": "Apakah status solat seseorang yang mendapati ada sedikit najis yang dimaafkan (seperti darah nyamuk yang sedikit) pada pakaian selepas selesai solat?", "pilihan": ["Batal dan wajib diulangi", "Sunat sujud sahwi", "Sah dan tidak perlu diulangi", "Harus diulangi jika ada masa"], "jawapan": 2},
        {"id": 53, "soalan": "Apakah tindakan yang betul bagi makmum masbuq jika imam berada dalam keadaan sujud sahwi sebelum salam?", "pilihan": ["Terus berdiri menambah rakaat tanpa ikut sujud", "Duduk menunggu imam selesai salam baru berdiri", "Membaca salam bersama imam", "Ikut sujud bersama imam, kemudian berdiri menambah rakaat"], "jawapan": 3},
        {"id": 54, "soalan": "Makmum yang sempat membaca Al-Fatihah sekadar kadar surah pendek bersama imam sebelum imam rukuk dipanggil...", "pilihan": ["Makmum Masbuq", "Makmum Muwafiq", "Makmum Munfarid", "Makmum Lateh"], "jawapan": 1},
        {"id": 55, "soalan": "Apakah hukum pergerakan anggota kecil (seperti menggerakkan jari jemari semasa bertasbih) berturut-turut lebih 3 kali dalam solat?", "pilihan": ["Membatalkan solat", "Harus dengan niat", "Tidak membatalkan solat", "Sunat sujud sahwi"], "jawapan": 2},
        {"id": 56, "soalan": "Jika seseorang ragu-ragu sama ada dia baru menunaikan 3 atau 4 rakaat dalam Solat Isyak, apakah yang perlu dilakukannya?", "pilihan": ["Batal solat dan mula semula dari rakaat pertama", "Ambil bilangan 3 (yang yakin), tambah 1 rakaat dan disunatkan Sujud Sahwi", "Ambil bilangan 4 dan terus salam", "Tanya makmum di sebelah"], "jawapan": 1},
        {"id": 57, "soalan": "Antara berikut, manakah syarat sah bagi pelaksanaan Solat Jamak Taqdim yang TEPAT?", "pilihan": ["Dilakukan pada bila-bila masa tanpa niat", "Solat kedua mesti didahulukan dari solat pertama", "Boleh berselang masa yang panjang antara dua solat", "Niat jamak mesti ada pada waktu solat pertama & mendahulukan solat waktu pertama"], "jawapan": 3},
        {"id": 58, "soalan": "Apakah hukum mengulangi membaca Surah Al-Fatihah secara sengaja dalam satu rakaat solat?", "pilihan": ["Membatalkan solat terus", "Harus dan mendapat pahala", "Makruh dan disunatkan Sujud Sahwi jika terlupa", "Batal jika tiada niat zikir"], "jawapan": 2},
        {"id": 59, "soalan": "Kawasan manakah yang WAJIB terbuka (tidak terhalang oleh kain/rambut) semasa melakukan sujud?", "pilihan": ["Lutut", "Tapak tangan", "Hujung jari kaki", "Dahi"], "jawapan": 3},
        {"id": 60, "soalan": "Apakah hukum berniat memutus / keluar daripada solat (*Mufaraqah*) semasa sedang bersolat?", "pilihan": ["Batal solatnya serta-merta", "Solat diteruskan seperti biasa", "Sunat sujud sahwi", "Sah tetapi makruh"], "jawapan": 0},
        {"id": 61, "soalan": "Manakah antara berikut TIDAK tergolong dalam Rukun Qawli (Lafaz) yang memerlukan bacaan didengari oleh telinga sendiri?", "pilihan": ["Membaca Doa Iftitah", "Membaca Al-Fatihah", "Takbiratul Ihram", "Membaca Tahiyyat Akhir"], "jawapan": 0},
        {"id": 62, "soalan": "Sekiranya seseorang terlupa membaca Tahiyyat Awal dan terus berdiri tegak untuk rakaat ketiga, apakah tindakan yang betul mengikut Mazhab Syafi'i?", "pilihan": ["Wajib duduk semula membaca Tahiyyat Awal", "Batal solat kerana tertinggal rukun", "Teruskan solat dan lakukan Sujud Sahwi sebelum salam", "Solat sah tanpa perlu Sujud Sahwi"], "jawapan": 2},
        {"id": 63, "soalan": "Apakah hukum mendahului pergerakan Imam sebanyak DUA rukun fi'li secara sengaja tanpa keuzuran?", "pilihan": ["Makruh sahaja", "Sunat mufaraqah", "Harus jika imam terlalu lambat", "Membatalkan solat makmum"], "jawapan": 3},
        {"id": 64, "soalan": "Apakah status solat seseorang yang tersilap menghadap arah yang berlawanan dengan Kiblat tanpa sebarang ijtihad/usaha mencari Kiblat terlebih dahulu?", "pilihan": ["Harus jika tidak tahu", "Tidak sah dan wajib diulangi solatnya", "Sah jika niat betul", "Sah jika dalam bangunan"], "jawapan": 1},
        {"id": 65, "soalan": "Apakah yang dimaksudkan dengan *Waktu Garam* (Waktu Haram Solat Sunat Tanpa Sebab)?", "pilihan": ["Waktu selepas Isyak hingga Subuh", "Waktu antara Zohor dan Asar", "Waktu rembang (Matahari tepat di atas kepala kecuali hari Jumaat)", "Waktu malam sebelum Subuh"], "jawapan": 2},
        {"id": 66, "soalan": "Apakah syarat membolehkan musafir menunaikan solat Jamak dan Qasar mengikut jarak perjalanan?", "pilihan": ["Melebihi 2 Marhalah (kira-kira 81km - 89km)", "Sekurang-kurangnya 30km", "Asalkan keluar dari daerah kediaman", "Melebihi 150km"], "jawapan": 0},
        {"id": 67, "soalan": "Seseorang yang bersolat secara duduk kerana keuzuran, bagaimanakah cara dia melakukan rukun rukuk yang betul?", "pilihan": ["Tunduk sedikit sehingga dahi bertentangan dengan tempat sujud", "Duduk tegak tanpa perlu tunduk", "Tunduk sekadar mana yang munasabah sehingga mukanya melepasi lutut", "Hanya meletakkan tangan di lantai"], "jawapan": 2},
        {"id": 68, "soalan": "Apakah hukum makmum membaca Al-Fatihah semasa Solat Jahriyyah (Solat bacaan nyaring) bagi Mazhab Syafi'i?", "pilihan": ["Haram membaca dan wajib dengar sahaja", "Wajib membaca Al-Fatihah secara perlahan", "Sunat jika ada masa", "Dimaafkan dan tak perlu baca langsung"], "jawapan": 1},
        {"id": 69, "soalan": "Apakah perbezaan utama antara Sujud Sahwi dan Sujud Tilawah dari segi bacaannya?", "pilihan": ["Sujud Tilawah membaca 'Subhana man la yanamu wa la yashu'", "Tiada sebarang bacaan khas", "Sujud Tilawah wajib dibaca secara kuat", "Sujud Sahwi khusus disunatkan membaca 'Subhana man la yanamu wa la yashu'"], "jawapan": 3},
        {"id": 70, "soalan": "Apakah hukum solat bagi orang yang menanggung najis yang tidak dimaafkan pada pakaiannya tetapi dia LUPA atau TIDAK TAHU kewujudan najis tersebut sehingga selesai solat?", "pilihan": ["Sah dan tidak perlu qada", "Wajib diulangi/diqada solatnya mengikut Mazhab Syafi'i", "Sunat sujud sahwi sahaja", "Harus memilih untuk ulangi atau tidak"], "jawapan": 1}
    ]
}

@app.route('/api/wordle-soalan', methods=['GET'])
def get_wordle_soalan():
    all_questions = []
    
    for sub_cat, q_list in QUIZ_DATA.get('rukun', {}).items():
        all_questions.extend(q_list)
    all_questions.extend(QUIZ_DATA.get('sejarah', []))
    all_questions.extend(QUIZ_DATA.get('solat_fardu', []))
    
    valid_wordle = []
    for q in all_questions:
        jawapan_text = q['pilihan'][q['jawapan']]
        clean_word = re.sub(r'\([^)]*\)', '', jawapan_text).strip().upper()
        clean_word = re.sub(r'[^A-Z]', '', clean_word)
        
        # HANYA AMBIL PERKATAAN 3 HINGGA 6 HURUF SAHAJA
        if 3 <= len(clean_word) <= 6:
            valid_wordle.append({
                "soalan": q['soalan'],
                "jawapan": clean_word
            })
            
    return jsonify({"data": valid_wordle})

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
    
    # JIKA MOD SURVIVAL / RAWAK: Kumpulkan semua soalan dari semua kategori
    if kategori == 'survival' or kategori == 'random':
        all_questions = []
        
        # 1. Ambil dari kategori Rukun (termasuk sub-kategori)
        for sub_cat, q_list in QUIZ_DATA.get('rukun', {}).items():
            all_questions.extend(q_list)
            
        # 2. Ambil dari Sejarah
        all_questions.extend(QUIZ_DATA.get('sejarah', []))
        
        # 3. Ambil dari Solat Fardu
        all_questions.extend(QUIZ_DATA.get('solat_fardu', []))
        
        return jsonify({"data": all_questions})

    # Logik biasa untuk kategori spesifik
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
        nama = data.get("nama", "Anon").strip()[:35]
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