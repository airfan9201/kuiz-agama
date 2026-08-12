# =========================================================
# TETAPAN REDIS / VERCEL DATABASE (AUTO-DETECT KEY)
# =========================================================
import urllib.parse
import redis
import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

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
            {"id": 50, "soalan": "Syurga tempat ganjaran bagi orang beriman dinamakan...", "pilihan": ["Jannah", "Jahannam", "Barzakh", "Mahsyar"], "jawapan": 0}            
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
            {"id": 50, "soalan": "Ibadah Umrah boleh dikerjakan pada...", "pilihan": ["Bila-bila masa sepanjang tahun", "Bulan Zulhijjah sahaja", "Bulan Ramadan sahaja", "Hari Raya sahaja"], "jawapan": 0}            
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
            {"id": 50, "soalan": "Lafaz 'Sami'Allahu Liman Hamidah' dibaca semasa...", "pilihan": ["Bangkit dari rukuk menuju iktidal", "Mahu sujud", "Semasa rukuk", "Semasa duduk antara dua sujud"], "jawapan": 0}            
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
            {"id": 21, "soalan": "Menyapu air ke seluruh kepala (bukan sebahagian) hukumnya...", "pilihan": ["Sunat", "Rukun", "Membatalkan wuduk", "Haram"], "jawapan": 0},
            {"id": 22, "soalan": "Membaca doa selepas berwuduk hukumnya...", "pilihan": ["Sunat", "Rukun", "Wajib", "Harus"], "jawapan": 0},
            {"id": 23, "soalan": "Mengeringkan anggota wuduk dengan tuala tanpa sebarang hajat hukumnya...", "pilihan": ["Makruh / Harus", "Haram", "Membatalkan wuduk", "Rukun"], "jawapan": 0},
            {"id": 24, "soalan": "Apakah pengganti wuduk sekiranya tiada air atau uzur bertayamum?", "pilihan": ["Debu tanah yang suci", "Pasir pantai", "Batu", "Kain bersih"], "jawapan": 0},
            {"id": 25, "soalan": "Rukun Tayamum mengandungi Niat, Menyapu Muka, Menyapu Tangan hingga siku dan...", "pilihan": ["Tertib", "Menyapu kaki", "Menyapu kepala", "Membasuh telinga"], "jawapan": 0},
            {"id": 26, "soalan": "Menyentuh kemaluan manusia dengan tapak tangan tanpa lapik hukumnya...", "pilihan": ["Membatalkan wuduk", "Tidak membatalkan wuduk", "Sunat wuduk", "Makruh"], "jawapan": 0},
            {"id": 27, "soalan": "Niat wuduk dilafazkan di dalam hati bersamaan semasa air mula menyentuh...", "pilihan": ["Bahagian muka", "Tangan", "Kaki", "Telinga"], "jawapan": 0},
            {"id": 28, "soalan": "Menyilang-nyilang jari tangan dan kaki (Takhlil) semasa wuduk hukumnya...", "pilihan": ["Sunat", "Rukun", "Wajib", "Makruh"], "jawapan": 0},
            {"id": 29, "soalan": "Membazir penggunaan air semasa berwuduk hukumnya...", "pilihan": ["Makruh", "Harus", "Sunat", "Wajib"], "jawapan": 0},
            {"id": 30, "soalan": "Menghadap ke arah mana semasa berwuduk disunatkan?", "pilihan": ["Kiblat", "Timur", "Utara", "Bebas"], "jawapan": 0},
            {"id": 31, "soalan": "Bersiwak (mencuci gigi) sebelum wuduk hukumnya...", "pilihan": ["Sunat", "Rukun", "Wajib", "Makruh"], "jawapan": 0},
            {"id": 32, "soalan": "Membasuh celah-celah jari tangan dan kaki dipanggil...", "pilihan": ["Takhlil", "Istinja'", "Tayammum", "Masah"], "jawapan": 0},
            {"id": 33, "soalan": "Apakah hukum tayamum menggunakan tepung atau debu kotor?", "pilihan": ["Tidak sah", "Sah", "Makruh", "Harus"], "jawapan": 0},
            {"id": 34, "soalan": "Tayamum dilakukan untuk menggantikan wuduk apabila...", "pilihan": ["Ketiadaan air atau sakit yang teruk jika kena air", "Lemas", "Malas mandi", "Masa terlalu banyak"], "jawapan": 0},
            {"id": 35, "soalan": "Niat mandi wajib (mandi janabah) hukumnya...", "pilihan": ["Rukun Mandi", "Sunat Mandi", "Syarat Sah Sahaja", "Harus"], "jawapan": 0},
            {"id": 36, "soalan": "Meratakan air ke seluruh anggota badan dan rambut termasuk dalam rukun...", "pilihan": ["Mandi Wajib", "Wuduk", "Tayamum", "Istinja'"], "jawapan": 0},
            {"id": 37, "soalan": "Sebab yang mewajibkan mandi wajib bagi wanita ialah...", "pilihan": ["Haid, Nifas, dan Wiladah (melahirkan)", "Pening kepala", "Kena hujan", "Peluh berlebihan"], "jawapan": 0},
            {"id": 38, "soalan": "Darah yang keluar dari rahim wanita selepas melahirkan anak dipanggil darah...", "pilihan": ["Nifas", "Haid", "Istihadah", "Fasid"], "jawapan": 0},
            {"id": 39, "soalan": "Darah penyakit yang keluar luar biasa dari rahim wanita dipanggil darah...", "pilihan": ["Istihadah", "Haid", "Nifas", "Wiladah"], "jawapan": 0},
            {"id": 40, "soalan": "Adakah wanita dalam keadaan Haid wajib menqada' (ganti) solat yang ditinggalkan?", "pilihan": ["Tidak Wajib", "Wajib", "Sunat", "Harus"], "jawapan": 0},
            {"id": 41, "soalan": "Adakah wanita dalam keadaan Haid wajib menqada' puasa Ramadan yang ditinggalkan?", "pilihan": ["Wajib Qada'", "Tidak Wajib", "Harus", "Makruh"], "jawapan": 0},
            {"id": 42, "soalan": "Menyucikan najis mutawassitah (sederhana) seperti air kencing dilakukan dengan...", "pilihan": ["Membasuh dengan air suci sehingga hilang bau, warna dan rasa", "Basuh 7 kali dengan tanah", "Lap dengan tisu sahaja", "Jemur di panas matahari"], "jawapan": 0},
            {"id": 43, "soalan": "Najis mughallazah (berat) seperti anjing dan babi disucikan dengan membasuh...", "pilihan": ["7 kali basuhan (1 daripadanya air tanah)", "3 kali basuhan air biasa", "Lap dengan kain kering", "Dengan sabun sahaja"], "jawapan": 0},
            {"id": 44, "soalan": "Najis mukhaffafah (ringan) contohnya air kencing bayi lelaki bawah 2 tahun yang hanya minum susu ibu disucikan dengan...", "pilihan": ["Renjikan air mutlaq pada tempat najis", "Basuh 7 kali dengan tanah", "Mandi wajib", "Basuh dengan sabun"], "jawapan": 0},
            {"id": 45, "soalan": "Membersihkan qubul dan dubur selepas membuang air dipanggil...", "pilihan": ["Istinja'", "Istisqa'", "Istikharah", "Istihadah"], "jawapan": 0},
            {"id": 46, "soalan": "Batu atau tisu boleh digunakan untuk beristinja' sekiranya...", "pilihan": ["Tiada air (dengan syarat-syarat tertentu)", "Bila-bila masa walaupun ada air", "Tidak boleh langsung", "Hanya waktu malam"], "jawapan": 0},
            {"id": 47, "soalan": "Perbuatan memasukkan air ke dalam hidung semasa wuduk dinamakan...", "pilihan": ["Istinsyaq", "Istinja'", "Takhlil", "Iftirasy"], "jawapan": 0},
            {"id": 48, "soalan": "Mengeluarkan air dari hidung selepas memasukkannya dipanggil...", "pilihan": ["Istinthar", "Istinsyaq", "Masah", "Ghasl"], "jawapan": 0},
            {"id": 49, "soalan": "Mengusap balutan (jabirah) atas luka semasa wuduk sebagai ganti basuhan dinamakan...", "pilihan": ["Masah 'Ala Al-Jabirah", "Tayamum", "Istinja'", "Qada'"], "jawapan": 0},
            {"id": 50, "soalan": "Air kencing dan tahi manusia tergolong dalam jenis najis...", "pilihan": ["Mutawassitah", "Mukhaffafah", "Mughallazah", "Ma'fu (Dimaafkan)"], "jawapan": 0}            
        ],
        "rukun_nikah": [
            {"id": 1, "soalan": "Berapakah rukun nikah dalam Islam?", "pilihan": ["4", "5", "6", "7"], "jawapan": 1},
            {"id": 2, "soalan": "Berikut adalah Rukun Nikah KECUALI...", "pilihan": ["Pengantin Lelaki", "Pengantin Perempuan", "Wali", "Hantaran / Kenduri"], "jawapan": 3},
            {"id": 3, "soalan": "Ucapan penyerahan dari pihak wali dipanggil...", "pilihan": ["Ijab", "Kabul", "Sighah", "Khutbah"], "jawapan": 0},
            {"id": 4, "soalan": "Ucapan penerimaan dari pengantin lelaki dipanggil...", "pilihan": ["Kabul", "Ijab", "Niat", "Saksi"], "jawapan": 0},
            {"id": 5, "soalan": "Berapakah bilangan saksi yang wajib ada dalam majlis akad nikah?", "pilihan": ["1 orang", "2 orang lelaki yang adil", "4 orang", "3 orang"], "jawapan": 1},
            {"id": 6, "soalan": "Wali nasab yang paling utama bagi seorang perempuan ialah...", "pilihan": ["Bapa Kandung", "Datuk sebelah bapa", "Abang kandung", "Bapa saudara"], "jawapan": 0},
            {"id": 7, "soalan": "Wali yang dilantik oleh pemerintah untuk menikahkan perempuan yang tiada wali dipanggil...", "pilihan": ["Wali Hakim / Raja", "Wali Mujbir", "Wali Aqrab", "Wali Ab'ad"], "jawapan": 0},
            {"id": 8, "soalan": "Gabungan Ijab dan Kabul dalam akad nikah dinamakan...", "pilihan": ["Sighah", "Mahar", "Walimah", "Khitbah"], "jawapan": 0},
            {"id": 9, "soalan": "Pemberian wajib daripada suami kepada isteri disebabkan pernikahan dinamakan...", "pilihan": ["Mahar (Mas Kahwin)", "Ufti", "Hadiah", "Wang Hantaran"], "jawapan": 0},
            {"id": 10, "soalan": "Apakah hukum memberi Mahar (Mas Kahwin) kepada isteri?", "pilihan": ["Wajib", "Sunat", "Harus", "Makruh"], "jawapan": 0},
            {"id": 11, "soalan": "Apakah hukum mengadakan majlis kenduri kahwin (Walimatul 'Urus)?", "pilihan": ["Sunat Muakkad", "Rukun Nikah", "Wajib Ain", "Harus"], "jawapan": 0},
            {"id": 12, "soalan": "Berikut adalah syarat sah saksi nikah KECUALI...", "pilihan": ["Lelaki", "Islam & Berakal", "Adil", "Mesti berharta"], "jawapan": 3},
            {"id": 13, "soalan": "Wali yang berhak menikahkan anak gadisnya tanpa persetujuannya dahulu (dengan syarat tertentu) dipanggil...", "pilihan": ["Wali Mujbir", "Wali Hakim", "Wali Aqrab", "Wali Fasiq"], "jawapan": 0},
            {"id": 14, "soalan": "Wanita yang haram dikahwini selama-lamanya dipanggil...", "pilihan": ["Mahram", "Muallaf", "Mustahik", "Ajnabi"], "jawapan": 0},
            {"id": 15, "soalan": "Ibu mertua tergolong dalam mahram secara...", "pilihan": ["Perkahwinan (Musaharahi)", "Keturunan (Nusub)", "Penyusuan", "Angkat"], "jawapan": 0},
            {"id": 16, "soalan": "Anak perempuan susuan haram dikahwini disebabkan hubungan...", "pilihan": ["Penyusuan (Rada'ah)", "Keturunan", "Perkahwinan", "Sahabat"], "jawapan": 0},
            {"id": 17, "soalan": "Seseorang lelaki haram berkahwin dengan dua orang adik-beradik perempuan dalam...", "pilihan": ["Satu masa yang sama", "Bila-bila masa", "Masa selepas bercerai", "Masa selepas kematian"], "jawapan": 0},
            {"id": 18, "soalan": "Perempuan yang berada dalam tempoh Idah perkahwinan lain hukum dikahwini adalah...", "pilihan": ["Haram dan Tidak Sah", "Harus", "Sunat", "Makruh"], "jawapan": 0},
            {"id": 19, "soalan": "Apakah syarat utama bagi pengantin lelaki?", "pilihan": ["Islam, lelaki, bukan mahram bakal isteri", "Mesti berpangkat", "Mesti ada rumah sendiri", "Berumur 30 tahun ke atas"], "jawapan": 0},
            {"id": 20, "soalan": "Pinangan dalam Islam dinamakan...", "pilihan": ["Khitbah", "Walimah", "Sighah", "Raddah"], "jawapan": 0},
            {"id": 21, "soalan": "Meminang pinangan orang lain hukumnya...", "pilihan": ["Haram", "Harus", "Sunat", "Makruh"], "jawapan": 0},
            {"id": 22, "soalan": "Talak yang dilafazkan oleh suami dinamakan...", "pilihan": ["Penceraian", "Rujuk", "Fasakh", "Khuluk"], "jawapan": 0},
            {"id": 23, "soalan": "Pembatalan perkahwinan melalui keputusan mahkamah syariah dipanggil...", "pilihan": ["Fasakh", "Talak", "Lian", "Ila'"], "jawapan": 0},
            {"id": 24, "soalan": "Penceraian atas permintaan isteri dengan membayar ganti rugi kepada suami dipanggil...", "pilihan": ["Khuluk (Tebus Talak)", "Fasakh", "Lian", "Zihar"], "jawapan": 0},
            {"id": 25, "soalan": "Kembali semula kepada ikatan pernikahan asal dalam tempoh idah dipanggil...", "pilihan": ["Rujuk", "Nikah semula", "Khitbah", "Ihram"], "jawapan": 0},
            {"id": 26, "soalan": "Tempoh penantian bagi wanita selepas bercerai atau kematian suami dipanggil...", "pilihan": ["Idah", "Ihram", "Istinja'", "Nifas"], "jawapan": 0},
            {"id": 27, "soalan": "Idah bagi wanita bercerai yang masih ada haid ialah...", "pilihan": ["3 kali suci (Quru')", "4 bulan 10 hari", "3 bulan", "Tiada idah"], "jawapan": 0},
            {"id": 28, "soalan": "Idah bagi kematian suami bagi wanita tidak hamil ialah...", "pilihan": ["4 bulan 10 hari", "3 bulan", "100 hari", "1 tahun"], "jawapan": 0},
            {"id": 29, "soalan": "Nafkah zahir yang wajib disediakan oleh suami merangkumi...", "pilihan": ["Makanan, pakaian dan tempat tinggal", "Kereta mewah sahaja", "Barang kemas sahaja", "Wang simpanan sahaja"], "jawapan": 0},
            {"id": 30, "soalan": "Pernyataan 'Sah' selepas akad nikah dilafazkan oleh...", "pilihan": ["Dua orang saksi", "Pengantin perempuan", "Jurukamera", "Tetamu majlis"], "jawapan": 0},
            {"id": 31, "soalan": "Apakah hukum asal Perkahwinan dalam Islam?", "pilihan": ["Harus (Boleh berubah ikut situasi)", "Wajib", "Sunat sahaja", "Haram"], "jawapan": 0},
            {"id": 32, "soalan": "Perkahwinan menjadi WAJIB bagi seseorang yang...", "pilihan": ["Mampu dan bimbang jatuh ke dalam zina", "Tidak mampu dari segi nafkah", "Saja-saja mahu mencuba", "Masih bersekolah"], "jawapan": 0},
            {"id": 33, "soalan": "Perkahwinan menjadi HARAM bagi seseorang yang...", "pilihan": ["Niat untuk menyiksa/mencederakan pasangan", "Tidak ada kerjaya tetap", "Berumur 50 tahun", "Tiada kenderaan"], "jawapan": 0},
            {"id": 34, "soalan": "Talak yang membolehkan suami rujuk semula tanpa akad nikah baharu dalam idah dipanggil...", "pilihan": ["Talak Raj'i (Talak 1 atau 2)", "Talak Ba'in", "Talak 3", "Fasakh"], "jawapan": 0},
            {"id": 35, "soalan": "Talak 3 dipanggil juga sebagai...", "pilihan": ["Talak Ba'in Kubra", "Talak Raj'i", "Talak Sughra", "Khuluk"], "jawapan": 0},
            {"id": 36, "soalan": "Bekas isteri yang dicerai dengan Talak 3 hanya boleh dinikahi semula oleh bekas suami selepas...", "pilihan": ["Kahwin dengan lelaki lain, bersetubuh dan dicerai secara sah serta tamat idah", "Tunggu 3 tahun", "Membayar denda", "Solat taubat"], "jawapan": 0},
            {"id": 37, "soalan": "Suami menyamakan isterinya dengan ibunya (contoh: 'Belakang mu seperti belakang ibuku') dipanggil...", "pilihan": ["Zihar", "Lian", "Ila'", "Khuluk"], "jawapan": 0},
            {"id": 38, "soalan": "Hukuman bagi perbuatan Zihar sebelum suami menyentuh isterinya ialah wajib membayar...", "pilihan": ["Kaffarah Zihar", "Dam", "Fidyah", "Cukai"], "jawapan": 0},
            {"id": 39, "soalan": "Tuduhan zina oleh suami terhadap isteri tanpa 4 orang saksi diikuti sumpah dinamakan...", "pilihan": ["Lian", "Zihar", "Fasakh", "Khuluk"], "jawapan": 0},
            {"id": 40, "soalan": "Sumpah suami tidak akan menyentuh/menyetubuhi isterinya untuk tempoh tertentu dipanggil...", "pilihan": ["Ila'", "Lian", "Zihar", "Rujuk"], "jawapan": 0},
            {"id": 41, "soalan": "Anak yang lahir kurang dari 6 bulan selepas akad nikah dari sudut nasab...", "pilihan": ["Tidak boleh dinasabkan kepada bapa baginya", "Boleh dinasabkan terus", "Dinasabkan kepada wali Hakim", "Menjadi mahram terus"], "jawapan": 0},
            {"id": 42, "soalan": "Tanggungjawab memberi nafkah anak adalah di atas bahu...", "pilihan": ["Bapa Kandung", "Ibu Kandung", "Datuk sebelah ibu", "Kerajaan"], "jawapan": 0},
            {"id": 43, "soalan": "Pemeliharaan anak yang masih kecil selepas penceraian dipanggil...", "pilihan": ["Hadanah", "Nafkah", "Walimah", "Nusyuz"], "jawapan": 0},
            {"id": 44, "soalan": "Hak Hadanah (penjagaan anak kecil) kebiasaannya diutamakan kepada...", "pilihan": ["Ibu Kandung", "Bapa Kandung", "Bapa Saudara", "Jiran"], "jawapan": 0},
            {"id": 45, "soalan": "Perbuatan isteri yang menderhakai suami tanpa alasan munasabah dipanggil...", "pilihan": ["Nusyuz", "Khuluk", "Fasakh", "Lian"], "jawapan": 0},
            {"id": 46, "soalan": "Harta yang diperoleh bersama oleh suami isteri dalam tempoh perkahwinan dipanggil...", "pilihan": ["Harta Sepencarian", "Mahar", "Harta Pusaka", "Hibah"], "jawapan": 0},
            {"id": 47, "soalan": "Pemberian harta secara sukarela semasa hidup tanpa balasan dipanggil...", "pilihan": ["Hibah", "Wasiat", "Faraid", "Zakat"], "jawapan": 0},
            {"id": 48, "soalan": "Pengurusan pembahagian harta pusaka orang Islam mengikut syarak dipanggil...", "pilihan": ["Faraid", "Hibah", "Wasiat", "Nazar"], "jawapan": 0},
            {"id": 49, "soalan": "Had maksimum kadar Wasiat yang boleh diberikan kepada bukan ahli waris ialah...", "pilihan": ["1/3 daripada keseluruhan harta", "1/2 daripada harta", "Semua harta", "1/4 daripada harta"], "jawapan": 0},
            {"id": 50, "soalan": "Sebab utama pertalian mahram perkahwinan terbahagi kepada 3 iaitu Keturunan, Penyusuan, dan...", "pilihan": ["Musahararah (Perkahwinan)", "Persekolahan", "Angkat", "Persahabatan"], "jawapan": 0}            
        ]
    },
    "sejarah": [
        {"id": 1, "soalan": "Apakah tarikh kelahiran Nabi Muhammad SAW?", "pilihan": ["12 Rabiulawal", "17 Ramadan", "1 Muharram", "10 Zulhijjah"], "jawapan": 0},
        {"id": 2, "soalan": "Siapakah nama ibu kepada Nabi Muhammad SAW?", "pilihan": ["Khadijah", "Aminah", "Halimah", "Aisyah"], "jawapan": 1},
        {"id": 3, "soalan": "Di manakah tempat lahir Nabi Muhammad SAW?", "pilihan": ["Madinah", "Taif", "Makkah", "Yerusalem"], "jawapan": 2},
        {"id": 4, "soalan": "Siapakah nama bapa kepada Nabi Muhammad SAW?", "pilihan": ["Abu Talib", "Abdullah", "Abdul Muttalib", "Hamzah"], "jawapan": 1},
        {"id": 5, "soalan": "Siapakah nama datuk yang memelihara Nabi Muhammad SAW selepas ibunya meninggal?", "pilihan": ["Abdul Muttalib", "Abu Talib", "Abu Lahab", "Abbas"], "jawapan": 0},
        {"id": 6, "soalan": "Siapakah ibu susuan Nabi Muhammad SAW yang terkenal?", "pilihan": ["Halimatus Sa'diyah", "Thuwaibah", "Ummu Aiman", "Barakah"], "jawapan": 0},
        {"id": 7, "soalan": "Apakah gelaran yang diberikan kepada Nabi Muhammad SAW kerana kejujurannya?", "pilihan": ["Al-Amin", "Al-Farooq", "As-Siddiq", "Saifullah"], "jawapan": 0},
        {"id": 8, "soalan": "Siapakah isteri pertama Nabi Muhammad SAW?", "pilihan": ["Khadijah binti Khuwailid", "Aisyah binti Abu Bakar", "Hafsah binti Umar", "Saudah binti Zam'ah"], "jawapan": 0},
        {"id": 9, "soalan": "Berapakah umur Nabi Muhammad SAW semasa menerima wahyu pertama?", "pilihan": ["25 Tahun", "30 Tahun", "40 Tahun", "63 Tahun"], "jawapan": 2},
        {"id": 10, "soalan": "Di manakah wahyu pertama diturunkan kepada Nabi Muhammad SAW?", "pilihan": ["Gua Hira'", "Gua Thawr", "Masjidil Haram", "Bukit Uhud"], "jawapan": 0},
        {"id": 11, "soalan": "Apakah surah dan ayat pertama yang diturunkan kepada Nabi SAW?", "pilihan": ["Surah Al-Alaq (Ayat 1-5)", "Surah Al-Fatiha", "Surah Al-Baqarah", "Surah Al-Ikhlas"], "jawapan": 0},
        {"id": 12, "soalan": "Siapakah lelaki dewasa pertama yang memeluk Islam?", "pilihan": ["Abu Bakar As-Siddiq", "Umar bin Al-Khattab", "Ali bin Abi Talib", "Uthman bin Affan"], "jawapan": 0},
        {"id": 13, "soalan": "Siapakah kanak-kanak pertama yang memeluk Islam?", "pilihan": ["Ali bin Abi Talib", "Zaid bin Harithah", "Usamah bin Zaid", "Hassan bin Ali"], "jawapan": 0},
        {"id": 14, "soalan": "Siapakah wanita pertama yang memeluk agama Islam?", "pilihan": ["Khadijah binti Khuwailid", "Sumayyah", "Fatimah binti Muhammad", "Aisyah"], "jawapan": 0},
        {"id": 15, "soalan": "Peristiwa perjalanan malam Nabi SAW dari Makkah ke Baitulmaqdis dan naik ke langit dipanggil...", "pilihan": ["Isra' dan Mi'raj", "Hijrah", "Fathul Makkah", "Badar"], "jawapan": 0},
        {"id": 16, "soalan": "Dalam peristiwa Isra' Mi'raj, ibadah apakah yang difardukan secara terus kepada Nabi SAW?", "pilihan": ["Solat 5 Waktu", "Puasa Ramadan", "Zakat", "Haji"], "jawapan": 0},
        {"id": 17, "soalan": "Penghijrahan Nabi Muhammad SAW bersama umat Islam adalah dari Makkah ke...", "pilihan": ["Yathrib (Madinah)", "Taif", "Habsyah", "Syam"], "jawapan": 0},
        {"id": 18, "soalan": "Siapakah sahabat yang menemani Nabi SAW bersembunyi di Gua Thawr semasa Hijrah?", "pilihan": ["Abu Bakar As-Siddiq", "Umar bin Al-Khattab", "Ali bin Abi Talib", "Uthman bin Affan"], "jawapan": 0},
        {"id": 19, "soalan": "Apakah peperangan pertama yang berlaku dalam sejarah Islam pada 17 Ramadan?", "pilihan": ["Perang Badar", "Perang Uhud", "Perang Khandaq", "Perang Hunain"], "jawapan": 0},
        {"id": 20, "soalan": "Dalam Perang Uhud, bapa saudara Nabi SAW yang gugur syahid ialah...", "pilihan": ["Hamzah bin Abdul Muttalib", "Abbas", "Abu Talib", "Ja'far bin Abi Talib"], "jawapan": 0},
        {"id": 21, "soalan": "Strategi menggali parit dalam Perang Khandaq dicadangkan oleh sahabat bernama...", "pilihan": ["Salman Al-Farisi", "Khalid bin Al-Walid", "Abu Ubaidah", "Bilal bin Rabah"], "jawapan": 0},
        {"id": 22, "soalan": "Peristiwa pembukaan semula Kota Makkah tanpa pertumpahan darah dipanggil...", "pilihan": ["Fathul Makkah", "Sulh Hudaibiyah", "Ghazwah Makkah", "Hijrah Makkah"], "jawapan": 0},
        {"id": 23, "soalan": "Siapakah muazin (pelaung azan) pertama dalam Islam?", "pilihan": ["Bilal bin Rabah", "Abdullah bin Ummi Maktum", "Abu Hurairah", "Zaid bin Thabit"], "jawapan": 0},
        {"id": 24, "soalan": "Masjid pertama yang dibina oleh Nabi Muhammad SAW ialah...", "pilihan": ["Masjid Quba'", "Masjid Nabawi", "Masjidil Haram", "Masjid Al-Aqsa"], "jawapan": 0},
        {"id": 25, "soalan": "Anak perempuan Baginda Nabi SAW yang berkahwin dengan Ali bin Abi Talib ialah...", "pilihan": ["Fatimah Az-Zahra", "Ruqayyah", "Umm Kalthum", "Zainab"], "jawapan": 0},
        {"id": 26, "soalan": "Tahun kematian Khadijah R.A dan Abu Talib dikenali dalam sejarah sebagai...", "pilihan": ["Amul Huzni (Tahun Duka Cita)", "Amul Fil (Tahun Gajah)", "Amul Jamaah", "Amul Wufud"], "jawapan": 0},
        {"id": 27, "soalan": "Nabi Muhammad SAW diutus daripada keturunan kaum...", "pilihan": ["Quraisy", "Tamim", "Ansar", "Khazraj"], "jawapan": 0},
        {"id": 28, "soalan": "Perjanjian damai antara pihak Islam Madinah dan Quraisy Makkah dinamakan...", "pilihan": ["Perjanjian Hudaibiyah", "Bay'atur Ridwan", "Piagam Madinah", "Perjanjian Aqabah"], "jawapan": 0},
        {"id": 29, "soalan": "Berapakah umur Nabi Muhammad SAW semasa Baginda wafat?", "pilihan": ["63 Tahun", "60 Tahun", "65 Tahun", "70 Tahun"], "jawapan": 0},
        {"id": 30, "soalan": "Di manakah Makam Baginda Nabi Muhammad SAW terletak sekarang?", "pilihan": ["Masjid Nabawi, Madinah", "Masjidil Haram, Makkah", "Perkuburan Baqi'", "Gua Hira'"], "jawapan": 0},
        {"id": 31, "soalan": "Apakah nama bapa saudara Nabi SAW yang paling keras menentang dakwah Islam?", "pilihan": ["Abu Lahab", "Abu Talib", "Hamzah", "Abbas"], "jawapan": 0},
        {"id": 32, "soalan": "Peristiwa tentera gajah menyerang Kaabah berlaku pada tahun kelahiran Nabi SAW yang dipanggil...", "pilihan": ["Amul Fil (Tahun Gajah)", "Amul Huzni", "Tahun Hijrah", "Tahun Fathul"], "jawapan": 0},
        {"id": 33, "soalan": "Raja Habsyah yang adil dan melindungi umat Islam yang berhijrah ke sana bernama...", "pilihan": ["Raja Najasyi (Negus)", "Raja Heraklius", "Raja Muqawqis", "Raja Kisra"], "jawapan": 0},
        {"id": 34, "soalan": "Siapakah nama sahabat yang digelar 'Al-Farooq' (Pemisah Antara Hak & Batil)?", "pilihan": ["Umar bin Al-Khattab", "Abu Bakar As-Siddiq", "Uthman bin Affan", "Ali bin Abi Talib"], "jawapan": 0},
        {"id": 35, "soalan": "Siapakah sahabat yang digelar 'Zun Nurain' (Pemilik Dua Cahaya)?", "pilihan": ["Uthman bin Affan", "Ali bin Abi Talib", "Zaid bin Harithah", "Talhah bin Ubaidillah"], "jawapan": 0},
        {"id": 36, "soalan": "Siapakah sahabat yang digelar 'Saifullah' (Pedang Allah yang Terhunus)?", "pilihan": ["Khalid bin Al-Walid", "Hamzah bin Abdul Muttalib", "Sa'ad bin Abi Waqqas", "Abu Ubaidah"], "jawapan": 0},
        {"id": 37, "soalan": "Perjanjian taat setia para sahabat kepada Nabi SAW di bawah pokok sebelum Perjanjian Hudaibiyah dipanggil...", "pilihan": ["Bay'atur Ridwan", "Piagam Madinah", "Perjanjian Aqabah", "Bay'at'ul Nisa'"], "jawapan": 0},
        {"id": 38, "soalan": "Sahabat dari kalangan penduduk asal Madinah yang menyambut orang Makkah dipanggil kaum...", "pilihan": ["Ansar", "Muhajirin", "Quraisy", "Khazraj"], "jawapan": 0},
        {"id": 39, "soalan": "Umat Islam dari Makkah yang berhijrah ke Madinah dipanggil kaum...", "pilihan": ["Muhajirin", "Ansar", "Bani Nadhir", "Bani Qainuqa'"], "jawapan": 0},
        {"id": 40, "soalan": "Perlembagaan bertulis pertama di dunia yang digubal oleh Nabi SAW di Madinah ialah...", "pilihan": ["Piagam Madinah (Sahifah Madinah)", "Piagam Makkah", "Perjanjian Taif", "Khutbah Wada'"], "jawapan": 0},
        {"id": 41, "soalan": "Nabi SAW pergi berdakwah ke Kota Taif tetapi dibalas dengan...", "pilihan": ["Lontaran batu dan penghinaan", "Sambutan hangat", "Hadiah emas", "Sokongan tentera"], "jawapan": 0},
        {"id": 42, "soalan": "Nabi Muhammad SAW berkahwin dengan Aisyah R.A yang merupakan anak perempuan kepada...", "pilihan": ["Abu Bakar As-Siddiq", "Umar bin Al-Khattab", "Uthman bin Affan", "Ali bin Abi Talib"], "jawapan": 0},
        {"id": 43, "soalan": "Nabi Muhammad SAW mempunyai berapa orang anak kesemuanya?", "pilihan": ["7 Orang (3 Lelaki, 4 Perempuan)", "5 Orang", "4 Orang", "10 Orang"], "jawapan": 0},
        {"id": 44, "soalan": "Berikut adalah anak-anak lelaki Nabi SAW yang meninggal dunia semasa kecil KECUALI...", "pilihan": ["Hassan", "Qasim", "Abdullah", "Ibrahim"], "jawapan": 0},
        {"id": 45, "soalan": "Perang terakhir yang disertai oleh Nabi Muhammad SAW ialah...", "pilihan": ["Perang Tabuk", "Perang Badar", "Perang Uhud", "Perang Khaibar"], "jawapan": 0},
        {"id": 46, "soalan": "Haji terakhir yang dilaksanakan oleh Baginda Nabi SAW dinamakan...", "pilihan": ["Haji Wada' (Haji Perpisahan)", "Haji Akbar", "Haji Qiran", "Haji Tamattu'"], "jawapan": 0},
        {"id": 47, "soalan": "Khalifah pertama yang memimpin umat Islam selepas kewafatan Nabi SAW ialah...", "pilihan": ["Abu Bakar As-Siddiq", "Umar bin Al-Khattab", "Uthman bin Affan", "Ali bin Abi Talib"], "jawapan": 0},
        {"id": 48, "soalan": "Empat sahabat utama yang memimpin selepas kewafatan Nabi SAW digelar sebagai...", "pilihan": ["Khulafa' Ar-Rasyidin", "Al-Asyarah Al-Mubasysyarun", "Ahlul Bait", "Ansar"], "jawapan": 0},
        {"id": 49, "soalan": "Mukjizat Nabi SAW membelah bulan berlaku untuk membuktikan kenabian kepada kaum...", "pilihan": ["Musyrikin Quraisy", "Yahudi Madinah", "Raja Rom", "Parsi"], "jawapan": 0},
        {"id": 50, "soalan": "Pekerjaan awal Nabi Muhammad SAW semasa zaman remaja bersama bapa saudaranya ialah...", "pilihan": ["Pengembala kambing & Peniaga", "Petani", "Nelayan", "Tukang Besi"], "jawapan": 0}        
    ],
    "solat_fardu": [
        {"id": 1, "soalan": "Berapakah jumlah rakaat bagi solat Subuh?", "pilihan": ["2 Rakaat", "3 Rakaat", "4 Rakaat", "5 Rakaat"], "jawapan": 0},
        {"id": 2, "soalan": "Apakah solat fardu yang dikerjakan pada waktu petang?", "pilihan": ["Zohor", "Asar", "Maghrib", "Isyak"], "jawapan": 1},
        {"id": 3, "soalan": "Berapakah rakaat solat Maghrib?", "pilihan": ["3 Rakaat", "2 Rakaat", "4 Rakaat", "1 Rakaat"], "jawapan": 0},
        {"id": 4, "soalan": "Solat fardu manakah yang dikerjakan apabila bayang-bayang objek sama panjang dengan objeknya?", "pilihan": ["Asar", "Zohor", "Maghrib", "Subuh"], "jawapan": 0},
        {"id": 5, "soalan": "Waktu solat Subuh bermula apabila terbit...", "pilihan": ["Fajar Sadiq", "Matahari", "Fajar Kazib", "Bintang"], "jawapan": 0},
        {"id": 6, "soalan": "Solat Zohor, Asar, dan Isyak masing-masing mengandungi berapakah rakaat?", "pilihan": ["4 Rakaat", "3 Rakaat", "2 Rakaat", "5 Rakaat"], "jawapan": 0},
        {"id": 7, "soalan": "Membaca Doa Qunut disunatkan (mengikut Madzhab Syafi'i) pada rakaat kedua solat...", "pilihan": ["Subuh", "Zohor", "Maghrib", "Isyak"], "jawapan": 0},
        {"id": 8, "soalan": "Hukum menunaikan Solat Fardu lima waktu bagi setiap Muslim mukallaf adalah...", "pilihan": ["Fardu Ain", "Fardu Kifayah", "Sunat Muakkad", "Harus"], "jawapan": 0},
        {"id": 9, "soalan": "Seruan atau panggilan menandakan telah masuk waktu solat dinamakan...", "pilihan": ["Azan", "Iqamah", "Takbir", "Tasbih"], "jawapan": 0},
        {"id": 10, "soalan": "Isyarat bahawa solat berjemaah akan dimulakan dipanggil...", "pilihan": ["Iqamah", "Azan", "Khutbah", "Tarhim"], "jawapan": 0},
        {"id": 11, "soalan": "Menghadap ke arah manakah syarat sah solat?", "pilihan": ["Kiblat (Kaabah)", "Timur", "Barat Daya", "Baitulmaqdis"], "jawapan": 0},
        {"id": 12, "soalan": "Perbuatan menyucikan diri daripada hadas kecil dinamakan...", "pilihan": ["Berwuduk", "Mandi Wajib", "Bertayamum", "Beristinja'"], "jawapan": 0},
        {"id": 13, "soalan": "Perbuatan menyucikan diri daripada hadas besar dinamakan...", "pilihan": ["Mandi Wajib (Janabah)", "Berwuduk", "Beristinja'", "Basuh kaki"], "jawapan": 0},
        {"id": 14, "soalan": "Menyembunyikan aurat merupakan salah satu daripada...", "pilihan": ["Syarat Sah Solat", "Rukun Solat", "Sunat Solat", "Perkara membatalkan solat"], "jawapan": 0},
        {"id": 15, "soalan": "Apakah batas aurat lelaki semasa menunaikan solat?", "pilihan": ["Pusat hingga lutut", "Seluruh badan kecuali muka dan tapak tangan", "Dada hingga kaki", "Pusat hingga buku lali"], "jawapan": 0},
        {"id": 16, "soalan": "Apakah batas aurat perempuan semasa menunaikan solat?", "pilihan": ["Seluruh badan kecuali muka dan kedua tapak tangan", "Pusat hingga lutut", "Kepala hingga dada", "Seluruh badan tanpa pengecualian"], "jawapan": 0},
        {"id": 17, "soalan": "Solat fardu secara berkumpulan dengan ada Imam dan Makmum dinamakan...", "pilihan": ["Solat Berjemaah", "Solat Jamak", "Solat Qasar", "Solat Munfarid"], "jawapan": 0},
        {"id": 18, "soalan": "Solat secara bersendirian dinamakan solat...", "pilihan": ["Munfarid", "Berjemaah", "Jamak", "Khauf"], "jawapan": 0},
        {"id": 19, "soalan": "Ganjaran pahala solat berjemaah berbanding solat bersendirian ialah...", "pilihan": ["27 Kali ganda", "10 Kali ganda", "50 Kali ganda", "5 Kali ganda"], "jawapan": 0},
        {"id": 20, "soalan": "Mengerjakan dua solat fardu dalam satu waktu dipanggil solat...", "pilihan": ["Jamak", "Qasar", "Hajat", "Istikharah"], "jawapan": 0},
        {"id": 21, "soalan": "Memendekkan solat 4 rakaat menjadi 2 rakaat semasa musafir dipanggil solat...", "pilihan": ["Qasar", "Jamak", "Witr", "Tahajjud"], "jawapan": 0},
        {"id": 22, "soalan": "Solat apakah yang Boleh di-Qasarkan (dipendekkan rakaatnya)?", "pilihan": ["Zohor, Asar, dan Isyak", "Subuh dan Maghrib", "Semua solat fardu", "Maghrib dan Isyak sahaja"], "jawapan": 0},
        {"id": 23, "soalan": "Mengumpulkan Solat Zohor dan Asar lalu dikerjakan dalam waktu Zohor dipanggil...", "pilihan": ["Jamak Taqdim", "Jamak Ta'khir", "Qasar", "Jamak Harus"], "jawapan": 0},
        {"id": 24, "soalan": "Mengumpulkan Solat Maghrib dan Isyak lalu dikerjakan dalam waktu Isyak dipanggil...", "pilihan": ["Jamak Ta'khir", "Jamak Taqdim", "Qasar Ta'khir", "Solat Qadha'"], "jawapan": 0},
        {"id": 25, "soalan": "Apakah hukum Solat Jumaat bagi setiap lelaki Muslim yang cukup syarat?", "pilihan": ["Fardu Ain", "Fardu Kifayah", "Sunat Muakkad", "Harus"], "jawapan": 0},
        {"id": 26, "soalan": "Berapakah rakaat solat Fardu Jumaat?", "pilihan": ["2 Rakaat", "4 Rakaat", "3 Rakaat", "1 Rakaat"], "jawapan": 0},
        {"id": 27, "soalan": "Syarat utama sebelum mendirikan Solat Jumaat ialah mendengarkan...", "pilihan": ["Dua Khutbah", "Ceramah umum", "Bacaan Al-Quran", "Zikir"], "jawapan": 0},
        {"id": 28, "soalan": "Bercakap-cakap semasa khatib sedang membaca khutbah Jumaat hukumnya...", "pilihan": ["Laghaw (Pahala Jumaat berkurang / Makruh)", "Membatalkan solat Jumaat", "Harus", "Sunat"], "jawapan": 0},
        {"id": 29, "soalan": "Makmum yang terlambat dan tidak sempat membaca Al-Fatihah bersama imam dipanggil makmum...", "pilihan": ["Masbuq", "Muwafiq", "Munfarid", "Lateh"], "jawapan": 0},
        {"id": 30, "soalan": "Makmum yang sempat membaca surah Al-Fatihah dengan sempurna bersama imam dipanggil makmum...", "pilihan": ["Muwafiq", "Masbuq", "Qada'", "Mutaba'ah"], "jawapan": 0},
        {"id": 31, "soalan": "Apakah hukum menunaikan Solat Asar selepas terbenam matahari tanpa keuzuran?", "pilihan": ["Haram & Berdosa besar (Perlu Qada')", "Harus", "Sunat", "Makruh"], "jawapan": 0},
        {"id": 32, "soalan": "Solat yang tidak ada rakaat sunat Ba'diyyah (selepasnya) ialah...", "pilihan": ["Solat Subuh dan Solat Asar", "Solat Zohor", "Solat Maghrib", "Solat Isyak"], "jawapan": 0},
        {"id": 33, "soalan": "Solat sunat yang mengiringi solat fardu (sebelum atau selepas) dipanggil solat sunat...", "pilihan": ["Rawatib", "Tahajjud", "Dhuha", "Witir"], "jawapan": 0},
        {"id": 34, "soalan": "Solat sunat Rawatib sebelum solat fardu dipanggil...", "pilihan": ["Qabliyyah", "Ba'diyyah", "Tarawih", "Tahiyyatul Masjid"], "jawapan": 0},
        {"id": 35, "soalan": "Solat sunat Rawatib selepas solat fardu dipanggil...", "pilihan": ["Ba'diyyah", "Qabliyyah", "Witir", "Dhuha"], "jawapan": 0},
        {"id": 36, "soalan": "Solat sunat menghormati masjid sebaik sahaja masuk ke dalamnya dipanggil...", "pilihan": ["Tahiyyatul Masjid", "Dhuha", "Istikharah", "Awwabin"], "jawapan": 0},
        {"id": 37, "soalan": "Apakah hukum melaungkan Azan bagi solat fardu?", "pilihan": ["Sunat Muakkad (Bagi lelaki)", "Wajib Ain", "Harus", "Makruh"], "jawapan": 0},
        {"id": 38, "soalan": "Lafaz tambahan dalam Azan Subuh 'As-Salatu Khairum Minan Naum' bermaksud...", "pilihan": ["Solat itu lebih baik daripada tidur", "Marilah menuju kejayaan", "Allah Maha Besar", "Masa solat telah tiba"], "jawapan": 0},
        {"id": 39, "soalan": "Solat sunat yang dikerjakan pada waktu pagi apabila matahari terbit anggaran setinggi penggalah ialah...", "pilihan": ["Solat Dhuha", "Solat Tahajjud", "Solat Witir", "Solat Tasbih"], "jawapan": 0},
        {"id": 40, "soalan": "Solat sunat penutup bagi solat-solat malam yang mempunyai bilangan rakaat ganjil dipanggil...", "pilihan": ["Solat Witir", "Solat Dhuha", "Solat Hajat", "Solat Taubat"], "jawapan": 0},
        {"id": 41, "soalan": "Solat sunat yang dikerjakan pada waktu malam selepas bangun daripada tidur dipanggil...", "pilihan": ["Solat Tahajjud", "Solat Tarawih", "Solat Witir", "Solat Dhuha"], "jawapan": 0},
        {"id": 42, "soalan": "Apakah tindakan makmum jika imam tersilap perbuatan dalam solat (bagi lelaki)?", "pilihan": ["Membaca 'Subhanallah'", "Menepuk tangan", "Bercakap menegur imam", "Membaca Al-Fatihah nyaring"], "jawapan": 0},
        {"id": 43, "soalan": "Apakah tindakan makmum perempuan jika imam tersilap dalam solat?", "pilihan": ["Menepuk belakang tangan kanan pada tapak tangan kiri", "Membaca Subhanallah", "Bercakap", "Menjerit"], "jawapan": 0},
        {"id": 44, "soalan": "Solat jenazah mengandungi berapakah bilangan rukun Takbir?", "pilihan": ["4 Kali Takbir", "2 Kali Takbir", "5 Kali Takbir", "3 Kali Takbir"], "jawapan": 0},
        {"id": 45, "soalan": "Adakah terdapat perbuatan Rukuk dan Sujud dalam Solat Jenazah?", "pilihan": ["Tiada (Hanya berdiri dan takbir)", "Ada 2 rukuk", "Ada 4 sujud", "Sama seperti solat biasa"], "jawapan": 0},
        {"id": 46, "soalan": "Membaca doa untuk mayat dalam solat Jenazah dilakukan selepas takbir yang ke-...", "pilihan": ["Ketiga dan Ketujuh", "Pertama", "Kedua", "Ketiga & Keempat"], "jawapan": 3},
        {"id": 47, "soalan": "Membaca Selawat ke atas Nabi SAW dalam solat Jenazah dilakukan selepas takbir yang ke-...", "pilihan": ["Kedua", "Pertama", "Ketiga", "Keempat"], "jawapan": 0},
        {"id": 48, "soalan": "Hukum menguruskan dan menunaikan Solat Jenazah bagi masyarakat Muslim ialah...", "pilihan": ["Fardu Kifayah", "Fardu Ain", "Sunat Muakkad", "Harus"], "jawapan": 0},
        {"id": 49, "soalan": "Jarak perjalanan musafir yang mengharuskan Solat Jamak dan Qasar mengikut mazhab Syafi'i ialah anggaran...", "pilihan": ["2 Marhalah (Anggaran 81km - 89km)", "10km", "50km", "200km"], "jawapan": 0},
        {"id": 50, "soalan": "Tempoh keharusan solat Jamak dan Qasar bagi musafir yang menetap di sesuatu tempat (tidak berniat tinggal tetap) ialah...", "pilihan": ["3 Hari 3 Malam (tidak termasuk hari sampai & keluar)", "1 Hari", "10 Hari", "Seminggu"], "jawapan": 0}        
    ]
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