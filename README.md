# Qr application py
attendance schedule for schools
🇹🇷 Python Kivy - Öğrenci / Öğretmen QR ve Yoklama Uygulaması

Bu proje, Python Kivy kullanılarak geliştirilmiş bir öğrenci–öğretmen yönetim uygulamasıdır.
Kullanıcılar öğrenci veya öğretmen olarak kayıt olabilir.
Her kullanıcı, veritabanında (SQLite) saklanır ve bilgiler kalıcıdır.

🎯 Özellikler:

Öğretmen ve öğrenci kayıt/giriş sistemi

Öğrenciler, kayıt olduktan sonra öğretmen onayı bekler

Onaylanan öğrenciler kendi QR kodlarını görüntüleyebilir

Öğretmenler sadece kendi öğrencilerini görebilir

Öğrenciler 2 saat içinde onaylanmazsa başvurusu otomatik silinir

Veritabanı: SQLite (okul.db)

Arayüz: Kivy Framework

QR Kod oluşturma: qrcode + Pillow

🧩 Kullanılan Kütüphaneler:
pip install kivy qrcode[pil] pillow

🗂️ Veritabanı Yapısı:

users: kullanıcı adı, şifre, rol (öğretmen / öğrenci)

students: öğrenci kayıtları, öğretmen onayı

attendance: yoklama kayıtları (öğretmen tarafından işlenir)

🚀 Çalıştırma:
python main.py

📱 Planlanan Geliştirmeler:

Yoklama geçmişi görüntüleme

Mobil platforma (Android) paketleme

QR kodla yoklama alma sistemi

🇬🇧 Python Kivy - Student / Teacher QR Attendance App

This project is a Python Kivy-based student–teacher management system.
Users can register as Teacher or Student, and all data is stored permanently using SQLite.

🎯 Features:

Student and teacher registration & login

Students require teacher approval after registration

Approved students can view their personal QR code

Teachers see only their own students

Unapproved student requests auto-delete after 2 hours

Database: SQLite (okul.db)

UI: Kivy Framework

QR Generation: qrcode + Pillow

🧩 Required Libraries:
pip install kivy qrcode[pil] pillow

🚀 Run:
python main.py

📄 Lisans:

Bu proje MIT Lisansı ile yayınlanmıştır.
İsteyen herkes kodu inceleyebilir, değiştirebilir ve kullanabilir.
