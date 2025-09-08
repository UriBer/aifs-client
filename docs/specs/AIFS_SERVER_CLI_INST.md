# AIFS - AI-Native File System

AI-native File System - Designing and implementing an AI-native file system to replace ext4, NTFS (or any traditional file system) means re-thinking storage from the ground up so that it is built **for** machine-learning, vector search, semantic retrieval, continuous training and inference pipelines — not just for human-named files and folders.


## 🚀 Usage Examples

### Start the Server
```bash
python start_server.py --port 50051 --storage-dir ~/.aifs
```

### Use the CLI
```bash
# Store an asset
python aifs_cli.py put --kind blob ./tests/files/data.txt 

# Search for assets
python aifs_cli.py search --query "test data"

# Create a snapshot
python aifs_cli.py snapshot --namespace test --assets asset1,asset2

# List assets
python aifs_cli.py list
```

### Use the Python Client
```python
from aifs.client import AIFSClient

# Connect to server
client = AIFSClient("localhost:50051")

# Store asset
asset_id = client.put_asset(
    data=b"Hello, AIFS!",
    kind="blob",
    metadata={"description": "Test asset"}
)

# Retrieve asset
asset = client.get_asset(asset_id)

# Vector search
results = client.vector_search(query_embedding, k=10)
```

### Use the FUSE Layer
```bash
# Mount AIFS as a filesystem
python -c "
from aifs.fuse import AIFSFuse
from aifs.client import AIFSClient
import fuse

client = AIFSClient('localhost:50051')
fuse_ops = AIFSFuse(client, 'default')
fuse.FUSE(fuse_ops, '/mnt/aifs')
"
```

## 🔧 Configuration

### Environment Variables
```bash
export AIFS_ROOT_DIR=~/.aifs           # Data directory
export AIFS_SERVER_PORT=50051          # Server port
export AIFS_ENCRYPTION_KEY=your_key    # Encryption key (32 bytes)
export AIFS_PRIVATE_KEY=your_priv_key  # Ed25519 private key
```

### Server Configuration
```python
# Custom configuration
from aifs.server import serve

serve(
    root_dir="~/.aifs",
    port=50051,
    max_workers=20
)
```

## 🔒 Security Features

### Encryption
- **AES-256-GCM**: Military-grade encryption for all data
- **Key Derivation**: HKDF-based key derivation
- **Nonce Management**: Secure random nonce generation
- **Authenticated Encryption**: Integrity and confidentiality

### Authentication
- **Ed25519 Signatures**: Fast, secure digital signatures
- **Public Key Verification**: Cryptographic proof of authenticity
- **Timestamp Validation**: Prevents replay attacks
- **Namespace Isolation**: Multi-tenant security

### Authorization
- **Macaroon Tokens**: Capability-based access control
- **Method Restrictions**: Fine-grained permission control
- **Namespace Scoping**: Resource isolation
- **Expiry Management**: Time-limited access tokens

## 📊 Performance Characteristics

### Storage Performance
- **Content Deduplication**: Eliminates redundant storage
- **Sharded Storage**: Efficient file system organization
- **Compression**: zstd compression for space efficiency
- **Streaming I/O**: Efficient large file handling

### Search Performance
- **FAISS Integration**: High-performance vector search (when available)
- **scikit-learn Fallback**: Functional vector search (slower)
- **Index Optimization**: Optimized for similarity queries
- **Caching**: Metadata and embedding caching
- **Parallel Processing**: Multi-threaded operations

### Network Performance
- **gRPC Streaming**: Efficient data transfer
- **Compression**: zstd compression for network efficiency
- **Connection Pooling**: Reusable connections
- **Load Balancing**: Ready for horizontal scaling

## 🚧 Limitations & Future Work

### Current Limitations
- **Hash Algorithm**: Uses SHA-256 instead of BLAKE3 (Rust dependency)
- **Vector Search**: Falls back to scikit-learn if FAISS unavailable
- **Performance**: Local implementation, not production-optimized
- **Scalability**: Single-node implementation
- **Monitoring**: Basic metrics only

### Planned Improvements
- **BLAKE3 Integration**: Install Rust for full spec compliance
- **FAISS Optimization**: Ensure FAISS is always available
- **Performance Optimization**: Meet RFC performance targets
- **Distributed Storage**: Multi-node deployment
- **Advanced Monitoring**: OpenTelemetry integration
- **Load Testing**: Performance benchmarking
- **Security Audit**: Penetration testing

## 🐛 Troubleshooting

### Common Issues

#### FAISS Installation Problems
```
error: command 'swig' failed: No such file or directory
```
**Solutions**:
1. **Use the FAISS installer**: `python install_faiss.py`
2. **Install system dependencies**:
   - macOS: `brew install swig libomp openblas cmake`
   - Ubuntu: `sudo apt-get install swig libomp-dev openblas-dev cmake`
3. **Use conda**: `conda install -c conda-forge faiss-cpu`
4. **Accept fallback**: System will use scikit-learn automatically

#### Rust Compilation Error
```
error: Cargo, the Rust package manager, is not installed
```
**Solution**: Install Rust or use the SHA-256 implementation (current default)

#### Permission Errors
```
error: Permission denied
```
**Solution**: Check file permissions and run with appropriate user

#### Port Already in Use
```
error: Address already in use
```
**Solution**: Change port or stop existing service

### Debug Mode
```bash
# Enable debug logging
export AIFS_LOG_LEVEL=DEBUG
python start_server.py

# Run tests with verbose output
python run_tests.py --verbose
```

### Performance Tuning
```bash
# Check vector database backend
python -c "from aifs.vector_db import VectorDB; vdb = VectorDB('/tmp'); print(vdb.get_stats())"

# Verify FAISS installation
python -c "import faiss; print('FAISS version:', faiss.__version__)"
```

## 📚 API Reference

### Core Classes

#### AssetManager
```python
class AssetManager:
    def put_asset(data, kind, embedding=None, metadata=None, parents=None)
    def get_asset(asset_id)
    def vector_search(query_embedding, k=10)
    def create_snapshot(namespace, asset_ids, metadata=None)
    def verify_snapshot(snapshot_id, public_key)
```

#### StorageBackend
```python
class StorageBackend:
    def put(data)
    def get(hash_hex)
    def exists(hash_hex)
    def delete(hash_hex)
    def get_chunk_info(hash_hex)
```

#### CryptoManager
```python
class CryptoManager:
    def sign_snapshot(merkle_root, timestamp, namespace)
    def verify_snapshot_signature(signature, merkle_root, timestamp, namespace, public_key)
    def get_public_key()
```

#### MerkleTree
```python
class MerkleTree:
    def get_root_hash()
    def get_proof(asset_id)
    def verify_proof(asset_id, proof, root_hash)
```

#### VectorDB
```python
class VectorDB:
    def add(asset_id, embedding)
    def search(query_embedding, k=10)
    def delete(asset_id)
    def get_stats()  # Shows backend (FAISS or scikit-learn)
```

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone https://github.com/UriBer/AIFS.git
cd local_implementation

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8

# Run code formatting
black aifs/ tests/

# Run linting
flake8 aifs/ tests/

# Run tests with coverage
pytest --cov=aifs tests/
```

### Code Style
- **Python**: PEP 8 compliance
- **Type Hints**: Full type annotation
- **Documentation**: Comprehensive docstrings
- **Testing**: 90%+ test coverage target

## 📄 License

This implementation is provided under the same license as the main project. See the LICENSE file for details.

## 🙏 Acknowledgments

- **Open Source Community**: For the excellent libraries used

---

## 📖 Documentation

- **Architecture Specification**: See [docs/spec/rfc/0001-aifs-architecture.md](docs/spec/rfc/0001-aifs-architecture.md)
- **Implementation Guide**: See [local_implementation/README_IMPLEMENTATION.md](local_implementation/README_IMPLEMENTATION.md)
- **Changelog**: See [docs/CHANGELOG.md](docs/CHANGELOG.md)

**Note**: This implementation prioritizes functionality and security over performance optimization. For production deployment, additional performance tuning and security hardening is recommended.

**Vector Search Note**: The system automatically falls back to scikit-learn if FAISS is unavailable, ensuring functionality while maintaining the option for high-performance vector search when FAISS is properly installed.
