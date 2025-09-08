'use client'

import { useState, useCallback } from 'react'
import { Dialog } from '@headlessui/react'
import { XMarkIcon, CloudArrowUpIcon } from '@heroicons/react/24/outline'
import { useDropzone } from 'react-dropzone'
import { toast } from 'react-hot-toast'

interface UploadModalProps {
  isOpen: boolean
  onClose: () => void
}

export function UploadModal({ isOpen, onClose }: UploadModalProps) {
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setUploading(true)
    setUploadProgress(0)

    try {
      for (let i = 0; i < acceptedFiles.length; i++) {
        const file = acceptedFiles[i]
        
        const formData = new FormData()
        formData.append('file', file)
        
        // Use XMLHttpRequest for real progress tracking
        await new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest()
          
          // Track upload progress
          xhr.upload.addEventListener('progress', (event) => {
            if (event.lengthComputable) {
              const fileProgress = (event.loaded / event.total) * 100
              const totalProgress = ((i + fileProgress / 100) / acceptedFiles.length) * 100
              setUploadProgress(totalProgress)
            }
          })
          
          xhr.addEventListener('load', () => {
            if (xhr.status >= 200 && xhr.status < 300) {
              const result = JSON.parse(xhr.responseText)
              console.log('Uploaded file:', result)
              resolve(result)
            } else {
              reject(new Error(`Upload failed for ${file.name}: ${xhr.status}`))
            }
          })
          
          xhr.addEventListener('error', () => {
            reject(new Error(`Upload failed for ${file.name}`))
          })
          
          xhr.open('POST', '/api/v1/assets/upload')
          xhr.send(formData)
        })
      }
      
      toast.success(`Successfully uploaded ${acceptedFiles.length} file(s)`)
      
      // Close modal after a short delay
      setTimeout(() => {
        onClose()
      }, 1000)
    } catch (error) {
      toast.error('Upload failed')
      console.error('Upload error:', error)
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }, [onClose])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'text/csv': ['.csv'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/gif': ['.gif'],
      'video/mp4': ['.mp4'],
      'audio/mpeg': ['.mp3'],
      'application/json': ['.json'],
      'text/markdown': ['.md'],
      'text/x-python': ['.py']
    },
    maxSize: 100 * 1024 * 1024, // 100MB
    multiple: true
  })

  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
      
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="mx-auto max-w-md w-full bg-white rounded-lg shadow-xl">
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <Dialog.Title className="text-lg font-semibold text-gray-900">
                Upload Files
              </Dialog.Title>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="w-6 h-6" />
              </button>
            </div>

            {uploading ? (
              <div className="space-y-4">
                <div className="text-center">
                  <CloudArrowUpIcon className="w-12 h-12 text-primary-500 mx-auto mb-4 animate-pulse" />
                  <p className="text-sm text-gray-600">Uploading files...</p>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
                <p className="text-sm text-gray-500 text-center">{uploadProgress}%</p>
              </div>
            ) : (
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  isDragActive
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <input {...getInputProps()} />
                <CloudArrowUpIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-sm text-gray-600 mb-2">
                  {isDragActive
                    ? 'Drop files here...'
                    : 'Drag & drop files here, or click to select'}
                </p>
                <p className="text-xs text-gray-500">
                  Supports PDF, DOC, TXT, CSV, images, videos, and more
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Max file size: 100MB
                </p>
              </div>
            )}
          </div>
        </Dialog.Panel>
      </div>
    </Dialog>
  )
}
