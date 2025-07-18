import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import json

# Configure page
st.set_page_config(
    page_title="Peter Kelly - Portfolio",
    page_icon="👨‍💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def load_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .section-header {
        font-size: 2rem;
        font-weight: bold;
        margin: 2rem 0 1rem 0;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem;
    }
    
    .project-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .skill-tag {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.8rem;
    }
    
    .contact-link {
        display: inline-block;
        margin: 0.5rem 1rem 0.5rem 0;
        padding: 0.5rem 1rem;
        background: #667eea;
        color: white;
        text-decoration: none;
        border-radius: 5px;
        transition: background 0.3s;
    }
    
    .contact-link:hover {
        background: #764ba2;
    }
    </style>
    """, unsafe_allow_html=True)

# Load configuration
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "name": "Peter Kelly",
            "title": "Data Analyst",
            "email": "testemail@gmail.com",
            "linkedin": "https://linkedin.com/in/yourprofile",
            "github": "https://github.com/yourusername",
            "bio": "Passionate about data science and web development..."
        }

# Sidebar navigation
def sidebar():
    st.sidebar.title("Navigation")
    pages = ["Home", "About", "Projects", "Data Visualizations", "Skills", "Contact"]
    return st.sidebar.selectbox("Go to", pages)

# Home page
def home_page(config):
    st.markdown(f'<h1 class="main-header">{config["name"]}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align: center; font-size: 1.5rem; color: #666;">{config["title"]}</p>', unsafe_allow_html=True)
    
    # Profile image (if available)
    try:
        profile_img = Image.open('assets/profile.jpg')
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(profile_img, width=300)
    except FileNotFoundError:
        st.info("Add your profile image to assets/profile.jpg")
    
    # Quick intro
    st.markdown(f'<div class="section-header">Welcome!</div>', unsafe_allow_html=True)
    st.write(config["bio"])
    
    # Quick stats or highlights
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Projects Completed", "12")
    with col2:
        st.metric("Technologies Used", "15+")
    with col3:
        st.metric("Years Experience", "3")
    with col4:
        st.metric("Coffee Cups", "∞")

# About page
def about_page(config):
    st.markdown(f'<div class="section-header">About Me</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("""
        I'm a passionate data scientist and developer with experience in building 
        data-driven applications and creating insightful visualizations. 
        
        My journey started with curiosity about how data can tell stories and solve 
        real-world problems. Over the years, I've worked on various projects ranging 
        from machine learning models to interactive web applications.
        
        When I'm not coding, you can find me exploring new technologies, contributing 
        to open-source projects, or enjoying a good cup of coffee while reading about 
        the latest developments in AI and data science.
        """)
        
        st.subheader("Experience")
        st.write("""
        **Data Scientist** - Company Name (2022 - Present)
        - Developed machine learning models for predictive analytics
        - Created interactive dashboards using Python and Streamlit
        - Collaborated with cross-functional teams to deliver data solutions
        
        **Junior Developer** - Previous Company (2021 - 2022)
        - Built web applications using Python and JavaScript
        - Worked on data pipeline optimization
        - Contributed to open-source projects
        """)
    
    with col2:
        st.subheader("Education")
        st.write("""
        **Master's in Data Science**
        University Name (2021)
        
        **Bachelor's in Computer Science**
        University Name (2019)
        """)
        
        st.subheader("Certifications")
        st.write("""
        - AWS Certified Cloud Practitioner
        - Google Analytics Certified
        - Python for Data Science (Coursera)
        """)

# Projects page
def projects_page():
    st.markdown(f'<div class="section-header">Projects</div>', unsafe_allow_html=True)
    
    projects = [
        {
            "name": "Sales Dashboard",
            "description": "Interactive dashboard for sales analytics with real-time data visualization.",
            "tech": ["Python", "Streamlit", "Plotly", "Pandas"],
            "link": "https://github.com/yourusername/sales-dashboard"
        },
        {
            "name": "Customer Segmentation ML",
            "description": "Machine learning model for customer segmentation using clustering algorithms.",
            "tech": ["Python", "Scikit-learn", "Jupyter", "Seaborn"],
            "link": "https://github.com/yourusername/customer-segmentation"
        },
        {
            "name": "Stock Price Predictor",
            "description": "LSTM neural network for predicting stock prices with technical indicators.",
            "tech": ["Python", "TensorFlow", "Pandas", "yfinance"],
            "link": "https://github.com/yourusername/stock-predictor"
        }
    ]
    
    for project in projects:
        st.markdown(f"""
        <div class="project-card">
            <h3>{project['name']}</h3>
            <p>{project['description']}</p>
            <div>
                {''.join([f'<span class="skill-tag">{tech}</span>' for tech in project['tech']])}
            </div>
            <br>
            <a href="{project['link']}" target="_blank" class="contact-link">View Project</a>
        </div>
        """, unsafe_allow_html=True)

# Data Visualizations page
def visualizations_page():
    st.markdown(f'<div class="section-header">Data Visualizations</div>', unsafe_allow_html=True)
    
    # Sample data for demonstrations
    sample_data = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Sales': [1000, 1200, 900, 1500, 1800, 2000],
        'Profit': [200, 300, 150, 400, 600, 700]
    })
    
    tab1, tab2, tab3 = st.tabs(["📈 Sales Trends", "🌍 Geographic Data", "📊 Custom Analysis"])
    
    with tab1:
        st.subheader("Sales Performance Over Time")
        fig = px.line(sample_data, x='Month', y=['Sales', 'Profit'], 
                     title="Monthly Sales and Profit Trends")
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            fig_bar = px.bar(sample_data, x='Month', y='Sales', 
                           title="Monthly Sales Volume")
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            fig_pie = px.pie(values=sample_data['Profit'], names=sample_data['Month'],
                           title="Profit Distribution by Month")
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab2:
        st.subheader("Geographic Visualization")
        st.info("This section would contain interactive maps and geographic analysis")
        # Add your geographic visualizations here
        
    with tab3:
        st.subheader("Interactive Analysis")
        st.write("Upload your own data for custom visualizations:")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write(df.head())
            
            if len(df.columns) >= 2:
                x_col = st.selectbox("Select X axis", df.columns)
                y_col = st.selectbox("Select Y axis", df.columns)
                chart_type = st.selectbox("Chart Type", ["Line", "Bar", "Scatter"])
                
                if chart_type == "Line":
                    fig = px.line(df, x=x_col, y=y_col)
                elif chart_type == "Bar":
                    fig = px.bar(df, x=x_col, y=y_col)
                else:
                    fig = px.scatter(df, x=x_col, y=y_col)
                
                st.plotly_chart(fig, use_container_width=True)

# Skills page
def skills_page():
    st.markdown(f'<div class="section-header">Skills & Technologies</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Programming Languages")
        skills_prog = ["Python", "R", "SQL", "JavaScript", "HTML/CSS"]
        for skill in skills_prog:
            st.progress(0.8, text=skill)
        
        st.subheader("Data Science & ML")
        skills_ds = ["Pandas", "NumPy", "Scikit-learn", "TensorFlow", "Plotly"]
        for skill in skills_ds:
            st.progress(0.7, text=skill)
    
    with col2:
        st.subheader("Web Development")
        skills_web = ["Streamlit", "Flask", "FastAPI", "React", "Node.js"]
        for skill in skills_web:
            st.progress(0.6, text=skill)
        
        st.subheader("Cloud & Tools")
        skills_cloud = ["AWS", "Docker", "Git", "Jupyter", "VS Code"]
        for skill in skills_cloud:
            st.progress(0.7, text=skill)

# Contact page
def contact_page(config):
    st.markdown(f'<div class="section-header">Get In Touch</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("I'm always interested in new opportunities and collaborations. Feel free to reach out!")
        
        # Contact form
        with st.form("contact_form"):
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            message = st.text_area("Message", height=150)
            submit = st.form_submit_button("Send Message")
            
            if submit:
                st.success("Thank you for your message! I'll get back to you soon.")
    
    with col2:
        st.markdown(f"""
        <div style="margin-top: 2rem;">
            <h3>Connect with me:</h3>
            <a href="mailto:{config['email']}" class="contact-link">📧 Email</a><br>
            <a href="{config['linkedin']}" target="_blank" class="contact-link">💼 LinkedIn</a><br>
            <a href="{config['github']}" target="_blank" class="contact-link">🐱 GitHub</a><br>
        </div>
        """, unsafe_allow_html=True)

# Main app
def main():
    load_css()
    config = load_config()
    
    # Sidebar navigation
    page = sidebar()
    
    # Page routing
    if page == "Home":
        home_page(config)
    elif page == "About":
        about_page(config)
    elif page == "Projects":
        projects_page()
    elif page == "Data Visualizations":
        visualizations_page()
    elif page == "Skills":
        skills_page()
    elif page == "Contact":
        contact_page(config)

if __name__ == "__main__":
    main()