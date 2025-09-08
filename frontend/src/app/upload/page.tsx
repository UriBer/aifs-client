'use client'

import { useState } from 'react'
import { MainLayout } from '@/components/layout/MainLayout'
import { UploadModal } from '@/components/assets/UploadModal'

export default function UploadPage() {
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false)

  return (
    <MainLayout>
      <div className="p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Upload Assets</h1>
          <p className="text-gray-600 mb-6">
            Upload files to your AIFS storage and make them searchable with AI.
          </p>
        </div>

        <div className="max-w-2xl">
          <div className="card p-8 text-center">
            <div className="mb-4">
              <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Upload Files</h3>
            <p className="text-gray-600 mb-4">
              Drag and drop files here, or click to select files
            </p>
            <button
              onClick={() => setIsUploadModalOpen(true)}
              className="btn btn-primary"
            >
              Choose Files
            </button>
          </div>
        </div>

        <UploadModal
          isOpen={isUploadModalOpen}
          onClose={() => setIsUploadModalOpen(false)}
        />
      </div>
    </MainLayout>
  )
}
