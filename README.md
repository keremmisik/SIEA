# SIEA - Smart Invoice Entry Automation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)

## 🎯 Overview

SIEA (Smart Invoice Entry Automation) is an intelligent invoice processing system that enables users to scan or photograph invoices for automatic data extraction. Built with modern web technologies and AI-powered OCR, it automatically extracts invoice data and stores it securely with enterprise-grade encryption.

## ✨ Features

- 📷 **Camera Integration**: Real-time invoice scanning with web camera
- 📁 **File Upload**: Drag & drop invoice photo upload
- 🤖 **AI-Powered OCR**: Google Gemini 1.5 Flash for intelligent data extraction
- 🗄️ **Secure Storage**: PostgreSQL database with AES-256 encryption
- 📊 **Excel Export**: Styled Excel file generation (.xlsx)
- 🔒 **Data Security**: 5-year automatic data retention policy
- 👤 **User Management**: JWT-based authentication system
- 📱 **Responsive Design**: Mobile and desktop compatible interface
- 🎨 **Modern UI**: User-friendly interface designed with Tailwind CSS
- 🌐 **Multi-language**: Turkish and English invoice support
- 🐳 **Containerized**: Full Docker support for easy deployment

## 🛠 Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT + bcrypt
- **AI OCR**: Google Gemini 1.5 Flash
- **Excel Export**: pandas + openpyxl + xlsxwriter
- **Encryption**: cryptography (Fernet)

### Frontend
- **Framework**: React.js 18
- **Routing**: React Router DOM
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Camera**: react-webcam
- **File Upload**: react-dropzone
- **Notifications**: react-toastify
- **HTTP Client**: Axios

### DevOps & Deployment
- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx
- **SSL**: Let's Encrypt ready
- **Database Migration**: Custom migration system

## 📋 System Requirements

- **Python**: 3.8+
- **Node.js**: 16+
- **PostgreSQL**: 12+
- **Google Gemini API Key**

## 🚀 Quick Setup

### Option 1: Automatic Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/SIEA.git
cd SIEA

# Run automatic setup
python setup.py
```

### Option 2: Manual Setup

#### 1. Environment Configuration

```bash
# Copy environment template
cp backend/env_example.txt backend/.env

# Generate secure keys
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
```

Update `backend/.env` with your values:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/siea_db
SECRET_KEY=your-generated-secret-key
ENCRYPTION_KEY=your-generated-encryption-key
GEMINI_API_KEY=your-gemini-api-key
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=.jpg,.jpeg,.png,.pdf
```

#### 2. Database Setup

```bash
# Install PostgreSQL and create database
createdb siea_db

# Run migrations
cd backend
python database/migrations.py
```

#### 3. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

#### 4. Frontend Setup

```bash
cd frontend
npm install
npm start
```

## 🐳 Docker Setup

### Development Environment

```bash
docker-compose -f docker-compose.dev.yml up --build
```

### Production Environment

```bash
docker-compose up --build
```

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | User registration |
| POST | `/auth/login` | User login |
| POST | `/invoices/upload` | Upload and process invoice |
| GET | `/invoices` | Get user's invoices |
| GET | `/invoices/export/excel` | Export invoices to Excel |
| POST | `/debug/ocr` | Debug OCR processing |

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | - |
| `SECRET_KEY` | JWT secret key | - |
| `ENCRYPTION_KEY` | Fernet encryption key | - |
| `GEMINI_API_KEY` | Google Gemini API key | - |
| `MAX_FILE_SIZE` | Maximum upload size (bytes) | 10485760 |
| `ALLOWED_EXTENSIONS` | Allowed file extensions | .jpg,.jpeg,.png,.pdf |

### Getting Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

## 🏗️ Project Structure

```
SIEA/
├── backend/                 # FastAPI backend
│   ├── database/           # Database models and migrations
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic services
│   ├── main.py            # FastAPI application
│   └── requirements.txt   # Python dependencies
├── frontend/               # React frontend
│   ├── public/            # Static files
│   ├── src/               # React source code
│   │   ├── components/    # Reusable components
│   │   ├── contexts/      # React contexts
│   │   ├── pages/         # Page components
│   │   └── App.js         # Main App component
│   └── package.json       # Node.js dependencies
├── scripts/               # Deployment scripts
├── docker-compose.yml     # Production Docker setup
├── docker-compose.dev.yml # Development Docker setup
└── README.md             # This file
```

## 🔒 Security Features

- **Data Encryption**: All sensitive data encrypted with Fernet (AES-256)
- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt with salt
- **SQL Injection Protection**: SQLAlchemy ORM
- **CORS Protection**: Configurable CORS settings
- **File Validation**: Type and size validation
- **Data Retention**: Automatic cleanup after 5 years

## 🤖 OCR Processing

### Supported Invoice Data

- **Company Name**: Extracted from the top of the invoice
- **Invoice Number**: Found after "FATURA NO:", "INVOICE NO:", etc.
- **Invoice Date**: Date in DD.MM.YYYY or DD/MM/YYYY format
- **Total Amount**: Total amount without currency symbol
- **Tax Amount**: VAT/KDV amount without currency symbol

### AI Model

- **Model**: Google Gemini 1.5 Flash
- **Languages**: Turkish and English
- **Accuracy**: High accuracy with structured prompts
- **Fallback**: Regex-based extraction for non-JSON responses

## 📊 Data Model

### User
- ID, email, full name, password hash
- Creation and update timestamps
- Active status

### Invoice
- ID, filename, processing timestamp
- Extracted data (encrypted JSON)
- Company name, invoice number, date
- Total amount, tax amount
- User relationship
- Expiration date (5 years)

## 🚀 Performance Optimizations

- **Database Indexing**: Optimized queries with proper indexes
- **Image Processing**: Efficient image handling
- **Lazy Loading**: Frontend components loaded on demand
- **Code Splitting**: Optimized bundle sizes
- **Caching**: Session caching with potential Redis integration

## 🧪 Testing

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

## 📦 Deployment

### Production Deployment

1. **Server Setup**:
   ```bash
   # Install Docker and Docker Compose
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```

2. **SSL Configuration**:
   ```bash
   # Update nginx.conf with your domain
   # Configure Let's Encrypt
   ```

3. **Deploy**:
   ```bash
   ./scripts/deploy-production.sh
   ```

### Cloud Deployment Options

- **Heroku**: Use provided Procfile
- **Railway**: Direct deployment support
- **AWS**: ECS with provided Docker images
- **DigitalOcean**: App Platform compatible

## 🔧 Troubleshooting

### Common Issues

1. **Gemini API Errors**:
   - Verify API key is correct
   - Check API quotas and limits
   - Ensure proper image format

2. **Database Connection**:
   - Verify PostgreSQL is running
   - Check connection string format
   - Ensure database exists

3. **Frontend Build Issues**:
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Check Node.js version compatibility

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export DEBUG=true
```

## 🗺️ Roadmap

- [ ] **Multi-language Support**: Additional language support
- [ ] **Batch Processing**: Multiple invoice upload
- [ ] **API Integration**: Third-party accounting software
- [ ] **Mobile App**: React Native mobile application
- [ ] **Advanced Analytics**: Invoice analytics dashboard
- [ ] **Cloud Storage**: AWS S3 integration
- [ ] **OCR Improvements**: Custom model training

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint for JavaScript code
- Write tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check this README and code comments
- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

## 🙏 Acknowledgments

- **Google Gemini**: AI-powered OCR capabilities
- **FastAPI**: High-performance Python web framework
- **React**: Frontend user interface library
- **Tailwind CSS**: Utility-first CSS framework
- **PostgreSQL**: Robust database system

---

**Made with ❤️ for efficient invoice processing**