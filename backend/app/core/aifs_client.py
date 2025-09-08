"""
AIFS client integration for communicating with AIFS server.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any, BinaryIO
import grpc
from grpc import aio

from app.core.config import settings
from app.core.exceptions import AIFSConnectionError, AIFSAuthenticationError
from app.aifs.proto import aifs_pb2_grpc, aifs_pb2

logger = logging.getLogger(__name__)


class AIFSClient:
    """Client for communicating with AIFS server via gRPC."""
    
    def __init__(self, host: str = None, port: int = None, use_tls: bool = None):
        self.host = host or settings.AIFS_SERVER_HOST
        self.port = port or settings.AIFS_SERVER_PORT
        self.use_tls = use_tls if use_tls is not None else settings.AIFS_SERVER_USE_TLS
        self.api_key = settings.AIFS_API_KEY
        self.channel = None
        self.stub = None
        
    async def connect(self):
        """Connect to AIFS server."""
        try:
            # Create gRPC channel
            if self.use_tls:
                credentials = grpc.ssl_channel_credentials()
                self.channel = aio.secure_channel(f"{self.host}:{self.port}", credentials)
            else:
                self.channel = aio.insecure_channel(f"{self.host}:{self.port}")
            
            # Create AIFS gRPC stub
            self.stub = aifs_pb2_grpc.AIFSStub(self.channel)
            logger.info(f"Connected to AIFS server at {self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"Failed to connect to AIFS server: {e}")
            raise AIFSConnectionError(f"Failed to connect to AIFS server: {e}")
    
    async def disconnect(self):
        """Disconnect from AIFS server."""
        if self.channel:
            await self.channel.close()
            logger.info("Disconnected from AIFS server")
    
    async def ping(self) -> bool:
        """Ping AIFS server to check connectivity."""
        try:
            if not self.stub:
                return False
            
            # Use Health service to check connectivity
            health_stub = aifs_pb2_grpc.HealthStub(self.channel)
            request = aifs_pb2.HealthCheckRequest()
            response = await health_stub.Check(request)
            return response.healthy
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            return False
    
    async def put_asset(
        self,
        data: bytes,
        kind: str = "blob",
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        parents: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Store an asset in AIFS."""
        try:
            if not self.stub:
                raise AIFSConnectionError("AIFS client not connected")
            
            # Convert kind string to enum
            kind_enum = aifs_pb2.AssetKind.BLOB
            if kind == "tensor":
                kind_enum = aifs_pb2.AssetKind.TENSOR
            elif kind == "embed":
                kind_enum = aifs_pb2.AssetKind.EMBED
            elif kind == "artifact":
                kind_enum = aifs_pb2.AssetKind.ARTIFACT
            
            # Convert metadata
            metadata_dict = {}
            if metadata:
                metadata_dict = {str(k): str(v) for k, v in metadata.items()}
            
            # Convert parents
            parent_edges = []
            if parents:
                for parent in parents:
                    edge = aifs_pb2.ParentEdge(
                        parent_asset_id=parent.get("asset_id", ""),
                        transform_name=parent.get("transform_name", ""),
                        transform_digest=parent.get("transform_digest", "")
                    )
                    parent_edges.append(edge)
            
            # Convert embedding to bytes if provided
            embedding_bytes = b""
            if embedding:
                import struct
                embedding_bytes = struct.pack(f"{len(embedding)}f", *embedding)
            
            # Create request
            request = aifs_pb2.PutAssetRequest(
                kind=kind_enum,
                metadata=metadata_dict,
                parents=parent_edges,
                embedding=embedding_bytes,
                chunks=[aifs_pb2.Chunk(data=data)]
            )
            
            # Stream the request (even though we only have one chunk)
            async def request_generator():
                yield request
            
            response = await self.stub.PutAsset(request_generator())
            logger.info(f"Stored asset {response.asset_id} in AIFS")
            return response.asset_id
            
        except Exception as e:
            logger.error(f"Failed to store asset: {e}")
            raise
    
    async def get_asset(self, asset_id: str, include_data: bool = True) -> Dict[str, Any]:
        """Retrieve an asset from AIFS."""
        try:
            if not self.stub:
                raise AIFSConnectionError("AIFS client not connected")
            
            request = aifs_pb2.GetAssetRequest(
                asset_id=asset_id,
                include_data=include_data
            )
            
            response = await self.stub.GetAsset(request)
            
            # Convert response to dictionary
            result = {
                "id": response.metadata.asset_id,
                "kind": aifs_pb2.AssetKind.Name(response.metadata.kind).lower(),
                "size": response.metadata.size,
                "created_at": response.metadata.created_at,
                "metadata": dict(response.metadata.metadata),
                "parents": [
                    {
                        "asset_id": parent.parent_asset_id,
                        "transform_name": parent.transform_name,
                        "transform_digest": parent.transform_digest
                    }
                    for parent in response.parents
                ],
                "children": list(response.children)
            }
            
            if include_data:
                result["data"] = response.data
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to retrieve asset {asset_id}: {e}")
            raise
    
    async def vector_search(
        self,
        query_embedding: List[float],
        k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Perform vector search in AIFS."""
        try:
            if not self.stub:
                raise AIFSConnectionError("AIFS client not connected")
            
            # Convert embedding to bytes
            import struct
            embedding_bytes = struct.pack(f"{len(query_embedding)}f", *query_embedding)
            
            # Convert filter metadata
            filter_dict = {}
            if filter_metadata:
                filter_dict = {str(k): str(v) for k, v in filter_metadata.items()}
            
            request = aifs_pb2.VectorSearchRequest(
                query_embedding=embedding_bytes,
                k=k,
                filter=filter_dict
            )
            
            response = await self.stub.VectorSearch(request)
            
            # Convert response to list of dictionaries
            results = []
            for result in response.results:
                results.append({
                    "asset_id": result.asset_id,
                    "score": result.score,
                    "metadata": dict(result.metadata.metadata)
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            raise
    
    async def create_snapshot(
        self,
        namespace: str,
        asset_ids: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a snapshot of assets."""
        try:
            if not self.stub:
                raise AIFSConnectionError("AIFS client not connected")
            
            # Convert metadata
            metadata_dict = {}
            if metadata:
                metadata_dict = {str(k): str(v) for k, v in metadata.items()}
            
            request = aifs_pb2.CreateSnapshotRequest(
                namespace=namespace,
                asset_ids=asset_ids,
                metadata=metadata_dict
            )
            
            response = await self.stub.CreateSnapshot(request)
            logger.info(f"Created snapshot {response.snapshot_id}")
            return response.snapshot_id
            
        except Exception as e:
            logger.error(f"Failed to create snapshot: {e}")
            raise
    
    async def list_assets(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List assets from AIFS."""
        try:
            if not self.stub:
                raise AIFSConnectionError("AIFS client not connected")
            
            request = aifs_pb2.ListAssetsRequest(
                limit=limit,
                offset=offset
            )
            
            response = await self.stub.ListAssets(request)
            
            # Convert response to list of dictionaries
            assets = []
            for asset in response.assets:
                assets.append({
                    "id": asset.asset_id,
                    "kind": aifs_pb2.AssetKind.Name(asset.kind).lower(),
                    "size": asset.size,
                    "created_at": asset.created_at,
                    "metadata": dict(asset.metadata)
                })
            
            return assets
            
        except Exception as e:
            logger.error(f"Failed to list assets: {e}")
            raise


class AIFSClientManager:
    """Manager for AIFS client connections."""
    
    def __init__(self):
        self.client: Optional[AIFSClient] = None
        self._connected = False
    
    async def initialize(self):
        """Initialize AIFS client connection."""
        try:
            self.client = AIFSClient()
            await self.client.connect()
            
            # Test connection
            if await self.client.ping():
                self._connected = True
                logger.info("AIFS client initialized successfully")
            else:
                raise AIFSConnectionError("Failed to ping AIFS server")
                
        except Exception as e:
            logger.error(f"Failed to initialize AIFS client: {e}")
            self._connected = False
            # Don't raise exception to allow development without AIFS server
    
    async def close(self):
        """Close AIFS client connection."""
        if self.client:
            await self.client.disconnect()
            self._connected = False
            logger.info("AIFS client closed")
    
    @property
    def is_connected(self) -> bool:
        """Check if AIFS client is connected."""
        return self._connected
    
    def get_client(self) -> AIFSClient:
        """Get AIFS client instance."""
        if not self._connected or not self.client:
            raise AIFSConnectionError("AIFS client not connected")
        return self.client
