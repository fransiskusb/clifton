import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime
import openai
from google.generativeai import configure, GenerativeModel
import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv
import re

# Load API Key dari .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
configure(api_key=GOOGLE_API_KEY)
MODEL_NAME = "gemini-1.5-flash"

st.title("CliftonStrengths Quiz")

# Input Data Peserta
st.header("Data Peserta")
data_peserta = {
    "Nama Peserta": st.text_input("Nama Peserta"),
    "Nama Perusahaan": st.text_input("Nama Perusahaan"),
    "Tanggal Lahir": st.date_input("Tanggal Lahir"),
    "Tanggal Isi Test": st.date_input("Tanggal Isi Test", datetime.date.today()),
    "Jabatan": st.text_input("Jabatan"),
    "Bagian": st.text_input("Bagian"),
    "Lama Bekerja (tahun)": st.number_input("Lama Bekerja (tahun)", min_value=0, step=1),
    "Lama Bekerja (bulan)": st.number_input("Lama Bekerja (bulan)", min_value=0, max_value=11, step=1)
}

# Pertanyaan CliftonStrengths
st.header("Pertanyaan")
themes = {"Achiever": 0, "Activator": 0, "Adaptability": 0, "Analytical": 0, "Arranger": 0}
pertanyaan = [
    ("Saya merasa puas ketika menyelesaikan tugas yang menantang.", "Achiever"),
    ("Saya suka memulai tindakan dan membuat sesuatu terjadi.", "Activator"),
    ("Saya mudah menyesuaikan diri dengan perubahan yang tidak terduga.", "Adaptability"),
    ("Saya suka menganalisis data dan mencari pola.", "Analytical"),
    ("Saya senang mengatur dan mengkoordinasikan sumber daya.", "Arranger")
]

skor_mapping = {"Sangat Tidak Setuju": 1, "Tidak Setuju": 2, "Netral": 3, "Setuju": 4, "Sangat Setuju": 5}
theme_scores = {tema: 0 for _, tema in pertanyaan}

for idx, (pertanyaan_text, tema) in enumerate(pertanyaan, 1):
    st.markdown(f"**{idx}. {pertanyaan_text}**")
    pilihan = st.radio("", skor_mapping.keys(), index=2, key=f"q{idx}")
    theme_scores[tema] += skor_mapping[pilihan]

# Submit tombol
if st.button("Submit"):
    st.session_state.show_email_input = True  # Tampilkan input email dan tombol kirim email

# Tampilkan input email dan tombol kirim email jika tombol Submit ditekan
if st.session_state.get("show_email_input", False):
    email_penerima = st.text_input("Masukkan Email untuk menerima hasil tes")
    if st.button("Kirim Email"):
        # Validasi format email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email_penerima):
            st.error("Format email tidak valid!")
        else:
            st.session_state.email_valid = True  # Set email valid
            st.session_state.email_penerima = email_penerima  # Simpan email penerima

# Tampilkan input password jika email valid
if st.session_state.get("email_valid", False):
    password = st.text_input("Masukkan Password untuk verifikasi", type="password")
    if st.button("Verifikasi Password"):
        if password == "050402":  # Ganti dengan password yang sesuai
            st.session_state.password_valid = True  # Set password valid
        else:
            st.error("Password salah! Email tidak dikirim.")

# Kirim email jika email dan password valid
if st.session_state.get("password_valid", False):
    df_scores = pd.DataFrame(theme_scores.items(), columns=["Tema", "Skor"]).sort_values(by="Skor", ascending=False)
    
    # Interpretasi AI
    prompt = f"Analisis kekuatan untuk {data_peserta['Nama Peserta']} berdasarkan skor: {df_scores.to_dict()}"
    model = GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)
    interpretasi_ai = response.text if response and hasattr(response, 'text') else "Interpretasi tidak tersedia"
    
    # Buat PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Hasil Tes CliftonStrengths - {data_peserta['Nama Peserta']}", ln=True, align='C')
    pdf.ln(10)
    for key, value in data_peserta.items():
        pdf.cell(200, 10, f"{key}: {value}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, interpretasi_ai)
    pdf.ln(10)
    for index, row in df_scores.iterrows():
        pdf.cell(50, 10, row["Tema"], border=1)
        pdf.cell(30, 10, str(row["Skor"]), border=1, ln=True)
    pdf.ln(10)
    pdf.cell(0, 10, "© Copyright by PT Konsult Indo Sukses", align='C')
    file_name = f"Hasil_Tes_{data_peserta['Nama Peserta']}_{data_peserta['Nama Perusahaan']}.pdf"
    pdf.output(file_name)
    
    # Kirim Email
    sender_email = "konsulties@gmail.com"
    sender_password = "ipgj wjed dlku trdq"  # Ganti dengan password dari environment variable
    msg = EmailMessage()
    msg['From'] = sender_email
    msg['To'] = st.session_state.email_penerima
    msg['Subject'] = f"Hasil Tes CliftonStrengths - {data_peserta['Nama Peserta']}"
    msg.set_content(f"Dear {data_peserta['Nama Peserta']},\n\nBerikut hasil tes Anda.\n\nSalam,\nPT Konsult Indo Sukses")
    with open(file_name, "rb") as f:
        file_data = f.read()
        msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        st.success(f"Hasil tes berhasil dikirim ke {st.session_state.email_penerima}")
    except Exception as e:
        st.error(f"Gagal mengirim email: {e}")
