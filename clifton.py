import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime
from google.generativeai import configure, GenerativeModel
import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv
import re
import matplotlib.pyplot as plt
import dns.resolver

# Load API Key dari .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
configure(api_key=GOOGLE_API_KEY)
MODEL_NAME = "gemini-1.5-flash"

st.title("CliftonStrengths Quiz")

# Fungsi untuk validasi domain email
def validate_email_domain(email):
    try:
        domain = email.split('@')[1]  # Ambil domain dari email
        # Cek MX record dari domain
        dns.resolver.resolve(domain, 'MX')
        return True
    except (IndexError, dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout):
        return False

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

# Tema Kekuatan CliftonStrengths
themes = [
    "Achiever", "Activator", "Adaptability", "Analytical", "Arranger", "Belief", "Command", "Communication",
    "Competition", "Connectedness", "Consistency", "Context", "Deliberative", "Developer", "Discipline",
    "Empathy", "Focus", "Futuristic", "Harmony", "Ideation", "Includer", "Individualization", "Input",
    "Intellection", "Learner", "Maximizer", "Positivity", "Relator", "Responsibility", "Restorative",
    "Self-Assurance", "Significance", "Strategic", "Woo"
]
theme_scores = {theme: 0 for theme in themes}


# Pertanyaan CliftonStrengths
st.header("Pertanyaan")
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
("Saya sering melihat hubungan antara hal-hal yang tampaknya tidak terkait.", "Connectedness"),
("Saya menghargai keadilan dan memperlakukan semua orang secara setara.", "Consistency"),
("Saya percaya bahwa aturan harus diterapkan secara adil.", "Consistency"),
("Saya merasa tidak nyaman ketika melihat ketidakadilan.", "Consistency"),
("Saya suka mempelajari masa lalu untuk memahami masa kini.", "Context"),
("Saya sering mencari pelajaran dari sejarah.", "Context"),
("Saya merasa memahami masa lalu membantu saya membuat keputusan yang lebih baik.", "Context"),
("Saya berhati-hati dalam membuat keputusan dan menghindari risiko.", "Deliberative"),
("Saya sering mempertimbangkan semua kemungkinan sebelum bertindak.", "Deliberative"),
("Saya merasa lebih nyaman setelah memikirkan sesuatu dengan matang.", "Deliberative"),
("Saya senang membantu orang lain berkembang dan mencapai potensi mereka.", "Developer"),
("Saya merasa puas ketika melihat orang lain tumbuh dan berhasil.", "Developer"),
("Saya suka memberikan umpan balik yang membangun.", "Developer"),
("Saya memiliki rutinitas dan disiplin yang ketat dalam hidup saya.", "Discipline"),
("Saya merasa nyaman dengan jadwal yang terstruktur.", "Discipline"),
("Saya suka merencanakan hari saya dengan detail.", "Discipline"),
("Saya dapat merasakan emosi orang lain dan memahami perasaan mereka.", "Empathy"),
("Saya sering merasakan apa yang orang lain rasakan.", "Empathy"),
("Saya mudah tersentuh oleh cerita orang lain.", "Empathy"),
("Saya dapat tetap fokus pada tujuan utama saya.", "Focus"),
("Saya merasa nyaman ketika memiliki prioritas yang jelas.", "Focus"),
("Saya jarang kehilangan arah dalam pekerjaan saya.", "Focus"),
("Saya sering memikirkan masa depan dan apa yang mungkin terjadi.", "Futuristic"),
("Saya suka membayangkan kemungkinan-kemungkinan baru.", "Futuristic"),
("Saya merasa bersemangat ketika memikirkan masa depan.", "Futuristic"),
("Saya mencari kesepakatan dan menghindari konflik.", "Harmony"),
("Saya merasa tidak nyaman ketika ada ketegangan dalam kelompok.", "Harmony"),
("Saya suka menciptakan lingkungan yang damai.", "Harmony"),
("Saya suka menghasilkan ide-ide baru dan kreatif.", "Ideation"),
("Saya sering melihat solusi yang tidak terlihat oleh orang lain.", "Ideation"),
("Saya merasa bersemangat ketika memikirkan ide-ide baru.", "Ideation"),
("Saya berusaha untuk memasukkan semua orang dalam kelompok.", "Includer"),
("Saya merasa tidak nyaman ketika ada orang yang ditinggalkan.", "Includer"),
("Saya suka memastikan semua orang merasa diterima.", "Includer"),
("Saya tertarik pada keunikan dan perbedaan setiap individu.", "Individualization"),
("Saya suka memahami apa yang membuat setiap orang unik.", "Individualization"),
("Saya merasa senang ketika bisa membantu orang berdasarkan kebutuhan mereka.", "Individualization"),
("Saya suka mengumpulkan informasi dan mempelajari hal-hal baru.", "Input"),
("Saya sering mengumpulkan fakta dan data.", "Input"),
("Saya merasa bersemangat ketika mempelajari sesuatu yang baru.", "Input"),
("Saya suka berpikir mendalam dan merenungkan ide-ide.", "Intellection"),
("Saya sering merenungkan pertanyaan-pertanyaan filosofis.", "Intellection"),
("Saya merasa nyaman ketika bisa berpikir secara mandiri.", "Intellection"),
("Saya selalu ingin belajar dan meningkatkan diri.", "Learner"),
("Saya merasa bersemangat ketika mempelajari hal-hal baru.", "Learner"),
("Saya sering mencari kesempatan untuk berkembang.", "Learner"),
("Saya ingin mengoptimalkan segala sesuatu untuk mencapai hasil terbaik.", "Maximizer"),
("Saya merasa tidak puas dengan hasil yang biasa-biasa saja.", "Maximizer"),
("Saya suka membantu orang lain mencapai potensi terbaik mereka.", "Maximizer"),
("Saya membawa energi positif dan antusiasme ke dalam kelompok.", "Positivity"),
("Saya sering melihat sisi baik dari situasi yang sulit.", "Positivity"),
("Saya suka membuat orang lain merasa senang.", "Positivity"),
("Saya lebih suka hubungan yang mendalam dan bermakna.", "Relator"),
("Saya merasa nyaman dengan lingkaran pertemanan yang kecil.", "Relator"),
("Saya suka membangun hubungan yang tahan lama.", "Relator"),
("Saya merasa bertanggung jawab untuk menyelesaikan tugas yang diberikan kepada saya.", "Responsibility"),
("Saya tidak bisa meninggalkan pekerjaan yang belum selesai.", "Responsibility"),
("Saya merasa penting untuk memenuhi komitmen saya.", "Responsibility"),
("Saya senang memecahkan masalah dan memperbaiki hal-hal yang rusak.", "Restorative"),
("Saya merasa puas ketika bisa memperbaiki sesuatu.", "Restorative"),
("Saya sering melihat solusi untuk masalah yang rumit.", "Restorative"),
("Saya percaya pada kemampuan saya sendiri dan tidak ragu-ragu dalam mengambil keputusan.", "Self-Assurance"),
("Saya merasa yakin dengan pendapat saya.", "Self-Assurance"),
("Saya tidak mudah goyah oleh pendapat orang lain.", "Self-Assurance"),
("Saya ingin diakui dan dihargai atas prestasi saya.", "Significance"),
("Saya merasa penting untuk membuat dampak yang besar.", "Significance"),
("Saya termotivasi oleh pengakuan dari orang lain.", "Significance"),
("Saya dapat melihat pola dan merencanakan strategi untuk mencapai tujuan.", "Strategic"),
("Saya suka memikirkan langkah-langkah untuk mencapai kesuksesan.", "Strategic"),
("Saya merasa nyaman ketika merencanakan masa depan.", "Strategic"),
("Saya senang bertemu orang baru dan membangun hubungan.", "Woo"),
("Saya merasa bersemangat ketika bisa memengaruhi orang lain.", "Woo"),
("Saya suka membuat orang lain merasa nyaman.", "Woo"),
("Saya sering merasa tidak puas sampai saya menyelesaikan tugas.", "Achiever"),
("Saya merasa bersemangat ketika mencapai target.", "Achiever"),
("Saya sering bekerja lebih keras daripada yang diharapkan.", "Achiever"),
("Saya merasa tidak sabar untuk memulai proyek baru.", "Activator"),
("Saya suka mengambil inisiatif.", "Activator"),
("Saya merasa tidak nyaman ketika harus menunggu.", "Activator"),
("Saya bisa tetap tenang dalam situasi yang berubah-ubah.", "Adaptability"),
("Saya merasa nyaman dengan ketidakpastian.", "Adaptability"),
("Saya mudah menyesuaikan diri dengan lingkungan baru.", "Adaptability"),
("Saya suka memecahkan masalah dengan logika.", "Analytical"),
("Saya sering mencari penjelasan yang rasional.", "Analytical"),
("Saya merasa nyaman bekerja dengan data yang kompleks.", "Analytical"),
("Saya suka mengatur hal-hal agar berjalan lancar.", "Arranger"),
("Saya bisa melihat bagaimana potongan-potongan kecil membentuk gambaran besar.", "Arranger"),
("Saya merasa puas ketika semuanya terorganisir dengan baik.", "Arranger"),
("Saya merasa penting untuk hidup sesuai dengan nilai-nilai saya.", "Belief"),
("Saya termotivasi oleh tujuan yang lebih besar.", "Belief"),
("Saya merasa kuat ketika saya bisa hidup sesuai dengan prinsip saya.", "Belief"),
("Saya merasa nyaman memimpin orang lain.", "Command"),
("Saya tidak takut mengambil tanggung jawab.", "Command"),
("Saya bisa tegas ketika diperlukan.", "Command"),
("Saya senang berbicara di depan umum.", "Communication"),
("Saya merasa nyaman mempresentasikan ide-ide saya.", "Communication"),
("Saya mudah menjelaskan hal-hal yang rumit.", "Communication"),
("Saya suka membandingkan diri saya dengan orang lain.", "Competition"),
("Saya merasa bersemangat ketika saya menang.", "Competition"),
("Saya termotivasi oleh persaingan.", "Competition"),
("Saya percaya bahwa segala sesuatu terjadi karena suatu alasan.", "Connectedness"),
("Saya sering melihat hubungan antara hal-hal yang tampaknya tidak terkait.", "Connectedness"),
("Saya merasa semua orang dan segala sesuatu saling terhubung.", "Connectedness"),
("Saya percaya bahwa aturan harus diterapkan secara adil.", "Consistency"),
("Saya merasa tidak nyaman ketika melihat ketidakadilan.", "Consistency"),
("Saya menghargai keadilan.", "Consistency"),
("Saya suka mempelajari masa lalu untuk memahami masa kini.", "Context"),
("Saya sering mencari pelajaran dari sejarah.", "Context"),
("Saya merasa memahami masa lalu membantu saya membuat keputusan yang lebih baik.", "Context"),
("Saya sering mempertimbangkan semua kemungkinan sebelum bertindak.", "Deliberative"),
("Saya merasa lebih nyaman setelah memikirkan sesuatu dengan matang.", "Deliberative"),
("Saya berhati-hati dalam membuat keputusan.", "Deliberative"),
("Saya senang membantu orang lain berkembang.", "Developer"),
("Saya merasa puas ketika melihat orang lain tumbuh.", "Developer"),
("Saya suka memberikan umpan balik yang membangun.", "Developer"),
("Saya memiliki rutinitas yang ketat.", "Discipline"),
("Saya merasa nyaman dengan jadwal yang terstruktur.", "Discipline"),
("Saya suka merencanakan hari saya dengan detail.", "Discipline"),
("Saya sering merasakan apa yang orang lain rasakan.", "Empathy"),
("Saya mudah tersentuh oleh cerita orang lain.", "Empathy"),
("Saya bisa memahami perasaan orang lain.", "Empathy"),
("Saya jarang kehilangan arah dalam pekerjaan saya.", "Focus"),
("Saya merasa nyaman ketika memiliki prioritas yang jelas.", "Focus"),
("Saya bisa tetap fokus pada tujuan utama saya.", "Focus"),
("Saya suka membayangkan kemungkinan-kemungkinan baru.", "Futuristic"),
("Saya merasa bersemangat ketika memikirkan masa depan.", "Futuristic"),
("Saya sering memikirkan masa depan.", "Futuristic"),
("Saya merasa tidak nyaman ketika ada ketegangan dalam kelompok.", "Harmony"),
("Saya suka menciptakan lingkungan yang damai.", "Harmony"),
("Saya mencari kesepakatan dan menghindari konflik.", "Harmony"),
("Saya sering melihat solusi yang tidak terlihat oleh orang lain.", "Ideation"),
("Saya merasa bersemangat ketika memikirkan ide-ide baru.", "Ideation"),
("Saya suka menghasilkan ide-ide kreatif.", "Ideation"),
("Saya merasa tidak nyaman ketika ada orang yang ditinggalkan.", "Includer"),
("Saya suka memastikan semua orang merasa diterima.", "Includer"),
("Saya berusaha untuk memasukkan semua orang dalam kelompok.", "Includer"),
("Saya suka memahami apa yang membuat setiap orang unik.", "Individualization"),
("Saya merasa senang ketika bisa membantu orang berdasarkan kebutuhan mereka.", "Individualization"),
("Saya tertarik pada keunikan setiap individu.", "Individualization"),
("Saya sering mengumpulkan fakta dan data.", "Input"),
("Saya merasa bersemangat ketika mempelajari sesuatu yang baru.", "Input"),
("Saya suka mengumpulkan informasi.", "Input"),
("Saya sering merenungkan pertanyaan-pertanyaan filosofis.", "Intellection"),
("Saya merasa nyaman ketika bisa berpikir secara mandiri.", "Intellection"),
("Saya suka berpikir mendalam.", "Intellection"),
("Saya sering mencari kesempatan untuk berkembang.", "Learner"),
("Saya merasa bersemangat ketika mempelajari hal-hal baru.", "Learner"),
("Saya selalu ingin belajar dan meningkatkan diri.", "Learner")


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
            # Validasi domain email
            if not validate_email_domain(email_penerima):
                st.error("Domain email tidak valid!")
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
    
    # Buat Grafik
    fig, ax = plt.subplots()
    df_scores.plot(kind='bar', x='Tema', y='Skor', ax=ax, legend=False)
    ax.set_ylabel("Skor")
    ax.set_title("Hasil Tes CliftonStrengths")
    plt.tight_layout()
    grafik_file = "grafik.png"
    plt.savefig(grafik_file, format="png")
    plt.close()

    # Buat PDF dengan FPDF
    class PDF(FPDF):
        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.cell(0, 10, "© Copyright by PT Konsult Indo Sukses", 0, 0, "C")

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Hasil Tes CliftonStrengths - {data_peserta['Nama Peserta']}", ln=True, align='C')
    pdf.ln(10)

    # Tabel Data Peserta
    pdf.set_font("Arial", size=10)
    pdf.cell(50, 10, "Informasi Peserta", ln=True)
    for key, value in data_peserta.items():
        pdf.cell(50, 10, key, border=1)
        pdf.cell(0, 10, str(value), border=1, ln=True)
    pdf.ln(10)

    # Interpretasi AI
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, interpretasi_ai)
    pdf.ln(10)

    # Grafik
    pdf.cell(0, 10, "Grafik Hasil Tes", ln=True)
    pdf.image(grafik_file, x=10, w=180)
    pdf.ln(10)

    # Tabel Skor
    pdf.cell(0, 10, "Skor Tema", ln=True)
    for index, row in df_scores.iterrows():
        pdf.cell(50, 10, row["Tema"], border=1)
        pdf.cell(30, 10, str(row["Skor"]), border=1, ln=True)
    pdf.ln(10)

    # Simpan PDF
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
        st.success(f"Pesan telah BERHASIL dikirim ke alamat email {st.session_state.email_penerima}")
    except Exception as e:
        st.error(f"Gagal mengirim email: {e}")
