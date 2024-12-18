import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def calculate_rtp_and_roi(initial_rtp, withdraw_amounts, roi_rates, support_rate, months, delay_months):
    """
    RTP, ROI ve devlet katkısı hesaplama fonksiyonu.

    Args:
        initial_rtp (float): İlk ay RTP yatırım miktarı.
        withdraw_amounts (list): Her ay için geri alınacak tutar (₺).
        roi_rates (list): Her ay için ROI oranları.
        support_rate (float): Destek oranı.
        months (list): Ay isimleri.
        delay_months (int): Destek gelirinin eklenmeye başlayacağı ay sayısı.

    Returns:
        pd.DataFrame: Tüm hesaplanan değerleri içeren tablo.
    """
    num_months = len(months)
    roi_values = [0] * num_months       # ROI miktarları
    support_income = [0] * num_months   # Destek gelirleri
    next_rtp_investments = [0] * num_months  # Bir sonraki ay RTP yatırım miktarları
    total_investments = [0] * num_months  # Toplam RTP yatırım miktarları
    support_included = ["Hayır"] * num_months  # Destek dahil mi?
    profit = [0] * num_months  # Kar miktarı

    # İlk ayın hesaplamaları
    roi_values[0] = initial_rtp * roi_rates[0]
    support_income[0] = initial_rtp * support_rate
    next_rtp_investments[0] = roi_values[0] - withdraw_amounts[0]
    total_investments[0] = initial_rtp
    profit[0] = roi_values[0] + support_income[0] - withdraw_amounts[0]

    for i in range(1, num_months):
        # ROI hesapla (önceki ayın RTP üzerinden)
        roi_values[i] = next_rtp_investments[i - 1] * roi_rates[i]

        # Devlet katkısını hesapla
        support_income[i] = next_rtp_investments[i - 1] * support_rate

        # Bir sonraki ay RTP yatırım miktarını belirle
        if i < delay_months:
            # Gecikme süresi boyunca devlet katkısı eklenmez
            next_rtp_investments[i] = roi_values[i] - withdraw_amounts[i]
            support_included[i] = "Hayır"
        else:
            # Gecikme süresi sonrasında devlet katkısı eklenir
            next_rtp_investments[i] = roi_values[i] + support_income[i - delay_months] - withdraw_amounts[i]
            support_included[i] = "Evet"

        total_investments[i] = next_rtp_investments[i - 1]
        profit[i] = roi_values[i] + (support_income[i - delay_months] if i >= delay_months else 0) - withdraw_amounts[i]

    data = {
        "Aylar": months,
        "Aylık RTP Yatırım Miktarı (₺)": total_investments,
        "ROI Oranı": roi_rates,
        "ROI Miktarı (₺)": roi_values,
        "Destek Geliri (₺)": support_income,
        "Destek Dahil": support_included,
        "Kar (₺)": profit
    }

    df = pd.DataFrame(data)
    df.loc['Toplam'] = df.sum(numeric_only=True).fillna('')
    df.at['Toplam', 'Aylar'] = 'Toplam'
    df.at['Toplam', 'Destek Dahil'] = ''
    df.at['Toplam', 'ROI Oranı'] = ''

    return df

def create_pdf(df, fig):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Tabloyu ekle
    text = c.beginText(40, height - 40)
    text.setFont("Helvetica", 10)
    for col in df.columns:
        text.textLine(f"{col}: {', '.join(map(str, df[col].values))}")
    c.drawText(text)

    # Grafiği ekle
    img_buffer = BytesIO()
    fig.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    c.drawImage(img_buffer, 40, height - 300, width=500, preserveAspectRatio=True, mask='auto')

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# Streamlit Form
def main():
    st.title("Dezztech Return System
Reklam Tanıtım Pazarlama Desteği
Hesaplama Modülü")
    st.write("Bu araç, RTP yatırımı, ROI ve devlet katkısını hesaplar.")

    # Kullanıcıdan giriş alın
    initial_rtp = st.number_input("İlk Ay RTP Yatırım Miktarı (₺)", min_value=0.0, value=100000.0, step=1000.0, format="%.2f")
    support_rate = st.number_input("Destek Oranı", min_value=0.0, value=0.6, step=0.1, format="%.2f")
    num_months = st.number_input("Kaç Ay İçin Hesaplama Yapılacak?", min_value=1, value=12, step=1)
    delay_months = st.number_input("Destek Gelirinin Eklenmeye Başlayacağı Ay Sayısı", min_value=1, value=4, step=1)

    # Ay isimlerini oluştur
    all_month_names = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    months = [all_month_names[i % 12] for i in range(num_months)]

    # Geri alınacak tutarları ve ROI oranlarını kullanıcıdan alın
    withdraw_amounts = []
    roi_rates = []
    for i in range(num_months):
        withdraw_amounts.append(
            st.number_input(f"{months[i]} ayında geri alınacak tutar (₺)", min_value=0.0, value=0.0, step=1000.0, format="%.2f", key=f"withdraw_{i}")
        )
        roi_rates.append(
            st.number_input(f"{months[i]} için ROI Oranı", min_value=0.0, value=1.5, step=0.1, format="%.2f", key=f"roi_{i}")
        )

    # Hesaplama ve Sonuç Gösterimi
    if st.button("Hesapla"):
        results = calculate_rtp_and_roi(initial_rtp, withdraw_amounts, roi_rates, support_rate, months, delay_months)
        st.subheader("Sonuçlar")
        st.dataframe(results)  # Sonuçları tablo olarak göster

        # Toplamları hesapla
        total_roi = results["ROI Miktarı (₺)"].sum()
        total_support = results["Destek Geliri (₺)"].sum()
        total_investment = results["Aylık RTP Yatırım Miktarı (₺)"].sum()
        total_profit = results["Kar (₺)"].sum()

        st.write(f"Toplam ROI Miktarı: {total_roi:,.2f} ₺")
        st.write(f"Toplam Destek Geliri: {total_support:,.2f} ₺")
        st.write(f"Toplam Yatırım Miktarı: {total_investment:,.2f} ₺")
        st.write(f"Toplam Kar: {total_profit:,.2f} ₺")

        # Grafikler oluştur
        fig, ax = plt.subplots(3, 1, figsize=(10, 15))

        ax[0].plot(results["Aylar"], results["ROI Miktarı (₺)"], marker='o')
        ax[0].set_title("Aylık ROI Miktarı")
        ax[0].set_xlabel("Aylar")
        ax[0].set_ylabel("ROI Miktarı (₺)")

        ax[1].plot(results["Aylar"], results["Destek Geliri (₺)"], marker='o', color='orange')
        ax[1].set_title("Aylık Destek Geliri")
        ax[1].set_xlabel("Aylar")
        ax[1].set_ylabel("Destek Geliri (₺)")

        ax[2].plot(results["Aylar"], results["Kar (₺)"], marker='o', color='green')
        ax[2].set_title("Aylık Kar")
        ax[2].set_xlabel("Aylar")
        ax[2].set_ylabel("Kar (₺)")

        st.pyplot(fig)

        # PDF oluşturma butonu
        if st.button("PDF Olarak Kaydet"):
            pdf_buffer = create_pdf(results, fig)
            st.download_button(
                label="PDF İndir",
                data=pdf_buffer,
                file_name="rapor.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()
