'use client'

import { useState } from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'

interface FilterPanelProps {
  onClose: () => void
}

export function FilterPanel({ onClose }: FilterPanelProps) {
  const [filters, setFilters] = useState({
    fileTypes: [] as string[],
    tags: [] as string[],
    dateRange: '',
    sizeRange: ''
  })

  const hasActiveFilters = filters.fileTypes.length > 0 || filters.tags.length > 0 || filters.dateRange || filters.sizeRange;

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
          <button
            onClick={onClose}
            className="p-1 rounded-md hover:bg-gray-100"
          >
            <XMarkIcon className="h-5 w-5 text-gray-500" />
          </button>
        </div>
        {hasActiveFilters && (
          <button
            onClick={() => setFilters({ fileTypes: [], tags: [], dateRange: '', sizeRange: '' })}
            className="mt-2 text-sm text-primary-600 hover:text-primary-700"
          >
            Clear all filters
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-3">File Types</h4>
          <div className="space-y-2">
            <label className="flex items-center">
              <input
                type="checkbox"
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-700">PDF (12)</span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-700">DOC (8)</span>
            </label>
          </div>
        </div>
      </div>

      <div className="p-4 border-t border-gray-200">
        <button
          onClick={onClose}
          className="w-full btn btn-primary"
        >
          Apply Filters
        </button>
      </div>
    </div>
  )
}