import json
import os
from datetime import datetime, timedelta

import streamlit as st

# --- Page Configuration ---
st.set_page_config(page_title="東京イベント情報", layout="wide")

# --- Date Range Selection ---
st.sidebar.header("期間指定")
today = datetime.now()

# Allow range selection
max_months = 6
max_days = max_months * 30

start_date = st.sidebar.date_input("開始日", today)
default_end = min(today + timedelta(days=30), today + timedelta(days=max_days))
end_date = st.sidebar.date_input("終了日", default_end)

# Custom period selection
period_options = {
    "1週間": 7,
    "2週間": 14,
    "1ヶ月": 30,
    "3ヶ月": 90,
    "6ヶ月": 180
}
selected_period = st.sidebar.selectbox(
    "期間を選択",
    options=list(period_options.keys()),
    index=2  # Default to 1 month
)

# Apply selected period if the user chooses from dropdown
if st.sidebar.button("期間を適用"):
    days = period_options[selected_period]
    end_date = start_date + timedelta(days=days)
    st.session_state.end_date = end_date

# Check if date range is valid
if (end_date - start_date).days > max_days:
    st.sidebar.error(f"期間は最大{max_months}ヶ月({max_days}日)まで指定可能です。")
    end_date = start_date + timedelta(days=max_days)

# Display selected date range
st.sidebar.info(f"選択期間: {start_date.strftime('%Y/%m/%d')} から {end_date.strftime('%Y/%m/%d')} まで ({(end_date - start_date).days + 1}日間)")

# --- Additional Search Parameters ---
st.sidebar.header("検索条件")
event_type = st.sidebar.multiselect(
    "イベントタイプ",
    ["すべて", "音楽", "アート", "テクノロジー", "ビジネス", "スポーツ", "食べ物", "その他"],
    default=["すべて"]
)

# --- Main Interface ---
st.title("東京イベント情報")

# Placeholder for event data - replace with actual data fetching logic later
event_data = [
    {"イベント名": "イベントA", "日時": "2024-03-08", "場所": "東京ドーム", "説明": "これはイベントAの説明です。", "URL": "https://example.com/eventA"},
    {"イベント名": "イベントB", "日時": "2024-03-15", "場所": "渋谷", "説明": "これはイベントBの説明です。", "URL": "https://example.com/eventB"},
    {"イベント名": "イベントC", "日時": "2024-03-22", "場所": "新宿", "説明": "これはイベントCの説明です。", "URL": "https://example.com/eventC"},

]


# Display events
if event_data:
    if isinstance(event_data, list):
        # Display as cards in a grid
        st.subheader(f"イベント一覧 ({len(event_data)}件)")
        
        # Create tabs for different view modes
        tab1, tab2 = st.tabs(["カード表示", "テーブル表示"])
        
        with tab1:
            # Create rows with 3 columns each for event cards
            events = event_data
            for i in range(0, len(events), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i+j < len(events):
                        event = events[i+j]
                        with cols[j]:
                            with st.container():
                                st.markdown(f"### {event.get('イベント名', 'イベント名不明')}")
                                st.markdown(f"**日時**: {event.get('日時', '不明')}")
                                st.markdown(f"**場所**: {event.get('場所', '不明')}")
                                
                                # Show description with a "もっと見る" expander if it's long
                                description = event.get('説明', '')
                                if len(description) > 100:
                                    st.markdown(f"{description[:100]}...")
                                    with st.expander("もっと見る"):
                                        st.markdown(description)
                                else:
                                    st.markdown(description if description else "説明なし")
                                
                                # If URL exists, add a link button
                                url = event.get('URL', '')
                                if url and url != "N/A":
                                    st.markdown(f"[イベントサイトへ]({url})", unsafe_allow_html=True)
        
        with tab2:
            # Convert to a more table-friendly format
            table_data = []
            for event in events:
                table_data.append({
                    "イベント名": event.get("イベント名", ""),
                    "日時": event.get("日時", ""),
                    "場所": event.get("場所", ""),
                    "URL": event.get("URL", "")
                })
            st.dataframe(table_data, use_container_width=True)
            
    elif isinstance(event_data, dict) and "raw_content" in event_data:
        # Display raw content from API
        st.subheader("APIからのレスポンス:")
        st.text(event_data["raw_content"])
    else:
        # Fallback display
        st.json(event_data)
else:
    st.info("イベント情報がまだありません。")

# --- Footer ---
st.markdown("---")
st.caption("東京イベント情報アプリケーション")