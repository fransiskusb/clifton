import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime
import openai  # Untuk interpretasi AI
from google.generativeai import configure, GenerativeModel
import os
from dotenv import load_dotenv
import base64

# Load API Key dari .env atau variabel lingkungan
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("❌ API key tidak ditemukan! Pastikan telah diatur dalam .env atau sebagai variabel lingkungan.")
    st.stop()

# Konfigurasi Google Gemini API
configure(api_key=GOOGLE_API_KEY)
MODEL_NAME = "gemini-1.5-flash"

st.title("CliftonStrengths Quiz")
st.write("Jawab pertanyaan berikut untuk mengetahui kekuatan utama Anda.")

# Input Data Peserta
st.header("Data Peserta")
data_peserta = {
    "Nama Peserta": st.text_input("Nama Peserta"),
    "Nama Perusahaan": st.text_input("Nama Perusahaan"),
    "Tanggal Lahir": st.date_input("Tanggal Lahir"),
    "Tanggal Isi Test": st.date_input("Tanggal Isi Test", datetime.date.today()),
    "Jabatan": st.text_input("Jabatan"),
    "Bagian": st.text_input("Bagian"),
    "Lama Bekerja (tahun)": st.number_input("Lama Bekerja (tahun)", min_value=0, step=1)
}

# Tema Kekuatan CliftonStrengths
themes = [
    "Achiever", "Activator", "Adaptability", "Analytical", "Arranger", "Belief", "Command", "Communication",
    "Competition", "Connectedness", "Consistency", "Context", "Deliberative", "Developer", "Discipline",
    "Empathy", "Focus", "Futuristic", "Harmony", "Ideation", "Includer", "Individualization", "Input",
    "Intellection", "Learner", "Maximizer", "Positivity", "Relator", "Responsibility", "Restorative",
    "Self-Assurance", "Significance", "Strategic", "Woo"
]
theme_scores = {theme: 0 for theme in themes}

# 34 Pertanyaan CliftonStrengths
pertanyaan = [
("Saya merasa puas ketika saya menyelesaikan tugas yang menantang.", "Achiever"),
("Saya sering bekerja keras untuk mencapai tujuan saya.", "Achiever"),
("Saya merasa tidak nyaman jika tidak produktif.", "Achiever"),
("Saya suka memulai tindakan dan membuat sesuatu terjadi.", "Activator"),
("Saya lebih suka bertindak daripada menunggu.", "Activator"),
("Saya merasa bersemangat ketika saya bisa memulai proyek baru.", "Activator"),
("Saya mudah menyesuaikan diri dengan perubahan yang tidak terduga.", "Adaptability"),
("Saya lebih suka tetap fleksibel daripada mengikuti rencana yang ketat.", "Adaptability"),
("Saya bisa tetap tenang dalam situasi yang tidak terduga.", "Adaptability"),
("Saya suka menganalisis data dan mencari pola.", "Analytical"),
("Saya sering mencari bukti sebelum membuat keputusan.", "Analytical"),
("Saya merasa nyaman bekerja dengan angka dan statistik.", "Analytical"),
("Saya senang mengatur dan mengkoordinasikan orang dan sumber daya.", "Arranger"),
("Saya bisa melihat bagaimana potongan-potongan kecil membentuk gambaran besar.", "Arranger"),
("Saya suka mengatur hal-hal agar berjalan lebih efisien.", "Arranger"),
("Saya memiliki keyakinan kuat yang memandu tindakan saya.", "Belief"),
("Saya merasa penting untuk hidup sesuai dengan nilai-nilai saya.", "Belief"),
("Saya termotivasi oleh tujuan yang lebih besar daripada sekadar keuntungan pribadi.", "Belief"),
("Saya tidak takut mengambil alih situasi dan membuat keputusan.", "Command"),
("Saya merasa nyaman memimpin orang lain.", "Command"),
("Saya bisa tegas ketika diperlukan.", "Command"),
("Saya mudah menjelaskan ide-ide saya kepada orang lain.", "Communication"),
("Saya senang berbicara di depan umum.", "Communication"),
("Saya merasa nyaman mempresentasikan ide-ide saya.", "Communication"),
("Saya termotivasi oleh persaingan dan ingin menjadi yang terbaik.", "Competition"),
("Saya suka membandingkan diri saya dengan orang lain.", "Competition"),
("Saya merasa bersemangat ketika saya menang.", "Competition"),
("Saya merasa semua orang dan segala sesuatu saling terhubung.", "Connectedness"),
("Saya percaya bahwa segala sesuatu terjadi karena suatu alasan.", "Connectedness"),
("Saya sering melihat hubungan antara hal-hal yang tampaknya tidak terkait.", "Connectedness")



]

st.header("Pertanyaan")
for idx, (pertanyaan_text, tema) in enumerate(pertanyaan, 1):
    st.markdown(f"**{idx}. {pertanyaan_text}**")  # Menampilkan nomor pertanyaan dengan tebal
    pilihan = st.radio("", ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"], index=2, key=f"q{idx}")
    skor_mapping = {"Sangat Tidak Setuju": 1, "Tidak Setuju": 2, "Netral": 3, "Setuju": 4, "Sangat Setuju": 5}
    theme_scores[tema] += skor_mapping[pilihan]

# Fungsi untuk membuat PDF
def create_pdf(data_peserta, df_scores, interpretasi_ai, grafik_path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Halaman 1: Data Peserta
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Hasil Tes CliftonStrengths", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Data Peserta", ln=True)
    pdf.ln(5)
    for key, value in data_peserta.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
    pdf.ln(10)
    
    # Halaman 2: Interpretasi AI
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Interpretasi AI", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=interpretasi_ai)
    pdf.ln(10)
    
    # Halaman 3: Tabel Hasil Skor
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Hasil Skor Kekuatan", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    pdf.cell(50, 10, txt="Tema", border=1)
    pdf.cell(30, 10, txt="Skor", border=1, ln=True)
    for index, row in df_scores.iterrows():
        pdf.cell(50, 10, txt=row["Tema"], border=1)
        pdf.cell(30, 10, txt=str(row["Skor"]), border=1, ln=True)
    pdf.ln(10)
    
    # Halaman 4: Grafik
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Grafik Hasil Kekuatan", ln=True)
    pdf.ln(5)
    pdf.image(grafik_path, x=10, y=None, w=180)
    pdf.ln(10)
    
    # Footer (Copyright)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, txt="Copyright by PT Konsult Indo Sukses", align='C')
    
    # Simpan PDF
    file_name = f"Hasil_Tes_{data_peserta['Nama Peserta']}_{data_peserta['Nama Perusahaan']}.pdf"
    pdf.output(file_name)
    return file_name

# Fungsi untuk menyimpan grafik Plotly sebagai gambar
def save_plotly_fig(fig, filename):
    fig.write_image(filename)

# Pastikan state untuk status submit ada
if "submit_pressed" not in st.session_state:
    st.session_state.submit_pressed = False

# Tombol Submit
if st.button("Submit"):
    st.session_state.submit_pressed = True  # Menandai bahwa Submit telah ditekan

# Tampilkan input password hanya jika Submit sudah ditekan
if st.session_state.submit_pressed:
    password = st.text_input("Masukkan Password untuk melihat hasil", type="password")

    if password:  # Periksa password hanya jika ada input
        if password == "050402":
            st.success("Password benar! Menampilkan hasil tes...")
        st.header(f"Hasil Tes CliftonStrengths untuk {data_peserta['Nama Peserta']}")
        # Urutkan dan tampilkan hasil skor
        df_scores = pd.DataFrame(list(theme_scores.items()), columns=["Tema", "Skor"])
        df_scores = df_scores.sort_values(by="Skor", ascending=False)

        # Menampilkan grafik
        fig = px.bar(df_scores, x="Skor", y="Tema", orientation="h", title="Hasil Kekuatan CliftonStrengths")
        st.plotly_chart(fig)

        # Interpretasi dengan AI Google Gemini
        prompt = f"Berikan analisis kekuatan dan rekomendasi pekerjaan yang sesuai untuk {data_peserta['Nama Peserta']} berdasarkan skor berikut: {df_scores.to_dict()}"
        
        try:
            model = GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt)
            if response and hasattr(response, 'text'):
                interpretasi_ai = response.text
                st.write("Interpretasi AI:", interpretasi_ai)
            else:
                st.error("Terjadi kesalahan saat mendapatkan interpretasi AI.")
        except Exception as e:
            st.error(f"Error API: {e}")

        # Menampilkan tabel hasil
        st.dataframe(df_scores)

        # Simpan grafik sebagai gambar sementara
        grafik_path = "grafik_hasil.png"
        save_plotly_fig(fig, grafik_path)

        # Buat PDF
        file_name = create_pdf(data_peserta, df_scores, interpretasi_ai, grafik_path)

        # Tampilkan link unduh PDF
        with open(file_name, "rb") as f:
            pdf_data = f.read()
        b64_pdf = base64.b64encode(pdf_data).decode('utf-8')
        st.markdown(
            f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="{file_name}">Unduh Hasil Tes (PDF)</a>',
            unsafe_allow_html=True
        )
    else:
        st.error("Password salah! Harap masukkan password yang benar.")
