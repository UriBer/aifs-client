'use client'

import { useState } from 'react'
import { 
  Squares2X2Icon, 
  ListBulletIcon, 
  PlusIcon,
  FunnelIcon,
  ArrowUpTrayIcon
} from '@heroicons/react/24/outline'
import { AssetGrid } from './AssetGrid'
import { AssetList } from './AssetList'
import { UploadModal } from './UploadModal'
import { FilterPanel } from './FilterPanel'

type ViewMode = 'grid' | 'list'

export function AssetBrowser() {
  const [viewMode, setViewMode] = useState<ViewMode>('grid')
  const [isUploadOpen, setIsUploadOpen] = useState(false)
  const [isFilterOpen, setIsFilterOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  return (
    <div className="h-full flex flex-col">
      {/* Toolbar */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h2 className="text-lg font-semibold text-gray-900">Assets</h2>
            <span className="text-sm text-gray-500">47 items</span>
          </div>
          
          <div className="flex items-center space-x-2">
            {/* View Mode Toggle */}
            <div className="flex items-center border border-gray-300 rounded-lg">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 ${viewMode === 'grid' ? 'bg-primary-100 text-primary-700' : 'text-gray-500 hover:text-gray-700'}`}
              >
                <Squares2X2Icon className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 ${viewMode === 'list' ? 'bg-primary-100 text-primary-700' : 'text-gray-500 hover:text-gray-700'}`}
              >
                <ListBulletIcon className="w-5 h-5" />
              </button>
            </div>

            {/* Filter Button */}
            <button
              onClick={() => setIsFilterOpen(!isFilterOpen)}
              className="btn btn-outline btn-sm"
            >
              <FunnelIcon className="w-4 h-4 mr-2" />
              Filter
            </button>

            {/* Upload Button */}
            <button
              onClick={() => setIsUploadOpen(true)}
              className="btn btn-primary btn-sm"
            >
              <ArrowUpTrayIcon className="w-4 h-4 mr-2" />
              Upload
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Filter Panel */}
        {isFilterOpen && (
          <div className="w-80 bg-white border-r border-gray-200">
            <FilterPanel onClose={() => setIsFilterOpen(false)} />
          </div>
        )}

        {/* Asset Display */}
        <div className="flex-1 overflow-auto">
          {viewMode === 'grid' ? (
            <AssetGrid searchQuery={searchQuery} />
          ) : (
            <AssetList searchQuery={searchQuery} />
          )}
        </div>
      </div>

      {/* Upload Modal */}
      <UploadModal 
        isOpen={isUploadOpen} 
        onClose={() => setIsUploadOpen(false)} 
      />
    </div>
  )
}
