from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
import qrcode
import sqlite3
from datetime import datetime, timedelta
import os

# -------------------- VERİTABANI --------------------
DB_NAME = "okul.db"


def db_olustur():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT,
                active INTEGER DEFAULT 0
            )
        ''')
        ...
        conn.commit()
        conn.close()


def db_baglanti():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    return conn, c


# -------------------- KULLANICI İŞLEMLERİ --------------------
def kullanici_ekle(username, password, role):
    conn, c = db_baglanti()
    try:
        active = 1 if role == "Öğretmen" else 0
        c.execute("INSERT INTO users (username, password, role, active) VALUES (?, ?, ?, ?)",
                  (username, password, role, active))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def kullanici_giris(username, password, role):
    conn, c = db_baglanti()
    c.execute("SELECT id, active FROM users WHERE username=? AND password=? AND role=?",
              (username, password, role))
    sonuc = c.fetchone()
    conn.close()
    if sonuc:
        return sonuc
    return None, None


def ogrenci_basvuru(student_name, teacher_name):
    conn, c = db_baglanti()
    c.execute("SELECT id FROM users WHERE username=? AND role='Öğretmen'", (teacher_name,))
    teacher = c.fetchone()
    if not teacher:
        conn.close()
        return False, "Öğretmen bulunamadı"
    teacher_id = teacher[0]
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO students (teacher_id, student_name, created_at) VALUES (?, ?, ?)",
              (teacher_id, student_name, created_at))
    conn.commit()
    conn.close()
    return True, "Başvuru yapıldı, 2 saat içinde onay bekleniyor"


def bekleyen_ogrenciler(teacher_id):
    conn, c = db_baglanti()
    iki_saat_once = (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
    c.execute("DELETE FROM students WHERE active=0 AND created_at <= ?", (iki_saat_once,))
    conn.commit()
    c.execute("SELECT id, student_name FROM students WHERE teacher_id=? AND active=0", (teacher_id,))
    sonuc = c.fetchall()
    conn.close()
    return sonuc


def ogrenci_onayla(student_id):
    conn, c = db_baglanti()
    c.execute("UPDATE students SET active=1 WHERE id=?", (student_id,))
    conn.commit()
    conn.close()


def aktif_ogrenci(student_name):
    conn, c = db_baglanti()
    c.execute("SELECT student_name FROM students WHERE student_name=? AND active=1", (student_name,))
    sonuc = c.fetchone()
    conn.close()
    return bool(sonuc)


# -------------------- KAYIT EKRANI --------------------
class KayitEkrani(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(Label(text="Kayıt Ol", font_size=28, size_hint_y=None, height=50))
        self.k_adi = TextInput(hint_text="Kullanıcı Adı", size_hint_y=None, height=50)
        self.sifre = TextInput(hint_text="Şifre", password=True, size_hint_y=None, height=50)
        layout.add_widget(self.k_adi)
        layout.add_widget(self.sifre)
        self.rol_sec = Spinner(text="Rol Seçin", values=["Öğrenci", "Öğretmen"], size_hint_y=None, height=50)
        layout.add_widget(self.rol_sec)
        self.ogretmen_input = TextInput(hint_text="Öğrenciysen Öğretmen Adı", size_hint_y=None, height=50)
        layout.add_widget(self.ogretmen_input)
        self.mesaj = Label(text="", font_size=16, size_hint_y=None, height=30)
        layout.add_widget(self.mesaj)
        kayit_btn = Button(text="Kaydol / Başvur", size_hint_y=None, height=50)
        kayit_btn.bind(on_press=self.kaydol)
        layout.add_widget(kayit_btn)
        giris_btn = Button(text="Zaten hesabın var mı? Giriş Yap", size_hint_y=None, height=50)
        giris_btn.bind(on_press=lambda x: setattr(self.manager, "current", "giris"))
        layout.add_widget(giris_btn)
        self.add_widget(layout)

    def kaydol(self, instance):
        kadi = self.k_adi.text.strip()
        sifre = self.sifre.text.strip()
        rol = self.rol_sec.text.strip()
        ogretmen = self.ogretmen_input.text.strip()
        if not kadi or (rol == "Öğretmen" and not sifre) or rol == "Rol Seçin":
            self.mesaj.text = "⚠️ Tüm alanları doldurun"
            return
        if rol == "Öğrenci":
            success, msg = ogrenci_basvuru(kadi, ogretmen)
            self.mesaj.text = msg
        else:
            basarili = kullanici_ekle(kadi, sifre, rol)
            self.mesaj.text = "✅ Öğretmen kaydı başarılı!" if basarili else "❌ Bu kullanıcı adı zaten var!"


# -------------------- GİRİŞ --------------------
class GirisEkrani(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(Label(text="Giriş Yap", font_size=28, size_hint_y=None, height=50))
        self.k_adi = TextInput(hint_text="Kullanıcı Adı", size_hint_y=None, height=50)
        self.sifre = TextInput(hint_text="Şifre (Öğrenci boş bırakabilir)", password=True, size_hint_y=None, height=50)
        layout.add_widget(self.k_adi)
        layout.add_widget(self.sifre)
        self.rol_sec = Spinner(text="Rol Seçin", values=["Öğrenci", "Öğretmen"], size_hint_y=None, height=50)
        layout.add_widget(self.rol_sec)
        self.mesaj = Label(text="", font_size=16, size_hint_y=None, height=30)
        layout.add_widget(self.mesaj)
        giris_btn = Button(text="Giriş Yap", size_hint_y=None, height=50)
        giris_btn.bind(on_press=self.giris_yap)
        layout.add_widget(giris_btn)
        kayit_btn = Button(text="Hesabın yok mu? Kayıt Ol", size_hint_y=None, height=50)
        kayit_btn.bind(on_press=lambda x: setattr(self.manager, "current", "kayit"))
        layout.add_widget(kayit_btn)
        self.add_widget(layout)

    def giris_yap(self, instance):
        kadi = self.k_adi.text.strip()
        rol = self.rol_sec.text.strip()
        if rol == "Öğrenci":
            if aktif_ogrenci(kadi):
                qr_screen = self.manager.get_screen("qr")
                qr_screen.aktif_kullanici = (kadi, rol)
                self.manager.current = "qr"
            else:
                self.mesaj.text = "⚠️ Onay bekleniyor veya 2 saat geçti"
        else:
            sifre = self.sifre.text.strip()
            user_id, active = kullanici_giris(kadi, sifre, rol)
            if user_id:
                qr_screen = self.manager.get_screen("qr")
                qr_screen.aktif_kullanici = (kadi, rol)
                self.manager.current = "qr"
            else:
                self.mesaj.text = "❌ Kullanıcı adı/şifre yanlış!"


# -------------------- QR EKRANI --------------------
class QREkrani(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.aktif_kullanici = None
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        self.add_widget(self.layout)

    def on_enter(self, *args):
        self.layout.clear_widgets()
        kullanici, rol = self.aktif_kullanici
        self.layout.add_widget(
            Label(text=f"Hoşgeldiniz, {kullanici} ({rol})", font_size=24, size_hint_y=None, height=50))

        if rol == "Öğrenci":
            qr_img = qrcode.make(kullanici).convert("RGB")
            self.qr_resim = Image(size_hint=(0.5, 0.5), allow_stretch=True)
            self.layout.add_widget(self.qr_resim)
            self.qr_olustur(qr_img)
        else:
            self.layout.add_widget(Label(text="Öğretmen Paneli", font_size=20, size_hint_y=None, height=30))
            conn, c = db_baglanti()
            c.execute("SELECT id FROM users WHERE username=? AND role='Öğretmen'", (kullanici,))
            teacher_id = c.fetchone()[0]
            conn.close()

            self.bekleyen_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
            self.bekleyen_layout.bind(minimum_height=self.bekleyen_layout.setter('height'))
            scroll_bekleyen = ScrollView(size_hint=(1, 0.4))
            scroll_bekleyen.add_widget(self.bekleyen_layout)
            self.layout.add_widget(Label(text="Bekleyen Öğrenciler:"))
            self.layout.add_widget(scroll_bekleyen)
            self.guncelle_bekleyen_listesi(teacher_id)

            qr_img = qrcode.make(kullanici).convert("RGB")
            self.qr_resim = Image(size_hint=(0.5, 0.5), allow_stretch=True)
            self.layout.add_widget(Label(text="Sizin QR Kodunuz:"))
            self.layout.add_widget(self.qr_resim)
            self.qr_olustur(qr_img)

    def qr_olustur(self, qr_img):
        buf = qr_img.tobytes()
        w, h = qr_img.size
        texture = Texture.create(size=(w, h))
        texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        texture.flip_vertical()
        self.qr_resim.texture = texture

    def guncelle_bekleyen_listesi(self, teacher_id):
        self.bekleyen_layout.clear_widgets()
        bekleyenler = bekleyen_ogrenciler(teacher_id)
        if not bekleyenler:
            self.bekleyen_layout.add_widget(Label(text="Bekleyen öğrenci yok"))
        else:
            for sid, sname in bekleyenler:
                box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
                box.add_widget(Label(text=sname))
                btn = Button(text="Onayla", size_hint_x=0.3)
                btn.bind(on_press=lambda inst, x=sid: self.onayla(x, teacher_id))
                box.add_widget(btn)
                self.bekleyen_layout.add_widget(box)

    def onayla(self, student_id, teacher_id):
        ogrenci_onayla(student_id)
        self.guncelle_bekleyen_listesi(teacher_id)


# -------------------- UYGULAMA --------------------
class QRApp(App):
    def build(self):
        db_olustur()
        sm = ScreenManager()
        sm.add_widget(KayitEkrani(name="kayit"))
        sm.add_widget(GirisEkrani(name="giris"))
        sm.add_widget(QREkrani(name="qr"))
        return sm

if __name__ == "__main__":
    QRApp().run()
