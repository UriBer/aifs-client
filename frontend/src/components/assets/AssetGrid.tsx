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

// Mock data
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

interface AssetGridProps {
  searchQuery: string
}

export function AssetGrid({ searchQuery }: AssetGridProps) {
  const [selectedAssets, setSelectedAssets] = useState<string[]>([])

  const getFileIcon = (mimeType: string, type: string) => {
    if (type === 'folder') {
      return <FolderIcon className="w-8 h-8 text-blue-500" />
    }
    
    if (mimeType.startsWith('image/')) {
      return <PhotoIcon className="w-8 h-8 text-green-500" />
    }
    
    if (mimeType.startsWith('video/')) {
      return <VideoCameraIcon className="w-8 h-8 text-purple-500" />
    }
    
    if (mimeType.startsWith('audio/')) {
      return <MusicalNoteIcon className="w-8 h-8 text-pink-500" />
    }
    
    return <DocumentIcon className="w-8 h-8 text-gray-500" />
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
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
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
        {filteredAssets.map((asset) => (
          <div
            key={asset.id}
            onClick={() => handleAssetClick(asset.id)}
            className={clsx(
              'group relative p-4 border-2 rounded-lg cursor-pointer transition-all duration-200 hover:shadow-md',
              selectedAssets.includes(asset.id)
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-200 bg-white hover:border-gray-300'
            )}
          >
            {/* Selection indicator */}
            {selectedAssets.includes(asset.id) && (
              <div className="absolute top-2 left-2 w-4 h-4 bg-primary-500 rounded-full flex items-center justify-center">
                <div className="w-2 h-2 bg-white rounded-full"></div>
              </div>
            )}

            {/* More options button */}
            <button className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-100 rounded">
              <EllipsisVerticalIcon className="w-4 h-4 text-gray-500" />
            </button>

            {/* File icon */}
            <div className="flex justify-center mb-3">
              {getFileIcon(asset.mimeType, asset.type)}
            </div>

            {/* File name */}
            <div className="text-center">
              <h3 className="text-sm font-medium text-gray-900 truncate" title={asset.name}>
                {asset.name}
              </h3>
              
              {/* File size and date */}
              <div className="mt-1 text-xs text-gray-500">
                {asset.type === 'folder' ? (
                  <span>Folder</span>
                ) : (
                  <>
                    <div>{formatFileSize(asset.size)}</div>
                    <div>{formatDate(asset.createdAt)}</div>
                  </>
                )}
              </div>

              {/* Tags */}
              {asset.tags.length > 0 && (
                <div className="mt-2 flex flex-wrap justify-center gap-1">
                  {asset.tags.slice(0, 2).map((tag) => (
                    <span
                      key={tag}
                      className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                  {asset.tags.length > 2 && (
                    <span className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">
                      +{asset.tags.length - 2}
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
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
