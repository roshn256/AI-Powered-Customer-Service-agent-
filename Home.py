import streamlit as st

# Page configuration
st.set_page_config(
    page_title="VJCET Customer Service Agent",
    page_icon='🏛️',
    layout='wide',
    initial_sidebar_state="expanded"
)

# Custom CSS for styling and effects
st.markdown("""
<style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css');

    body {
        background-image: url('C:\\Users\\rosha\\Videos\\mp_rd\\langchain-chatbot-master\\images\\maxresdefault.jpg'); /* Use a URL or relative path */
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: var(--text-color); /* Dynamic text color */
    }
    .overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5); /* Semi-transparent overlay */
        z-index: -1;
    }
    .feature-box {
        padding: 20px;
        border-radius: 10px;
        border: 1px solid var(--border-color);
        margin: 10px 0;
        background-color: var(--background-color); /* Dynamic background color */
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        color: var(--text-color); /* Dynamic text color */
    }
    .feature-box:hover {
        transform: translateY(-5px); /* Slight lift on hover */
        box-shadow: 0 4px 8px rgba(0,0,0,0.2); /* Enhanced shadow on hover */
    }
    .header-box {
        background: linear-gradient(45deg, #004aad, #002850);
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        animation: fadeInDown 1s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .college-info {
        padding: 25px;
        background: var(--info-background); /* Dynamic background color */
        border-radius: 15px;
        margin: 20px 0;
        animation: fadeIn 1.5s;
        transition: background-color 0.3s ease;
        color: var(--text-color); /* Dynamic text color */
    }
    .college-info:hover {
        background-color: var(--info-background-hover); /* Dynamic background color on hover */
    }
    .animate__animated {
        --animate-duration: 1s;
    }
    /* Custom hover effect for images */
    .image-container {
        border-radius: 15px;
        overflow: hidden;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .image-container:hover {
        transform: scale(1.05); /* Slight zoom on hover */
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    /* Enhanced button styling */
    .stButton>button {
        border: 2px solid #004aad;
        border-radius: 20px;
        padding: 10px 24px;
        background-color: #004aad;
        color: white;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #002850;
        border-color: #002850;
        transform: scale(1.05);
    }
    /* Dark mode compatibility */
    @media (prefers-color-scheme: dark) {
        :root {
            --text-color: #ffffff;
            --background-color: rgba(45, 45, 45, 0.9);
            --info-background: rgba(30, 30, 30, 0.9);
            --info-background-hover: rgba(30, 30, 30, 1);
            --border-color: #444;
        }
        body {
            background-color: #121212;
        }
        .header-box {
            background: linear-gradient(45deg, #002850, #001529);
        }
        .stButton>button {
            background-color: #002850;
            border-color: #002850;
        }
        .stButton>button:hover {
            background-color: #001529;
            border-color: #001529;
        }
    }
    /* Light mode compatibility */
    @media (prefers-color-scheme: light) {
        :root {
            --text-color: #000000;
            --background-color: rgba(255, 255, 255, 0.9);
            --info-background: rgba(240, 248, 255, 0.9);
            --info-background-hover: rgba(240, 248, 255, 1);
            --border-color: #e0e0e0;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown('<div class="header-box animate__animated animate__fadeInDown"><h1>🏛️ VJCET Customer Service Agent</h1></div>', unsafe_allow_html=True)
st.markdown("## Your Intelligent Campus Support Solution")

# Features Section
st.markdown("## Key Features")
col1, col2, col3 = st.columns(3)  # Three columns for three features

# Feature 1: Document-Based Chat Assistant
with col1:
    st.markdown("""
    <div class="feature-box animate__animated animate__fadeInUp">
        <h3>📄 Document-Based Chat Assistant</h3>
        <ul>
            <li>Instant answers from college documents</li>
            <li>Academic policies clarification</li>
            <li>Examination system support</li>
            <li>Curriculum-related queries</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Feature 2: Website Interactive Chat
with col2:
    st.markdown("""
    <div class="feature-box animate__animated animate__fadeInUp">
        <h3>🌐 Website Interactive Chat</h3>
        <ul>
            <li>Real-time website navigation assistance</li>
            <li>Admission process guidance</li>
            <li>Event updates and information</li>
            <li>Department-specific support</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Feature 3: AI-Powered Support
with col3:
    st.markdown("""
    <div class="feature-box animate__animated animate__fadeInUp">
        <h3>🤖 Basic Chatbot</h3>
        <ul>
            <li>24/7 automated assistance</li>
            <li>Personalized responses</li>
            <li>Multi-language support</li>
            <li>Integration with college systems</li>
            <li>Handles unlimited queries</li>
            <li>Provides immediate access</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# College Information Section
st.markdown("---")
st.markdown('<div class="college-info animate__animated animate__fadeIn"><h2>🏫 About Viswajyothi College of Engineering & Technology</h2></div>', unsafe_allow_html=True)

# College Image and Text
col_img, col_text = st.columns([1, 2])

with col_img:
    st.image(
        'C:\\Users\\rosha\\OneDrive\\Desktop\\projects\\mp_rd\\langchain-chatbot-master\\images\\th.jpeg',  # Replace with your image URL or local path
        use_container_width=True
    )

# College Description
with col_text:
    st.markdown("""
    **Viswajyothi College of Engineering & Technology (VJCET)**, located in Vazhakulam, Kerala, is a premier technical institution 
    established in 2001. Affiliated to APJ Abdul Kalam Technological University, the college offers undergraduate and 
    postgraduate programs in engineering and technology.
    
    ### Key Highlights:
    - NAAC Accredited with 'A' Grade
    - 15+ Undergraduate programs
    - 8 Postgraduate programs
    - Strong industry-academia collaboration
    
    Guided by the vision of *"Moulding Engineers with Social Commitment"*, VJCET continues to be a center of excellence 
    in technical education, fostering innovation and ethical leadership among students.
    """)
