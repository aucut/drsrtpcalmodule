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
    st.image("data:image/svg+xml;utf8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20xmlns%3Axlink%3D%22http%3A%2F%2Fwww.w3.org%2F1999%2Fxlink%22%20viewBox%3D%220%200%2018%2023%22%3E%3Cpath%20d%3D%22M%205.276%201.178%20C%205.276%201.827%205.278%202.715%205.282%203.153%20L%205.287%203.95%20L%205.456%203.95%20C%205.817%203.95%206.308%203.994%206.728%204.065%20C%209.273%204.493%2011.505%206.023%2012.829%208.249%20C%2013.516%209.403%2013.93%2010.68%2014.052%2012.018%20C%2014.078%2012.3%2014.086%2012.491%2014.086%2012.826%20C%2014.086%2013.524%2014.026%2014.058%2013.89%2014.604%20C%2013.582%2015.834%2012.874%2016.95%2011.896%2017.747%20C%2011.103%2018.393%2010.159%2018.821%209.156%2018.988%20C%208.853%2019.039%208.642%2019.057%208.31%2019.065%20C%207.694%2019.078%207.197%2019.01%206.706%2018.844%20C%205.665%2018.494%204.817%2017.745%204.337%2016.754%20C%204.122%2016.313%204.002%2015.9%203.941%2015.398%20C%203.921%2015.24%203.914%2014.813%203.927%2014.634%20C%203.952%2014.312%204.014%2014.028%204.125%2013.743%20C%204.537%2012.688%205.477%2011.969%206.602%2011.851%20C%206.745%2011.836%207.066%2011.838%207.21%2011.856%20C%207.569%2011.899%207.898%2012.015%208.19%2012.2%20C%208.458%2012.369%208.706%2012.615%208.885%2012.887%20C%208.955%2012.995%209.078%2013.24%209.123%2013.365%20C%209.165%2013.48%209.212%2013.665%209.232%2013.8%20C%209.255%2013.943%209.263%2014.202%209.25%2014.345%20C%209.197%2014.92%208.899%2015.429%208.432%2015.742%20C%208.264%2015.855%208.031%2015.958%207.836%2016.007%20C%207.609%2016.064%207.299%2016.075%207.075%2016.035%20C%206.878%2015.998%206.649%2015.907%206.504%2015.809%20C%206.483%2015.795%206.467%2015.786%206.467%2015.79%20C%206.467%2015.801%206.548%2015.93%206.593%2015.991%20C%206.877%2016.372%207.281%2016.615%207.744%2016.684%20C%208.228%2016.756%208.801%2016.701%209.31%2016.532%20C%2010.543%2016.121%2011.459%2015.059%2011.682%2013.782%20C%2011.746%2013.419%2011.772%2012.845%2011.744%2012.417%20C%2011.564%209.654%209.704%207.316%207.075%206.553%20C%206.542%206.399%205.906%206.303%205.413%206.303%20L%205.284%206.303%20L%205.284%207.193%20L%205.284%208.082%20L%205.113%208.128%20C%203.424%208.586%201.963%209.68%201.043%2011.177%20C%200.235%2012.493%20-0.106%2014.012%200.038%2015.662%20C%200.163%2017.095%200.677%2018.484%201.518%2019.665%20C%201.932%2020.245%202.449%2020.793%203.016%2021.252%20C%204.151%2022.169%205.542%2022.761%207.002%2022.948%20C%207.37%2022.994%207.369%2022.994%208.127%2022.998%20C%208.876%2023.002%208.937%2023%209.284%2022.96%20C%2012.087%2022.645%2014.627%2021.118%2016.235%2018.782%20C%2017.168%2017.425%2017.75%2015.858%2017.925%2014.222%20C%2018.039%2013.155%2018.021%2012.066%2017.873%2011.022%20C%2017.654%209.489%2017.169%208.018%2016.437%206.668%20C%2015.088%204.18%2012.954%202.211%2010.38%201.075%20C%209.027%200.477%207.568%200.121%206.084%200.026%20C%205.905%200.015%205.504%200%205.374%200%20L%205.276%200%20Z%22%20fill%3D%22rgb(255%2C%20255%2C%20255)%22%3E%3C%2Fpath%3E%3C%2Fsvg%3E", width=100)
    st.title("Dezztech Return System RTP Desteği Hesaplama Modülü")
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

            )

if __name__ == "__main__":
    main()
