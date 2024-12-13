import streamlit as st

def calculate_rtp_and_roi(initial_rtp, withdraw_amounts, roi_rate, support_rate, months):
    """
    RTP, ROI ve Devlet Katkısı Hesaplama Fonksiyonu.

    Args:
        initial_rtp (float): İlk ay RTP Yatırım Miktarı.
        withdraw_amounts (list): Her ay için geri alınacak tutar (₺).
        roi_rate (float): ROI oranı.
        support_rate (float): Destek Oranı.
        months (list): Ay isimleri.

    Returns:
        dict: Tüm hesaplanan değerleri içeren tablo.
    """
    num_months = len(months)
    roi_values = [0] * num_months       # ROI miktarları
    support_income = [0] * num_months   # Destek gelirleri
    next_rtp_investments = [0] * num_months  # Bir sonraki ay RTP yatırım miktarları

    # İlk ayın hesaplamaları
    roi_values[0] = initial_rtp * roi_rate
    support_income[0] = initial_rtp * support_rate
    next_rtp_investments[0] = roi_values[0] - withdraw_amounts[0]

    for i in range(1, num_months):
        # ROI hesapla (önceki ayın RTP üzerinden)
        roi_values[i] = next_rtp_investments[i - 1] * roi_rate

        # Devlet katkısını hesapla
        support_income[i] = next_rtp_investments[i - 1] * support_rate

        # Bir sonraki ay RTP yatırım miktarını belirle
        if i < 4:
            # İlk 4 ay devlet katkısı eklenmez
            next_rtp_investments[i] = roi_values[i] - withdraw_amounts[i]
        else:
            # 5. ay ve sonrasında devlet katkısı eklenir
            next_rtp_investments[i] = roi_values[i] + support_income[i - 4] - withdraw_amounts[i]

    return {
        "Aylar": months,
        "ROI Miktarı": roi_values,
        "Destek Geliri": support_income,
        "Bir Sonraki Ay RTP Yatırım Miktarı": next_rtp_investments,
    }

# Streamlit Form
def main():
    st.title("Dezztech Return System Reklam Tanıtım Pazarlama Desteği Hesaplama Modülü.")
    st.write("Bu modül, bir dizi parametreye göre RTP (Return to Principal) yatırım hesaplaması yapan,
    her ay için ROI (Return on Investment) geliri, destek geliri, geri alınan tutar ve 
    gelecek ayın RTP miktarını hesaplayarak bir tablo halinde gösteren bir örnektir.

    Kullanım Adımları:
    1. İlk ay RTP yatırım miktarını, ROI oranını, destek oranını ve hesaplanacak ay sayısını girin.
    2. Her ay için geri alınacak tutarı girin.
    3. "Hesapla" butonuna basarak sonuçları tablodan inceleyin.

    Açıklamalar:
    - İlk 4 ay devlet desteği (Destek Geliri) uygulanmaz. Bu nedenle ilgili hücreler 0 olarak görünür.
    - 5. aydan itibaren destek geliri hesaplanarak bir sonraki ay RTP'sine eklenir.
    - Tablo, her ayın başlangıçtaki RTP miktarını, o ayki ROI gelirini, destek gelirini, 
      geri alınan tutarı ve bir sonraki aya devredilecek RTP miktarını gösterir.")

    # Kullanıcıdan giriş alın
    initial_rtp = st.number_input("İlk Ay RTP Yatırım Miktarı (₺)", min_value=0.0, value=100000.0, step=1000.0)
    roi_rate = st.number_input("ROI Oranı", min_value=0.0, value=1.5, step=0.1)
    support_rate = st.number_input("Destek Oranı", min_value=0.0, value=0.6, step=0.1)
    num_months = st.number_input("Kaç Ay İçin Hesaplama Yapılacak?", min_value=1, value=12, step=1)

    # Ay isimlerini oluştur
    all_month_names = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    months = [all_month_names[i % 12] for i in range(num_months)]

    # Geri alınacak tutarları kullanıcıdan alın
    withdraw_amounts = []
    for i in range(num_months):
        withdraw_amounts.append(
            st.number_input(f"{months[i]} ayında geri alınacak tutar (₺)", min_value=0.0, value=0.0, step=1000.0, key=f"withdraw_{i}")
        )

    # Hesaplama ve Sonuç Gösterimi
    if st.button("Hesapla"):
        results = calculate_rtp_and_roi(initial_rtp, withdraw_amounts, roi_rate, support_rate, months)
        st.subheader("Sonuçlar")
        st.table(results)  # Sonuçları tablo olarak göster

if __name__ == "__main__":
    main()
