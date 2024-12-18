import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def calculate_rtp_and_roi(initial_rtp, withdraw_amounts, roi_rate, support_rate, months, delay_months):
    """
    RTP, ROI ve devlet katkısı hesaplama fonksiyonu.

    Args:
        initial_rtp (float): İlk ay RTP yatırım miktarı.
        withdraw_amounts (list): Her ay için geri alınacak tutar (₺).
        roi_rate (float): ROI oranı.
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

    # İlk ayın hesaplamaları
    roi_values[0] = initial_rtp * roi_rate
    support_income[0] = initial_rtp * support_rate
    next_rtp_investments[0] = roi_values[0] - withdraw_amounts[0]
    total_investments[0] = initial_rtp

    for i in range(1, num_months):
        # ROI hesapla (önceki ayın RTP üzerinden)
        roi_values[i] = next_rtp_investments[i - 1] * roi_rate

        # Devlet katkısını hesapla
        support_income[i] = next_rtp_investments[i - 1] * support_rate

        # Bir sonraki ay RTP yatırım miktarını belirle
        if i < delay_months:
            # Gecikme süresi boyunca devlet katkısı eklenmez
            next_rtp_investments[i] = roi_values[i] - withdraw_amounts[i]
        else:
            # Gecikme süresi sonrasında devlet katkısı eklenir
            next_rtp_investments[i] = roi_values[i] + support_income[i - delay_months] - withdraw_amounts[i]

        total_investments[i] = next_rtp_investments[i - 1]

    data = {
        "Aylar": months,
        "ROI Miktarı (₺)": roi_values,
        "Destek Geliri (₺)": support_income,
        "Bir Sonraki Ay RTP Yatırım Miktarı (₺)": next_rtp_investments,
        "Toplam Yatırım (₺)": total_investments
    }

    df = pd.DataFrame(data)
    df.loc['Toplam'] = df.sum(numeric_only=True)
    df.at['Toplam', 'Aylar'] = 'Toplam'

    return df

# Streamlit Form
def main():
    st.title("RTP ve ROI Hesaplama Aracı")
    st.write("Bu araç, RTP yatırımı, ROI ve devlet katkısını hesaplar.")

    # Kullanıcıdan giriş alın
    initial_rtp = st.number_input("İlk Ay RTP Yatırım Miktarı (₺)", min_value=0.0, value=100000.0, step=1000.0, format="%.2f")
    roi_rate = st.number_input("ROI Oranı", min_value=0.0, value=1.5, step=0.1, format="%.2f")
    support_rate = st.number_input("Destek Oranı", min_value=0.0, value=0.6, step=0.1, format="%.2f")
    num_months = st.number_input("Kaç Ay İçin Hesaplama Yapılacak?", min_value=1, value=12, step=1)
    delay_months = st.number_input("Destek Gelirinin Eklenmeye Başlayacağı Ay Sayısı", min_value=1, value=4, step=1)

    # Ay isimlerini oluştur
    all_month_names = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    months = [all_month_names[i % 12] for i in range(num_months)]

    # Geri alınacak tutarları kullanıcıdan alın
    withdraw_amounts = []
    for i in range(num_months):
        withdraw_amounts.append(
            st.number_input(f"{months[i]} ayında geri alınacak tutar (₺)", min_value=0.0, value=0.0, step=1000.0, format="%.2f", key=f"withdraw_{i}")
        )

    # Hesaplama ve Sonuç Gösterimi
    if st.button("Hesapla"):
        results = calculate_rtp_and_roi(initial_rtp, withdraw_amounts, roi_rate, support_rate, months, delay_months)
        st.subheader("Sonuçlar")
        st.table(results)  # Sonuçları tablo olarak göster

        # Toplamları hesapla
        total_roi = results["ROI Miktarı (₺)"].sum()
        total_support = results["Destek Geliri (₺)"].sum()
        total_investment = results["Bir Sonraki Ay RTP Yatırım Miktarı (₺)"].sum()

        st.write(f"Toplam ROI Miktarı: {total_roi:,.2f} ₺")
        st.write(f"Toplam Destek Geliri: {total_support:,.2f} ₺")
        st.write(f"Toplam Yatırım Miktarı: {total_investment:,.2f} ₺")

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

        ax[2].plot(results["Aylar"], results["Bir Sonraki Ay RTP Yatırım Miktarı (₺)"], marker='o', color='green')
        ax[2].set_title("Bir Sonraki Ay RTP Yatırım Miktarı")
        ax[2].set_xlabel("Aylar")
        ax[2].set_ylabel("RTP Yatırım Miktarı (₺)")

        st.pyplot(fig)

if __name__ == "__main__":
    main()
