'use client'

import { useState } from 'react'
import { 
  DocumentIcon, 
  PhotoIcon, 
  VideoCameraIcon,
  MusicalNoteIcon,
  FolderIcon,
  EllipsisVerticalIcon
} from '@heroicons/react/24/outline'
import { clsx } from 'clsx'

interface Asset {
  id: string
  name: string
  type: string
  mimeType: string
  size: number
  createdAt: string
  tags: string[]
}

// Mock data (same as AssetGrid)
const mockAssets: Asset[] = [
  {
    id: '1',
    name: 'ML_Guide.pdf',
    type: 'file',
    mimeType: 'application/pdf',
    size: 2100000,
    createdAt: '2024-01-15T10:30:00Z',
    tags: ['ml', 'guide', 'documentation']
  },
  {
    id: '2',
    name: 'training_data.csv',
    type: 'file',
    mimeType: 'text/csv',
    size: 15300000,
    createdAt: '2024-01-14T15:20:00Z',
    tags: ['data', 'training', 'csv']
  },
  {
    id: '3',
    name: 'project_notes.md',
    type: 'file',
    mimeType: 'text/markdown',
    size: 800000,
    createdAt: '2024-01-13T09:15:00Z',
    tags: ['notes', 'project', 'markdown']
  },
  {
    id: '4',
    name: 'ML Models',
    type: 'folder',
    mimeType: 'folder',
    size: 0,
    createdAt: '2024-01-12T14:45:00Z',
    tags: ['ml', 'models', 'folder']
  },
  {
    id: '5',
    name: 'chart.png',
    type: 'file',
    mimeType: 'image/png',
    size: 1500000,
    createdAt: '2024-01-11T16:30:00Z',
    tags: ['image', 'chart', 'visualization']
  },
  {
    id: '6',
    name: 'presentation.mp4',
    type: 'file',
    mimeType: 'video/mp4',
    size: 45000000,
    createdAt: '2024-01-10T11:20:00Z',
    tags: ['video', 'presentation', 'demo']
  }
]

interface AssetListProps {
  searchQuery: string
}

export function AssetList({ searchQuery }: AssetListProps) {
  const [selectedAssets, setSelectedAssets] = useState<string[]>([])

  const getFileIcon = (mimeType: string, type: string) => {
    if (type === 'folder') {
      return <FolderIcon className="w-5 h-5 text-blue-500" />
    }
    
    if (mimeType.startsWith('image/')) {
      return <PhotoIcon className="w-5 h-5 text-green-500" />
    }
    
    if (mimeType.startsWith('video/')) {
      return <VideoCameraIcon className="w-5 h-5 text-purple-500" />
    }
    
    if (mimeType.startsWith('audio/')) {
      return <MusicalNoteIcon className="w-5 h-5 text-pink-500" />
    }
    
    return <DocumentIcon className="w-5 h-5 text-gray-500" />
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '-'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const filteredAssets = mockAssets.filter(asset =>
    asset.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    asset.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  const handleAssetClick = (assetId: string) => {
    setSelectedAssets(prev => 
      prev.includes(assetId) 
        ? prev.filter(id => id !== assetId)
        : [...prev, assetId]
    )
  }

  return (
    <div className="p-6">
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        {/* Table Header */}
        <div className="bg-gray-50 px-6 py-3 border-b border-gray-200">
          <div className="grid grid-cols-12 gap-4 text-sm font-medium text-gray-500">
            <div className="col-span-1">
              <input
                type="checkbox"
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
            </div>
            <div className="col-span-5">Name</div>
            <div className="col-span-2">Type</div>
            <div className="col-span-2">Size</div>
            <div className="col-span-2">Modified</div>
          </div>
        </div>

        {/* Table Body */}
        <div className="divide-y divide-gray-200">
          {filteredAssets.map((asset) => (
            <div
              key={asset.id}
              onClick={() => handleAssetClick(asset.id)}
              className={clsx(
                'px-6 py-4 hover:bg-gray-50 cursor-pointer transition-colors',
                selectedAssets.includes(asset.id) && 'bg-primary-50'
              )}
            >
              <div className="grid grid-cols-12 gap-4 items-center">
                {/* Checkbox */}
                <div className="col-span-1">
                  <input
                    type="checkbox"
                    checked={selectedAssets.includes(asset.id)}
                    onChange={() => handleAssetClick(asset.id)}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                </div>

                {/* Name */}
                <div className="col-span-5 flex items-center space-x-3">
                  {getFileIcon(asset.mimeType, asset.type)}
                  <div>
                    <div className="text-sm font-medium text-gray-900">{asset.name}</div>
                    {asset.tags.length > 0 && (
                      <div className="flex space-x-1 mt-1">
                        {asset.tags.slice(0, 3).map((tag) => (
                          <span
                            key={tag}
                            className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full"
                          >
                            {tag}
                          </span>
                        ))}
                        {asset.tags.length > 3 && (
                          <span className="text-xs text-gray-500">+{asset.tags.length - 3}</span>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {/* Type */}
                <div className="col-span-2 text-sm text-gray-500">
                  {asset.type === 'folder' ? 'Folder' : asset.mimeType.split('/')[1].toUpperCase()}
                </div>

                {/* Size */}
                <div className="col-span-2 text-sm text-gray-500">
                  {formatFileSize(asset.size)}
                </div>

                {/* Modified */}
                <div className="col-span-2 text-sm text-gray-500">
                  {formatDate(asset.createdAt)}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {filteredAssets.length === 0 && (
        <div className="text-center py-12">
          <DocumentIcon className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No assets found</h3>
          <p className="text-gray-500">
            {searchQuery ? 'Try adjusting your search terms' : 'Upload your first asset to get started'}
          </p>
        </div>
      )}
    </div>
  )
}
