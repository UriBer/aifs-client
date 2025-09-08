# AIFS Client - AI-Native File System Client

A modern web application for managing and interacting with AIFS (AI-Native File System) with built-in RAG (Retrieval-Augmented Generation) capabilities. This client connects to a real AIFS server via gRPC for asset storage, vector search, and lineage tracking.

## 🚀 Features

- **Asset Management**: Upload, organize, and manage files in AIFS server
- **Intelligent Search**: Semantic search using AIFS vector database
- **RAG Integration**: Built-in Q&A system using OpenAI GPT-4 with AIFS context
- **Visual Lineage**: Interactive visualization of asset relationships from AIFS
- **Real AIFS Integration**: Direct gRPC connection to AIFS server for all operations
- **Modern UI**: Responsive design with Tailwind CSS and real-time progress tracking

## 🏗️ Architecture

```
Frontend (Next.js) ↔ Backend (FastAPI) ↔ AIFS Server (gRPC)
                                    ↕
                            OpenAI API (GPT-4, Embeddings)
```

The backend acts as a bridge between the web frontend and the AIFS server, handling:
- File uploads to AIFS storage
- Vector search through AIFS database
- Asset lineage tracking via AIFS relationships
- RAG conversations with AIFS context

## 📋 Prerequisites

- Node.js 18+
- Python 3.11+
- AIFS server running on localhost:50051 (see AIFS setup below)
- OpenAI API key (for RAG functionality)

## 🛠️ Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd aifs-client
```

### 2. AIFS Server Setup

First, you need to have the AIFS server running. If you have the AIFS implementation:

```bash
# Navigate to AIFS directory
cd /path/to/AIFS/local_implementation

# Start the AIFS server
python start_server.py --host localhost --port 50051
```

The AIFS server should be running on `localhost:50051` before starting the client.

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the backend
python main.py
```

The backend will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Run the frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🔧 Configuration

### Backend Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Application
ENVIRONMENT=development
DEBUG=true

# AIFS Server (Required)
AIFS_SERVER_HOST=localhost
AIFS_SERVER_PORT=50051
AIFS_SERVER_USE_TLS=false
AIFS_API_KEY=your_aifs_api_key

# OpenAI (Required for RAG functionality)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

# File Upload
MAX_FILE_SIZE=104857600  # 100MB
```

### Frontend Environment Variables

Create a `.env.local` file in the `frontend` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📚 API Documentation

Once the backend is running, you can access the interactive API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔗 AIFS Integration

This client is designed to work with a real AIFS server. The integration includes:

### gRPC Services Used

- **AIFS Service**: Core asset operations (PutAsset, GetAsset, ListAssets, VectorSearch, CreateSnapshot)
- **Health Service**: Server connectivity checks
- **Admin Service**: Namespace and policy management

### Key Features

- **Real Asset Storage**: Files are stored in AIFS server, not locally
- **Vector Search**: Uses AIFS vector database for semantic search
- **Lineage Tracking**: Asset relationships are managed by AIFS
- **Snapshots**: Create and manage asset snapshots for versioning
- **Metadata**: Rich metadata support with AIFS schema

### Connection Status

The backend will automatically connect to the AIFS server on startup. Check the logs for connection status:

```
INFO - Connected to AIFS server at localhost:50051
INFO - AIFS client initialized successfully
```

If the AIFS server is not running, the backend will log warnings but continue to operate (some features will be limited).

## 🧪 Development

### Backend Development

```bash
cd backend

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Format code
black app/

# Lint code
flake8 app/
```

### Frontend Development

```bash
cd frontend

# Run development server
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Lint code
npm run lint

# Type check
npm run type-check
```

## 🚀 Production Deployment

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build individual services
docker build -t aifs-client-backend ./backend
docker build -t aifs-client-frontend ./frontend
```

### Manual Deployment

1. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm run build
   npm start
   ```

## 📖 Usage

### 1. Upload Assets

- Click the "Upload" button in the asset browser
- Drag and drop files or click to select
- Files are automatically processed and indexed

### 2. Search Assets

- Use the global search bar to find assets
- Supports both text and semantic search
- Filter results by type, tags, date, and size

### 3. RAG Chat

- Navigate to the RAG Chat section
- Select documents for context
- Ask questions about your documents
- Get AI-powered answers with source citations

### 4. View Lineage

- Navigate to the Lineage section
- Visualize asset relationships and transformations
- Explore data flow and dependencies

## 🔌 API Integration

### Upload Asset

```bash
curl -X POST "http://localhost:8000/api/v1/assets" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
  -F "name=My Document" \
  -F "tags=ml,research"
```

### Search Assets

```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning",
    "filters": {"type": "file"},
    "page": 1,
    "per_page": 20
  }'
```

### RAG Chat

```bash
curl -X POST "http://localhost:8000/api/v1/conversations/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "What are the main topics in the ML guide?",
    "context_assets": ["asset_id_1", "asset_id_2"]
  }'
```

## 🐛 Troubleshooting

### Common Issues

1. **Backend won't start**:
   - Check if port 8000 is available
   - Verify Python dependencies are installed
   - Check environment variables

2. **Frontend won't connect to backend**:
   - Verify `NEXT_PUBLIC_API_URL` is correct
   - Check if backend is running
   - Check CORS settings

3. **AIFS connection fails**:
   - Verify AIFS server is running
   - Check connection settings
   - The app works without AIFS server (mock mode)

4. **OpenAI API errors**:
   - Verify API key is correct
   - Check API quota and billing
   - RAG features will be disabled without OpenAI

### Debug Mode

```bash
# Backend debug
export AIFS_LOG_LEVEL=DEBUG
python main.py

# Frontend debug
npm run dev -- --verbose
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Write tests for new features
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 and embedding models
- FastAPI for the backend framework
- Next.js for the frontend framework
- Tailwind CSS for styling
- The open-source community

## 📞 Support

For support and questions:

- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting section

---

**Note**: This is a development version. For production use, additional security hardening and performance optimization is recommended.
