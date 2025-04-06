import utils
import streamlit as st
from streaming import StreamHandler
from langchain.chains import ConversationChain

st.set_page_config(
    page_title="🌐 VJCET Customer Service Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling with the new color scheme
st.markdown("""
<style>
    .header-section {
        background: linear-gradient(45deg, #004aad, #002850);
        color: #ffffff;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
    }
    .language-pill {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        background: #004aad;
        color: #ffffff;
        margin: 0.3rem;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        border: 1px solid #002850;
    }
    .chat-bubble {
        padding: 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    .user-bubble {
        background: #004aad;
        color: #ffffff;
        margin-left: auto;
        border: 1px solid #002850;
    }
    .assistant-bubble {
        background: rgba(255, 255, 255, 0.9);
        color: #000000;
        border: 1px solid #e0e0e0;
    }
    .hover-effect {
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .hover-effect:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .button-hover-effect:hover {
        background: #001529;
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown('<div class="header-section hover-effect"><h1>🌍 VJCET Multilingual Customer Support Agent</h1></div>', unsafe_allow_html=True)

# Language display
st.markdown("""
<div style="text-align: center; margin: 1rem 0;">
    <span class="language-pill hover-effect">🇺🇸 English</span>
    <span class="language-pill hover-effect">🇮🇳 Malayalam</span>
    <span class="language-pill hover-effect">🇮🇳 Hindi</span>
    <span class="language-pill hover-effect">🇮🇳 Tamil</span>
    <span class="language-pill hover-effect">🇸🇦 Arabic</span>
</div>
""", unsafe_allow_html=True)

class RegionalSupportAgent:

    def __init__(self):
        utils.sync_st_session()
        self.llm = utils.configure_llm()
        self.language_map = {
            "English": "en",
            "Malayalam": "ml",
            "Hindi": "hi",
            "Tamil": "ta",
            "Arabic": "ar"
        }
    
    def setup_chain(self):
        return ConversationChain(llm=self.llm, verbose=False)
    
    def language_selector(self):
        col1, col2 = st.columns([1, 3])
        with col1:
            return st.selectbox(
                "Choose Conversation Language:",
                list(self.language_map.keys()),
                format_func=lambda x: f"{self.get_flag(x)} {x}",
                key="lang_select"
            )
    
    def get_flag(self, language):
        flags = {
            "English": "🇺🇸",
            "Malayalam": "🇮🇳",
            "Hindi": "🇮🇳",
            "Tamil": "🇮🇳",
            "Arabic": "🇸🇦"
        }
        return flags.get(language, "🌐")
    
    @utils.enable_chat_history
    def main(self):
        chain = self.setup_chain()
        selected_lang = self.language_selector()
        
        user_query = st.chat_input(placeholder=f"Type your message in {selected_lang}...")
        
        if user_query:
            self.display_message(user_query, "user", selected_lang)
            self.generate_response(chain, user_query, selected_lang)
    
    def display_message(self, content, role, language):
        st.session_state.messages.append({
            "role": role,
            "content": content,
            "language": language
        })
    
    def generate_response(self, chain, query, language):
        with st.chat_message("assistant"):
            st_cb = StreamHandler(st.empty())
            try:
                lang_prompt = f"""Respond in {language} ({self.language_map[language]}) to the following:
                {query}
                Maintain natural conversational style and cultural appropriateness."""
                
                result = chain.invoke(
                    {"input": lang_prompt},
                    {"callbacks": [st_cb]}
                )
                response = result["response"]
                self.display_message(response, "assistant", language)
                utils.print_qa(RegionalSupportAgent, query, response)
                
            except Exception as e:
                error_msg = f"⚠️ Error: {str(e)}. Please try again or rephrase your question."
                self.display_message(error_msg, "assistant", language)

if __name__ == "__main__":
    agent = RegionalSupportAgent()
    agent.main()    