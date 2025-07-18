# Personal Portfolio Website

A professional portfolio website built with Streamlit, featuring data visualizations, project showcases, and personal information.

## Features

- 📊 Interactive data visualizations with Plotly
- 🎯 Project portfolio with GitHub integration
- 📈 Skills and experience showcase
- 📧 Contact form
- 🎨 Modern, responsive design
- 🔧 Easy customization through config.json

## Demo

[Live Demo](http://your-ec2-instance-public-ip:8501) (Replace with your actual URL)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/your-portfolio.git
   cd your-portfolio
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Customize your content**
   - Edit `config.json` with your personal information
   - Add your profile photo to `assets/profile.jpg`
   - Update project information in `app.py`

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

## Configuration

Edit `config.json` to customize your personal information:

```json
{
  "name": "Your Name",
  "title": "Data Scientist & Developer",
  "email": "your.email@example.com",
  "linkedin": "https://linkedin.com/in/yourprofile",
  "github": "https://github.com/yourusername",
  "bio": "Your bio goes here..."
}
```

## Deployment

### AWS EC2 Deployment

1. Launch a free-tier EC2 instance
2. Configure security groups (ports 80, 443, 22)
3. Clone your repository
4. Install dependencies
5. Run with PM2 process manager
6. Optional: Set up Nginx reverse proxy

See the detailed deployment guide in the project structure documentation.

## Technologies Used

- **Frontend**: Streamlit, HTML/CSS
- **Data Visualization**: Plotly, Pandas
- **Backend**: Python
- **Deployment**: AWS EC2, Nginx, PM2
- **Version Control**: Git

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

- Email: your.email@example.com
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)
- GitHub: [Your GitHub](https://github.com/yourusername)

## Acknowledgments

- Streamlit team for the amazing framework
- Plotly for interactive visualizations
- AWS for hosting infrastructure