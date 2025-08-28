import streamlit as st
import pandas as pd
from datetime import datetime
import json
from data.system_admins import SYSTEM_ADMINS
from utils.keyword_matcher import KeywordMatcher

# 페이지 설정
st.set_page_config(page_title="한화생명 시스템 담당자 검색", page_icon="💼", layout="wide")

# 모바일 최적화 CSS
st.markdown("""
<style>
    /* 모바일 대응 기본 설정 */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1rem !important;
            max-width: 100% !important;
        }

        .stSidebar .sidebar-content {
            width: 100% !important;
            min-width: unset !important;
        }

        /* 텍스트 크기 조정 */
        .stMarkdown h1 {
            font-size: 1.5rem !important;
        }

        .stMarkdown h2 {
            font-size: 1.3rem !important;
        }

        .stMarkdown h3 {
            font-size: 1.1rem !important;
        }

        /* 버튼 크기 조정 */
        .stButton button {
            width: 100% !important;
            height: 3rem !important;
            font-size: 0.9rem !important;
            padding: 0.5rem !important;
        }

        /* 입력창 크기 조정 */
        .stTextInput input {
            font-size: 1rem !important;
            padding: 0.75rem !important;
        }

        .stTextArea textarea {
            font-size: 1rem !important;
            min-height: 100px !important;
        }

        /* 카드 컨테이너 모바일 최적화 */
        .admin-card {
            background: white;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #007acc;
        }

        .admin-card h3 {
            margin-top: 0 !important;
            color: #333 !important;
            font-size: 1.2rem !important;
        }

        .admin-card p {
            margin: 0.5rem 0 !important;
            font-size: 0.9rem !important;
        }

        /* 탭 최적화 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }

        .stTabs [data-baseweb="tab"] {
            font-size: 0.9rem !important;
            padding: 0.5rem 0.75rem !important;
        }

        /* 컬럼 간격 조정 */
        .stColumns > div {
            padding: 0 0.25rem !important;
        }

        /* 익스팬더 최적화 */
        .streamlit-expanderHeader {
            font-size: 1rem !important;
        }

        /* 메트릭 카드 모바일 최적화 */
        .metric-container {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
            margin: 0.5rem 0;
        }

        /* 피드백 버튼 최적화 */
        .feedback-container {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin: 1rem 0;
        }

        .feedback-container button {
            flex: 1;
            max-width: 150px;
        }
    }

    /* 태블릿 대응 */
    @media (min-width: 769px) and (max-width: 1024px) {
        .main .block-container {
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
    }

    /* 클릭 가능한 전화번호 스타일 */
    .phone-link {
        color: #0066cc !important;
        cursor: pointer !important;
        text-decoration: underline !important;
        user-select: none !important;
        font-weight: 500 !important;
    }

    .phone-link:hover {
        color: #004499 !important;
        background-color: #f0f8ff !important;
        padding: 2px 4px !important;
        border-radius: 4px !important;
    }

    .copy-feedback {
        color: #28a745 !important;
        font-size: 0.8rem !important;
        margin-left: 8px !important;
        font-weight: bold !important;
    }

    /* 로딩 스피너 개선 */
    .stSpinner {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        height: 100px !important;
    }

    /* 알림 메시지 개선 */
    .stAlert {
        border-radius: 8px !important;
        margin: 1rem 0 !important;
    }

    /* 즐겨찾기 별 아이콘 */
    .favorite-star {
        color: #ffd700 !important;
        font-size: 1.2rem !important;
    }

    /* 반응형 그리드 */
    .responsive-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }

    /* 모바일에서 헤더 최적화 */
    @media (max-width: 768px) {
        .stColumns > div:first-child img {
            width: 70px !important;
            max-width: 70px !important;
        }

        .stColumns > div:nth-child(2) h1 {
            font-size: 1.6rem !important;
            line-height: 1.3 !important;
        }

        .stColumns > div:nth-child(2) p {
            font-size: 0.9rem !important;
            margin-top: 5px !important;
        }
    }
</style>
""",
            unsafe_allow_html=True)

# 세션 상태 초기화
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'favorites' not in st.session_state:
    st.session_state.favorites = []
if 'recent_searches' not in st.session_state:
    st.session_state.recent_searches = []
if 'feedback_data' not in st.session_state:
    st.session_state.feedback_data = []
if 'improvement_suggestions' not in st.session_state:
    st.session_state.improvement_suggestions = []

# 키워드 매처 초기화
matcher = KeywordMatcher(SYSTEM_ADMINS)


def add_to_favorites(admin_id):
    """즐겨찾기에 추가"""
    if admin_id not in st.session_state.favorites:
        st.session_state.favorites.append(admin_id)
        st.success(f"즐겨찾기에 추가되었습니다!")
        st.rerun()


def remove_from_favorites(admin_id):
    """즐겨찾기에서 제거"""
    if admin_id in st.session_state.favorites:
        st.session_state.favorites.remove(admin_id)
        st.success(f"즐겨찾기에서 제거되었습니다!")
        st.rerun()


def add_to_recent_searches(admin_id):
    """최근 조회에 추가"""
    if admin_id in st.session_state.recent_searches:
        st.session_state.recent_searches.remove(admin_id)
    st.session_state.recent_searches.insert(0, admin_id)
    # 최근 조회는 최대 10개까지 유지
    if len(st.session_state.recent_searches) > 10:
        st.session_state.recent_searches = st.session_state.recent_searches[:
                                                                            10]


def display_admin_card(admin, show_favorite_button=True, context="default"):
    """담당자 정보 카드 표시 (모바일 최적화)"""
    with st.container():
        # 모바일에서는 카드 스타일로 표시
        card_html = f"""
        <div class="admin-card">
            <h3>👨‍💼 {admin['name']}</h3>
            <p><strong>부서:</strong> {admin['department']}</p>
            <p><strong>직급:</strong> {admin['position']}</p>
            <p><strong>연락처:</strong> 
                <span 
                    class="phone-link"
                    onclick="copyToClipboard('{admin['phone']}', '{admin['id']}_{context}')"
                    title="클릭하여 복사"
                >
                    {admin['phone']}
                </span>
                <span id="copy_feedback_{admin['id']}_{context}" class="copy-feedback"></span>
            </p>
            <p><strong>이메일:</strong> {admin['email']}</p>
            <p><strong>업무 범위:</strong> {', '.join(admin['responsibilities'])}</p>
            {f"<p><strong>전문 분야:</strong> {', '.join(admin['specialties'])}</p>" if admin.get('specialties') else ""}
        </div>

        <script>
        function copyToClipboard(text, adminId) {{
            navigator.clipboard.writeText(text).then(function() {{
                const feedbackElement = document.getElementById('copy_feedback_' + adminId);
                if (feedbackElement) {{
                    feedbackElement.innerHTML = '✓ 복사됨!';
                    setTimeout(function() {{
                        feedbackElement.innerHTML = '';
                    }}, 2000);
                }}
            }}).catch(function(err) {{
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);

                const feedbackElement = document.getElementById('copy_feedback_' + adminId);
                if (feedbackElement) {{
                    feedbackElement.innerHTML = '✓ 복사됨!';
                    setTimeout(function() {{
                        feedbackElement.innerHTML = '';
                    }}, 2000);
                }}
            }});
        }}
        </script>
        """

        st.markdown(card_html, unsafe_allow_html=True)

        # 즐겨찾기 버튼을 카드 하단에 배치
        if show_favorite_button:
            if admin['id'] in st.session_state.favorites:
                if st.button("⭐ 즐겨찾기 해제",
                             key=f"unfav_{context}_{admin['id']}",
                             use_container_width=True):
                    remove_from_favorites(admin['id'])
            else:
                if st.button("☆ 즐겨찾기 추가",
                             key=f"fav_{context}_{admin['id']}",
                             use_container_width=True):
                    add_to_favorites(admin['id'])

        st.markdown("<br>", unsafe_allow_html=True)


def add_chat_message(user_message, bot_response, found_admins):
    """채팅 기록에 메시지 추가"""
    message_id = len(st.session_state.chat_history)
    st.session_state.chat_history.append({
        'id':
        message_id,
        'timestamp':
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'user_message':
        user_message,
        'bot_response':
        bot_response,
        'found_admins':
        found_admins,
        'feedback':
        None
    })


def add_feedback(message_id, feedback_type):
    """피드백 추가"""
    if message_id < len(st.session_state.chat_history):
        st.session_state.chat_history[message_id]['feedback'] = feedback_type
        st.session_state.feedback_data.append({
            'timestamp':
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'message_id':
            message_id,
            'feedback':
            feedback_type
        })
        st.success("피드백이 등록되었습니다!")


def add_improvement_suggestion(suggestion):
    """개선사항 추가"""
    st.session_state.improvement_suggestions.append({
        'timestamp':
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'suggestion':
        suggestion
    })
    st.success("개선사항이 등록되었습니다!")


def display_feedback_buttons(message_id):
    """피드백 버튼 표시 (모바일 최적화)"""
    if message_id < len(st.session_state.chat_history):
        current_feedback = st.session_state.chat_history[message_id].get(
            'feedback')

        st.markdown("---")

        if current_feedback is None:
            # 모바일 친화적 피드백 섹션
            st.markdown("""
            <div style='text-align: center; padding: 15px; background-color: #f8f9fa; border-radius: 10px; margin: 15px 0;'>
                <p style='margin-bottom: 15px; font-weight: 500; color: #333; font-size: 1rem;'>
                    💬 이 답변이 도움이 되셨나요?
                </p>
            </div>
            """,
                        unsafe_allow_html=True)

            # 모바일에서 2열 배치
            col1, col2 = st.columns(2)

            with col1:
                if st.button("👍 도움됨",
                             key=f"feedback_positive_{message_id}",
                             help="이 답변이 도움이 되었습니다",
                             use_container_width=True):
                    add_feedback(message_id, "positive")
                    st.rerun()

            with col2:
                if st.button("👎 개선필요",
                             key=f"feedback_negative_{message_id}",
                             help="이 답변을 개선할 필요가 있습니다",
                             use_container_width=True):
                    add_feedback(message_id, "negative")
                    st.rerun()
        else:
            # 피드백 완료 상태 표시
            if current_feedback == "positive":
                st.markdown("""
                <div style='text-align: center; padding: 15px; background-color: #d4edda; border-radius: 10px; margin: 15px 0; border-left: 4px solid #28a745;'>
                    <p style='margin: 0; color: #155724; font-weight: 500; font-size: 0.95rem;'>
                        ✅ 피드백 주셔서 감사합니다! 도움이 되어 기쁩니다.
                    </p>
                </div>
                """,
                            unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='text-align: center; padding: 15px; background-color: #fff3cd; border-radius: 10px; margin: 15px 0; border-left: 4px solid #ffc107;'>
                    <p style='margin: 0; color: #856404; font-weight: 500; font-size: 0.95rem;'>
                        📝 피드백 주셔서 감사합니다. 더 나은 답변을 제공하도록 개선하겠습니다.
                    </p>
                </div>
                """,
                            unsafe_allow_html=True)


def main():
    # 헤더 - 로고와 함께 (로고 파일이 있을 때만 표시)
    import os

    if os.path.exists("assets/hanwha_logo.png"):
        col1, col2 = st.columns([1, 8])

        with col1:
            st.image("assets/hanwha_logo.png", width=80)

        with col2:
            st.markdown("""
            <div style='padding-top: 15px;'>
                <h1 style='margin: 0; color: #333;'>한화생명 AI 상담 챗봇(Beta)</h1>
            </div>
            """,
                        unsafe_allow_html=True)
    else:
        # 로고가 없을 때는 텍스트만 표시
        st.markdown("""
        <div style='text-align: center; padding: 20px 0;'>
            <h1 style='margin: 0; color: #333;'> 한화생명 AI 상담 챗봇(Beta)</h1>
        </div>
        """,
                    unsafe_allow_html=True)

    #st.markdown("업무와 관련된 시스템 담당자를 빠르게 찾아보요!")

    # 사이드바 - 즐겨찾기 및 최근 조회 (모바일 최적화)
    with st.sidebar:
        st.header("✅ 빠른 접근")

        # 즐겨찾기
        st.subheader("⭐ 즐겨찾기")
        if st.session_state.favorites:
            for admin_id in st.session_state.favorites:
                admin = next((a for a in SYSTEM_ADMINS if a['id'] == admin_id),
                             None)
                if admin:
                    # 모바일에서 텍스트 줄임 처리
                    display_name = f"{admin['name']}"
                    display_dept = f"({admin['department']})"
                    if st.button(f"{display_name}\n{display_dept}",
                                 key=f"fav_quick_{admin_id}",
                                 use_container_width=True):
                        st.session_state.selected_admin = admin
                        add_to_recent_searches(admin_id)
                        st.rerun()
        else:
            st.info("즐겨찾기가 없습니다.")

        st.markdown("---")

        # 최근 조회
        st.subheader("🕒 최근 조회")
        if st.session_state.recent_searches:
            for admin_id in st.session_state.recent_searches[:5]:  # 최대 5개만 표시
                admin = next((a for a in SYSTEM_ADMINS if a['id'] == admin_id),
                             None)
                if admin:
                    display_name = f"{admin['name']}"
                    display_dept = f"({admin['department']})"
                    if st.button(f"{display_name}\n{display_dept}",
                                 key=f"recent_quick_{admin_id}",
                                 use_container_width=True):
                        st.session_state.selected_admin = admin
                        st.rerun()
        else:
            st.info("최근 조회 기록이 없습니다.")

    # 메인 영역
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["💬 채팅 검색", "📋 전체 담당자", "📝 대화 기록", "💡 개선사항", "📔교육용 자료"])

    with tab1:
        st.header("💬 채팅으로 담당자 찾기")

        # 자주 묻는 질문 섹션
        with st.expander("📌 자주 묻는 질문", expanded=False):
            st.markdown("**예시 질문:**")

            example_questions = [
                "계약 관련 부서는 어디인가요?", "근무 시간은 어떻게 되세요?", "고객서비스 담당자 연락처 알려주세요",
                "보험금 청구 담당자가 누구인가요?", "시스템 장애 신고는 어디로 하나요?"
            ]

            # 예시 질문들을 버튼으로 만들어서 클릭하면 입력창에 자동 입력
            for i, question in enumerate(example_questions):
                if st.button(f"💬 {question}",
                             key=f"example_q_{i}",
                             use_container_width=True):
                    st.session_state.selected_question = question
                    st.rerun()

        # 채팅 입력
        # 선택된 질문이 있으면 기본값으로 설정
        default_value = ""
        if hasattr(st.session_state, 'selected_question'):
            default_value = st.session_state.selected_question
            # 사용 후 삭제
            delattr(st.session_state, 'selected_question')

        user_input = st.text_input(
            "질문을 입력하세요",
            value=default_value,
            placeholder="무엇이든 물어보세요! (업무 담당자 안내, 부서 찾기 등)",
            label_visibility="collapsed")

        if user_input:
            # 키워드 매칭으로 담당자 찾기
            matched_admins = matcher.find_matching_admins(user_input)

            if matched_admins:
                bot_response = f"'{user_input}' 관련하여 {len(matched_admins)}명의 담당자를 찾았습니다:"
                st.success(bot_response)

                for admin in matched_admins:
                    display_admin_card(admin, context="chat")
                    add_to_recent_searches(admin['id'])

                # 채팅 기록에 추가
                add_chat_message(user_input, bot_response,
                                 [admin['id'] for admin in matched_admins])

                # 피드백 버튼 표시
                current_message_id = len(st.session_state.chat_history) - 1
                display_feedback_buttons(current_message_id)

            else:
                bot_response = "죄송합니다. 관련 담당자를 찾을 수 없습니다. 다른 키워드로 검색해보시거나 전체 담당자 목록을 확인해주세요."
                st.warning(bot_response)
                add_chat_message(user_input, bot_response, [])

                # 피드백 버튼 표시
                current_message_id = len(st.session_state.chat_history) - 1
                display_feedback_buttons(current_message_id)

    with tab2:
        st.header("📋 전체 시스템 담당자")

        # 검색 필터 (모바일에서는 세로 배치)
        dept_filter = st.selectbox(
            "부서 필터",
            ["전체"] + list(set([admin['department']
                               for admin in SYSTEM_ADMINS])))

        search_text = st.text_input("이름 또는 업무 검색", placeholder="검색어를 입력하세요...")

        # 필터링된 담당자 목록
        filtered_admins = SYSTEM_ADMINS

        if dept_filter != "전체":
            filtered_admins = [
                admin for admin in filtered_admins
                if admin['department'] == dept_filter
            ]

        if search_text:
            filtered_admins = [
                admin for admin in filtered_admins
                if search_text.lower() in admin['name'].lower() or any(
                    search_text.lower() in resp.lower()
                    for resp in admin['responsibilities'])
            ]

        # 결과 수 표시 (모바일 친화적 스타일)
        st.markdown(f"""
        <div style='text-align: center; padding: 10px; background-color: #e3f2fd; border-radius: 8px; margin: 10px 0;'>
            <strong>총 {len(filtered_admins)}명의 담당자</strong>
        </div>
        """,
                    unsafe_allow_html=True)

        for admin in filtered_admins:
            display_admin_card(admin, context="list")

    with tab3:
        st.header("📝 대화 기록")

        if st.session_state.chat_history:
            for i, chat in enumerate(reversed(st.session_state.chat_history)):
                with st.expander(
                        f"대화 {len(st.session_state.chat_history) - i}: {chat['timestamp']}"
                ):
                    st.markdown(f"**사용자:** {chat['user_message']}")
                    st.markdown(f"**챗봇:** {chat['bot_response']}")

                    if chat['found_admins']:
                        st.markdown("**찾은 담당자:**")
                        for admin_id in chat['found_admins']:
                            admin = next((a for a in SYSTEM_ADMINS
                                          if a['id'] == admin_id), None)
                            if admin:
                                st.markdown(
                                    f"- {admin['name']} ({admin['department']})"
                                )

                    # 피드백 상태 표시
                    if chat.get('feedback'):
                        if chat['feedback'] == 'positive':
                            st.markdown("**피드백:** 👍 도움됨")
                        else:
                            st.markdown("**피드백:** 👎 도움안됨")

            if st.button("🗑️ 대화 기록 삭제"):
                st.session_state.chat_history = []
                st.session_state.feedback_data = []
                st.success("대화 기록이 삭제되었습니다!")
                st.rerun()
        else:
            st.info("아직 대화 기록이 없습니다.")

    with tab4:
        st.header("💡건의사항")

        # 새 건의사항 작성
        st.subheader("✍️ 새로운 건의사항 작성")
        suggestion_text = st.text_area(
            "개선사항이나 건의사항을 자유롭게 작성해주세요:",
            placeholder="예: 검색 속도 개선, 새로운 기능 추가, 인터페이스 개선 등")

        if st.button("💌 건의사항 제출"):
            if suggestion_text.strip():
                add_improvement_suggestion(suggestion_text.strip())
                st.rerun()
            else:
                st.warning("건의사항을 입력해주세요.")

        st.markdown("---")

        # 피드백 통계 (모바일 최적화)
        st.subheader("📊 사용자 피드백 현황")
        if st.session_state.feedback_data:
            positive_count = sum(1 for f in st.session_state.feedback_data
                                 if f['feedback'] == 'positive')
            negative_count = sum(1 for f in st.session_state.feedback_data
                                 if f['feedback'] == 'negative')
            total_feedback = len(st.session_state.feedback_data)

            # 모바일에서는 메트릭을 카드 형태로 표시
            metrics_html = f"""
            <div class="responsive-grid">
                <div class="metric-container">
                    <h3 style="margin: 0; color: #1f77b4;">{total_feedback}</h3>
                    <p style="margin: 5px 0; font-weight: 500;">총 피드백</p>
                </div>
                <div class="metric-container">
                    <h3 style="margin: 0; color: #28a745;">{positive_count} 👍</h3>
                    <p style="margin: 5px 0; font-weight: 500;">긍정적 피드백</p>
                </div>
                <div class="metric-container">
                    <h3 style="margin: 0; color: #dc3545;">{negative_count} 👎</h3>
                    <p style="margin: 5px 0; font-weight: 500;">개선 필요</p>
                </div>
            </div>
            """
            st.markdown(metrics_html, unsafe_allow_html=True)

            if total_feedback > 0:
                satisfaction_rate = (positive_count / total_feedback) * 100
                st.progress(satisfaction_rate / 100)
                st.markdown(
                    f"<div style='text-align: center; font-weight: 500; color: #666;'>만족도: {satisfaction_rate:.1f}%</div>",
                    unsafe_allow_html=True)
        else:
            st.info("아직 피드백 데이터가 없습니다.")

        st.markdown("---")

        # 제출된 건의사항 목록
        st.subheader("📝 제출된 건의사항")
        if st.session_state.improvement_suggestions:
            for i, suggestion in enumerate(
                    reversed(st.session_state.improvement_suggestions)):
                with st.expander(
                        f"건의사항 {len(st.session_state.improvement_suggestions) - i}: {suggestion['timestamp']}"
                ):
                    st.write(suggestion['suggestion'])

            if st.button("🗑️ 건의사항 기록 삭제"):
                st.session_state.improvement_suggestions = []
                st.success("건의사항 기록이 삭제되었습니다!")
                st.rerun()
        else:
            st.info("아직 제출된 건의사항이 없습니다.")

    with tab5:
        st.header("📔 교육용 자료")

        # 파일 업로드 섹션
        st.subheader("📤 자료 업로드")

        # 업로드할 파일 선택
        uploaded_file = st.file_uploader(
            "교육용 자료를 업로드하세요",
            type=[
                'pdf', 'docx', 'doc', 'pptx', 'ppt', 'xlsx', 'xls', 'txt',
                'md', 'png', 'jpg', 'jpeg'
            ],
            help="지원 형식: PDF, Word, PowerPoint, Excel, 텍스트, 이미지 파일")

        # 파일 설명 입력
        file_description = st.text_area(
            "파일 설명", placeholder="업로드하는 자료에 대한 간단한 설명을 작성해주세요")

        # 카테고리 선택
        file_category = st.selectbox("카테고리", ["시스템 매뉴얼", "교육 자료", "가이드라인"])

        if uploaded_file is not None:
            # 파일 정보 표시
            st.markdown("---")
            st.markdown("**📄 업로드 파일 정보:**")

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**파일명:** {uploaded_file.name}")
                st.write(f"**파일 크기:** {uploaded_file.size:,} bytes")
            with col2:
                st.write(f"**파일 형식:** {uploaded_file.type}")
                st.write(f"**카테고리:** {file_category}")

            if file_description:
                st.write(f"**설명:** {file_description}")

            # 업로드 버튼
            if st.button("📤 파일 업로드", type="primary", use_container_width=True):
                try:
                    import os

                    # 업로드된 파일들을 저장할 디렉토리 생성
                    upload_dir = "education_materials"
                    if not os.path.exists(upload_dir):
                        os.makedirs(upload_dir)

                    # 파일 저장
                    file_path = os.path.join(upload_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    # 메타데이터 저장 (JSON 파일로)
                    import json
                    metadata_file = os.path.join(upload_dir, "metadata.json")

                    # 기존 메타데이터 로드
                    if os.path.exists(metadata_file):
                        with open(metadata_file, "r", encoding="utf-8") as f:
                            metadata = json.load(f)
                    else:
                        metadata = {}

                    # 새 파일 메타데이터 추가
                    metadata[uploaded_file.name] = {
                        "description": file_description,
                        "category": file_category,
                        "upload_time":
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "file_size": uploaded_file.size,
                        "file_type": uploaded_file.type
                    }

                    # 메타데이터 저장
                    with open(metadata_file, "w", encoding="utf-8") as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=2)

                    st.success(f"✅ '{uploaded_file.name}' 파일이 성공적으로 업로드되었습니다!")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ 파일 업로드 중 오류가 발생했습니다: {str(e)}")

        st.markdown("---")

        # 업로드된 파일 목록 및 다운로드 섹션
        st.subheader("📥 업로드된 자료 목록")

        import os
        import json

        upload_dir = "education_materials"
        metadata_file = os.path.join(upload_dir, "metadata.json")

        if os.path.exists(upload_dir) and os.path.exists(metadata_file):
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)

                if metadata:
                    # 카테고리 필터
                    categories = ["전체"] + list(
                        set([data["category"] for data in metadata.values()]))
                    selected_category = st.selectbox("카테고리 필터",
                                                     categories,
                                                     key="category_filter")

                    # 검색 기능
                    search_term = st.text_input("파일명 또는 설명 검색",
                                                placeholder="검색어를 입력하세요")

                    # 필터링된 파일 목록
                    filtered_files = {}
                    for filename, data in metadata.items():
                        # 카테고리 필터
                        if selected_category != "전체" and data[
                                "category"] != selected_category:
                            continue

                        # 검색 필터
                        if search_term and search_term.lower(
                        ) not in filename.lower() and search_term.lower(
                        ) not in data.get("description", "").lower():
                            continue

                        # 실제 파일이 존재하는지 확인
                        if os.path.exists(os.path.join(upload_dir, filename)):
                            filtered_files[filename] = data

                    if filtered_files:
                        st.markdown(f"**총 {len(filtered_files)}개의 파일**")

                        # 파일 목록을 카드 형태로 표시
                        for filename, data in filtered_files.items():
                            with st.expander(f"📄 {filename}", expanded=False):
                                col1, col2 = st.columns([3, 1])

                                with col1:
                                    st.markdown(
                                        f"**📝 설명:** {data.get('description', '설명 없음')}"
                                    )
                                    st.markdown(
                                        f"**📂 카테고리:** {data['category']}")
                                    st.markdown(
                                        f"**📅 업로드일:** {data['upload_time']}")
                                    st.markdown(
                                        f"**📊 파일 크기:** {data['file_size']:,} bytes"
                                    )
                                    if data.get('file_type'):
                                        st.markdown(
                                            f"**📎 파일 형식:** {data['file_type']}"
                                        )

                                with col2:
                                    # 다운로드 버튼
                                    file_path = os.path.join(
                                        upload_dir, filename)
                                    if os.path.exists(file_path):
                                        with open(file_path, "rb") as f:
                                            file_bytes = f.read()

                                        st.download_button(
                                            label="📥 다운로드",
                                            data=file_bytes,
                                            file_name=filename,
                                            key=f"download_{filename}",
                                            use_container_width=True)

                                        # 파일 삭제 버튼 (관리자용)
                                        if st.button("🗑️ 삭제",
                                                     key=f"delete_{filename}",
                                                     use_container_width=True,
                                                     help="이 파일을 삭제합니다"):
                                            try:
                                                # 파일 삭제
                                                os.remove(file_path)

                                                # 메타데이터에서 제거
                                                del metadata[filename]

                                                # 업데이트된 메타데이터 저장
                                                with open(
                                                        metadata_file,
                                                        "w",
                                                        encoding="utf-8") as f:
                                                    json.dump(
                                                        metadata,
                                                        f,
                                                        ensure_ascii=False,
                                                        indent=2)

                                                st.success(
                                                    f"✅ '{filename}' 파일이 삭제되었습니다!"
                                                )
                                                st.rerun()

                                            except Exception as e:
                                                st.error(
                                                    f"❌ 파일 삭제 중 오류가 발생했습니다: {str(e)}"
                                                )
                    else:
                        st.info("검색 조건에 맞는 파일이 없습니다.")
                else:
                    st.info("아직 업로드된 파일이 없습니다.")

            except Exception as e:
                st.error(f"❌ 파일 목록을 불러오는 중 오류가 발생했습니다: {str(e)}")
        else:
            st.info("아직 업로드된 파일이 없습니다.")

        st.markdown("---")

        # 사용 가이드
        with st.expander("📋 사용 가이드", expanded=False):
            st.markdown("""
            **📤 파일 업로드:**
            - 지원 형식: PDF, Word, PowerPoint, Excel, 텍스트, 이미지 파일
            - 각 파일에 대한 설명과 카테고리를 지정할 수 있습니다
            - 업로드된 파일은 서버에 안전하게 저장됩니다
            
            **📥 파일 다운로드:**
            - 업로드된 모든 파일을 카테고리별로 필터링할 수 있습니다
            - 파일명이나 설명으로 검색이 가능합니다
            - 각 파일의 상세 정보를 확인할 수 있습니다
            
            **🗑️ 파일 관리:**
            - 불필요한 파일은 삭제할 수 있습니다
            - 파일과 관련된 모든 메타데이터가 함께 관리됩니다
            
            **⚠️ 주의사항:**
            - 파일 업로드 시 중복된 파일명은 덮어쓰기됩니다
            - 삭제된 파일은 복구할 수 없으니 신중하게 삭제해주세요
            """)

    # 선택된 담당자 상세 보기 (사이드바에서 클릭한 경우)
    if hasattr(st.session_state, 'selected_admin'):
        with st.modal("담당자 상세 정보"):
            display_admin_card(st.session_state.selected_admin,
                               show_favorite_button=True,
                               context="modal")
            if st.button("닫기"):
                del st.session_state.selected_admin
                st.rerun()


if __name__ == "__main__":
    main()
