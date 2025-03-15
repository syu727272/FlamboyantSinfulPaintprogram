import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import os

# --- Page Configuration ---
st.set_page_config(page_title="東京イベント情報", layout="wide")

# --- API Key Management ---
def get_api_key():
    # Try to get from environment variable first
    api_key = os.environ.get("XAI_API_KEY", "")
    
    # If not found in environment, check session state or prompt user
    if not api_key:
        if "api_key" in st.session_state:
            api_key = st.session_state.api_key
        else:
            api_key = st.sidebar.text_input("GROK API Key", type="password")
            if api_key:
                st.session_state.api_key = api_key
    
    return api_key

# --- GROK API Configuration ---
API_KEY = get_api_key()
ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"  # GROQ API endpoint

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

# --- API Request Function ---
def get_events(start_date, end_date, event_types=None, limit=30):
    if not API_KEY:
        st.error("APIキーが設定されていません。サイドバーでAPIキーを入力してください。")
        return None
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Prepare query for GROK API
    event_type_query = ""
    if event_types and "すべて" not in event_types:
        event_type_query = " " + " ".join(event_types)
    
    query = f"東京で{start_date.strftime('%Y年%m月%d日')}から{end_date.strftime('%Y年%m月%d日')}までに開催されるイベント{event_type_query}を{limit}件リストアップして、各イベントの名前、日時、場所、説明、URLを含む辞書形式で返してください。"
    
    payload = {
        "messages": [
            {"role": "system", "content": "あなたはイベント情報を提供する専門AIアシスタントです。"},
            {"role": "user", "content": query}
        ],
        "model": "grok-1",
        "max_tokens": 4000
    }
    
    try:
        with st.spinner("イベント情報を取得中..."):
            response = requests.post(ENDPOINT, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            # Parse the assistant's message from GROK API response
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                # Try to extract JSON from the response
                try:
                    # Look for JSON in the response
                    import re
                    json_match = re.search(r'\[.*\]|\{.*\}', content, re.DOTALL)
                    if json_match:
                        events_data = json.loads(json_match.group())
                        return events_data
                    else:
                        # If no JSON found, return the raw content
                        st.warning("構造化されたデータが見つかりませんでした。生のレスポンスを表示します。")
                        return {"raw_content": content}
                except json.JSONDecodeError:
                    st.warning("JSON解析エラー。生のレスポンスを表示します。")
                    return {"raw_content": content}
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"APIリクエストエラー: {e}")
        return None

# --- Main Interface ---
st.title("東京イベント情報")
st.write("GROK APIを使用して東京で開催されるイベント情報を表示します")

col1, col2 = st.columns([1, 4])
with col1:
    fetch_btn = st.button("イベント情報を取得", use_container_width=True)
    
    limit = st.number_input("表示件数", min_value=5, max_value=100, value=30, step=5)

# Fetch events when button is clicked
if fetch_btn:
    event_data = get_events(
        start_date, 
        end_date, 
        event_types=event_type if "すべて" not in event_type else None,
        limit=limit
    )
    
    # Store in session state for persistence
    st.session_state.event_data = event_data
elif "event_data" in st.session_state:
    event_data = st.session_state.event_data
else:
    event_data = None

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
                            with st.container(border=True):
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
    if fetch_btn:
        st.info("イベント情報が取得できませんでした。検索条件を変更するか、APIキーをご確認ください。")
    else:
        st.info("「イベント情報を取得」ボタンをクリックしてイベントを検索してください。")

# --- Footer ---
st.markdown("---")
st.caption("GROK API を利用した東京イベント情報アプリケーション")
