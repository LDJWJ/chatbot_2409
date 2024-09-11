import streamlit as st
from openai import OpenAI
import json

# 제목과 설명 표시
st.title("💘 고급 연애 상담 챗봇")
st.write(
    "이 챗봇은 OpenAI의 GPT-3.5 모델을 사용하여 맞춤형 연애 상담을 제공합니다. "
    "OpenAI API 키가 필요합니다. [여기](https://platform.openai.com/account/api-keys)에서 얻을 수 있습니다."
)

# 사용자에게 OpenAI API 키 입력 요청
openai_api_key = st.text_input("OpenAI API 키", type="password")

if not openai_api_key:
    st.info("계속하려면 OpenAI API 키를 입력해주세요.", icon="🗝️")
else:
    # OpenAI 클라이언트 생성
    client = OpenAI(api_key=openai_api_key)

    # 사용자 정보 입력
    st.sidebar.header("개인 정보 (선택사항)")
    age = st.sidebar.number_input("나이", min_value=0, max_value=100, value=25)
    gender = st.sidebar.selectbox("성별", ["선택안함", "남성", "여성", "기타"])
    relationship_status = st.sidebar.selectbox("관계 상태", ["선택안함", "싱글", "연애중", "기혼", "기타"])

    # 사전 정의된 질문 옵션
    predefined_questions = [
        "연애를 시작하는 방법",
        "이별 극복하기",
        "장거리 연애 조언",
        "데이트 아이디어",
        "관계에서의 의사소통 개선"
    ]
    selected_question = st.selectbox("일반적인 연애 고민:", ["직접 입력"] + predefined_questions)

    # 채팅 메시지를 저장할 세션 상태 변수 생성
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 기존 채팅 메시지 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력 처리
    if selected_question != "직접 입력":
        prompt = selected_question
    else:
        prompt = st.chat_input("연애 고민을 말씀해주세요")

    if prompt:
        # 현재 프롬프트 저장 및 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 시스템 메시지 생성
        system_message = f"""당신은 전문적이고 공감적인 연애 상담가입니다. 
        사용자 정보: 나이 {age}, 성별 {gender}, 관계 상태 {relationship_status}
        이 정보를 고려하여 맞춤형 조언을 제공해주세요. 항상 긍정적이고 건설적인 조언을 해주세요."""

        # OpenAI API를 사용하여 응답 생성
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # 응답을 스트리밍하여 채팅에 표시하고 세션 상태에 저장
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # 감정 분석 (간단한 키워드 기반 분석)
        emotions = ["행복", "슬픔", "분노", "불안", "혼란"]
        emotion = max(emotions, key=lambda e: response.count(e))
        st.write(f"현재 감정 상태: {emotion}")

        # 추가 리소스 제공
        st.write("추가 리소스:")
        st.write("- [연애와 관계에 대한 추천 도서](https://example.com/books)")
        st.write("- [전문 상담 서비스](https://example.com/counseling)")

    # 대화 저장 기능
    if st.button("대화 내용 저장"):
        conversation = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
        st.download_button(
            label="대화 내용 다운로드",
            data=conversation,
            file_name="love_advice_chat.json",
            mime="application/json"
        )
