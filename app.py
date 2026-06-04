import streamlit as st
import google.generativeai as genai

# 1. 화면 타이틀 설정
st.set_page_config(page_title="Arch-Law AI", page_icon="🏢", layout="centered")
st.title("🏢 건축법 & 판례 탐색 AI 챗봇")
st.write("구상 중인 건축 상황이나 궁금한 법 조항을 입력하면 관련 법과 판례를 찾아줍니다.")

# 2. 내장 건축법 및 판례 데이터베이스
LAW_DATABASE = """
[참고 법률 및 판례 데이터베이스]
1. 건축법 제55조 (건축물의 건폐율) : 대지면적에 대한 건축면적의 비율. 위반 시 이행강제금 부과 가능.
2. 건축법 제56조 (건축물의 용적률) : 대지면적에 대한 연면적의 비율. 지하층은 용적률 제외되나 주거용 불법 개조 시 처벌.
3. 건축법 제61조 (일조 등의 확보를 위한 높이 제한) : 정북방향 인접 대지경계선 거리 제한. 위반 시 철거 및 손해배상 판례 있음.
4. 건축법 제11조 (건축허가) : 정당한 이유 없이 행정청이 건축허가를 거부하는 것은 위법함.
"""

# 3. 사이드바에 구글 API 키 입력창 만들기
with st.sidebar:
    st.header("🔑 구글 API 설정")
    google_api_key = st.text_input("Google API Key를 입력하세요", type="password")
    st.markdown("[Google AI Studio에서 무료 키 발급받기](https://aistudio.google.com/)")

# 4. 채팅 메시지 저장 공간 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하세요! 100% 무료 구글 Gemini 엔진으로 구동되는 건축법 챗봇입니다. 편하게 물어보세요!"}
    ]

# 5. 기존 대화 내용 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 6. 사용자 입력 및 답변 로직
if user_query := st.chat_input("예: 일조권 침해 기준이 뭔가요?"):
    with st.chat_message("user"):
        st.write(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    if not google_api_key:
        with st.chat_message("assistant"):
            st.error("왼쪽 사이드바에 Google API Key를 입력해주세요!")
    else:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("🔍 구글 AI가 법률 데이터 분석 중...")
            
            try:
                genai.configure(api_key=google_api_key)
                system_instruction = f"당신은 건축법 및 판례 전문 AI 상담사입니다. 아래 제공된 데이터베이스를 바탕으로 답변하세요.\n\n{LAW_DATABASE}"
                
                model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash",
                    system_instruction=system_instruction
                )
                
                # [안전장치 1] 대화 기록이 무조건 사용자의 첫 질문(user)부터 시작하도록 필터링
                contents = []
                start_sending = False
                for msg in st.session_state.messages:
                    if msg["role"] == "user":
                        start_sending = True
                    if start_sending:
                        role = "user" if msg["role"] == "user" else "model"
                        contents.append({"role": role, "parts": [msg["content"]]})
                
                response = model.generate_content(contents, stream=True)
                
                ai_answer = ""
                for chunk in response:
                    # [안전장치 2] 글자가 없는 빈 데이터 조각이 들어와도 에러 없이 패스하도록 예외 처리
                    try:
                        ai_answer += chunk.text
                        message_placeholder.markdown(ai_answer + "▌")
                    except Exception:
                        continue
                
                # 최종 답변 고정
                message_placeholder.markdown(ai_answer)
                st.session_state.messages.append({"role": "assistant", "content": ai_answer})
                
            except Exception as e:
                message_placeholder.error(f"에러가 발생했습니다: {str(e)}")