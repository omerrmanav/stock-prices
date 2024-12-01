import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt

page = st.sidebar.radio(
    "Sayfa Seçin",
     ["Hisse Bilgileri", "Alım Geçmişi", "Hesap Özeti ve Grafikler"]
     )

if page == "Hisse Bilgileri":
    st.header("🟢Hisse Bilgileri")
    symbols = ["XU100.IS", "THYAO.IS", "SISE.IS", "DOAS.IS", "EUPWR.IS", "USDTRY=X", "EURTRY=X"]
    durations = ["5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]
    col1, col2 = st.columns(2)

    with col1:
        st.header("Hisse Ara")
        selected_symbol = st.selectbox(
            "Lütfen grafiğini görmek istediğiniz hisseyi seçiniz.", symbols
        )
        selected_duration = st.selectbox(
            "Lütfen zaman aralığını belirtiniz.", durations
        )

        if "button_state" not in st.session_state:
            st.session_state["button_state"] = False
        if st.button("Tavan, taban ve ortalama fiyatı göster"):
            st.session_state["button_state"] = not st.session_state["button_state"]

    stock = yf.Ticker(selected_symbol)
    prices = stock.history(period = selected_duration)

    price_highest = prices["Close"].max()
    price_deepest = prices["Close"].min()
    price_average = prices["Close"].mean()

    date_price_highest = prices["Close"].idxmax()
    date_price_deepest = prices["Close"].idxmin()

    list_dates = prices.index.to_list()
    list_prices = prices["Close"].to_list()

    date_last = list_dates[-1]
    date_first = list_dates[0]
    price_day_last = list_prices[-1]
    price_day_first = list_prices[0]
    profit = ((price_day_last - price_day_first) / price_day_first) * 100

    with col2:
        st.header("Hisse Kaydet")
        with st.form(key="form_stock"):
            price = st.number_input("Maliyet", min_value=0.0, format="%.2f", value=price_average)
            quantity = st.number_input("Adet", min_value=0)
            button_submit = st.form_submit_button(label="Kaydet")

        if "stocks" not in st.session_state:
                st.session_state["stocks"] = []
    
        if button_submit:
            st.session_state["stocks"].append({
                "name" : selected_symbol,
                "price" : price,
                "quantity" : quantity,
                "current_price" : price_day_last,
                "cost": price * quantity,
                "total": price_day_last * quantity
            })
            st.write("Başarıyla kaydedildi")
    def red_point_to_graph(date, price):
        plt.scatter(date, price, color = "#f1c40f")
        plt.text(
            x=date,
            y=price,
            s=f"  {price:.2f}₺",
            ha="left",
            va="bottom",
            color="#f1c40f",
            fontweight="bold"
        )

    if(selected_symbol=="USDTRY=X", "EURTRY=X"):
        st.write("---")
        st.write(f"Anlık {selected_symbol} Fiyatı")
        dollar = list_prices[-1]
        st.write(dollar)

        turkish_lira = st.number_input("Dönüştürmek istediğiniz tutarı giriniz")
        convert_to_dollar = turkish_lira / dollar
        st.write(f"{turkish_lira} TL = {convert_to_dollar:.2f}")

    st.write(f"{selected_symbol} hissesine ait {selected_duration} grafiği")
    plt.figure(figsize=(10,6))
    plt.plot(list_dates, list_prices, color= "#000000")
    plt.title(f"{selected_symbol}")
    plt.xlabel("Tarih")
    plt.ylabel("Fiyat")
    plt.xticks(rotation=45)

    plt.text(
        x=0.05,
        y=0.95,
        s=f"Yüzdesel Kar: %{profit:.3f}",
        fontweight="bold",
        color="#2e4053",
        ha="left",
        va="top",
        transform=plt.gca().transAxes
    )

    if st.session_state["button_state"]:
        red_point_to_graph(date_last, price_day_last)
        red_point_to_graph(date_first, price_day_first)
        plt.plot(
            [date_first, date_last],                                # x = [a1, a2]
            [price_day_first, price_day_last],             # y = [b1, b2]
            color="#f1c40f",
            linestyle="-.",
            linewidth=1
        )
        red_point_to_graph(date_price_highest, price_highest)
        red_point_to_graph(date_price_deepest, price_deepest)

        plt.axhline(y=price_highest, color="#f1c40f", linewidth=1, linestyle="-.")
        plt.axhline(y=price_deepest, color="#f1c40f", linewidth=1, linestyle="-.")
        plt.axhline(y=price_average, color="#4a235a", linewidth=1, linestyle="-.")
        
        plt.text(
            x=list_dates[len(list_dates) // 2],
            y=price_average,
            s=f"{price_average:.2f}₺",
            ha="center",
            va="bottom",
            color="#4a235a",
            fontweight="bold"
    )
        
    if profit > 0:
        plt.fill_between(list_dates, list_prices, color="#196f3d", alpha=1)
    else:
        plt.fill_between(list_dates, list_prices, color="#7b241c", alpha=1)

    min_price = min(list_prices)
    max_price = max(list_prices)
    marginY = 0.05 * (max_price - min_price)
    plt.ylim(min_price - marginY, max_price + marginY)        # grafik en düşük ve en yüksek fiyatlar arasında sıkışmasın

    min_date = min(list_dates)
    max_date = max(list_dates)
    marginX = 0.001 * (max_date - min_date)
    plt.xlim(min_date - marginX, max_date + marginX)

    st.pyplot(plt)
    plt.close()

elif page == "Alım Geçmişi":
    st.header("Alım Geçmişi ")
    if st.session_state["stocks"]:
        st.write("Alımlar")
        for stock in st.session_state["stocks"]:
            income = stock["total"] - stock["cost"]
            income_percent = ((stock["total"] - stock["cost"]) / stock["cost"]) * 100
            st.write(
                f"🫰{stock["name"]}, "
                f"Miktar: {stock["quantity"]}, "
                f"Alış: {stock["price"]:.2f}, "
                f"Güncel: {stock["current_price"]:.2f}, \n"
                f"Maliyet: {stock["cost"]:.2f}₺, "
                f"Güncel: {stock["total"]:.2f}, "
                f"Kar: {income:.2f}₺, "
                f"Yüzde: %{income_percent:.2f}"
            )
    else:
        st.write("Alım Yapılmamıştır")
    
elif page == "Hesap Özeti ve Grafikler":
    st.header("Hesap Özeti ve Grafikler")
    invested_money = 0
    latest_status = 0

    if "stocks" in st.session_state and st.session_state["stocks"]:
        cost_prices = [stock["cost"] for stock in st.session_state["stocks"]]
        for one_price in cost_prices:
            invested_money += one_price

        latest_prices = [stock["total"] for stock in st.session_state["stocks"]]
        for one_price in latest_prices:
            latest_status += one_price

        all_income = latest_status - invested_money
        all_income_percent = ((latest_status - invested_money) / invested_money) * 100

        st.header("Hesap Özeti")
        st.write(
            f"Yatırılan Miktar: {invested_money:.2f}₺ "
            f"\n\nToplam Miktar: {latest_status:.2f}₺"
            f"\n\nKar: {all_income:.2f}₺, "
            f"Yüzde: %{all_income_percent:.2f}"
        )
    else:
        st.write("Hesap Özeti Bulunmuyor..")





    













