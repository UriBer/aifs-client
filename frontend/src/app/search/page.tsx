'use client'

import { useState } from 'react'
import { MainLayout } from '@/components/layout/MainLayout'
import { SearchBar } from '@/components/search/SearchBar'

export default function SearchPage() {
  const [searchResults, setSearchResults] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  const handleSearch = async (query: string) => {
    setIsLoading(true)
    try {
      const response = await fetch(`/api/v1/search?q=${encodeURIComponent(query)}`)
      if (response.ok) {
        const results = await response.json()
        setSearchResults(results)
      }
    } catch (error) {
      console.error('Search error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <MainLayout>
      <div className="p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Search Assets</h1>
          <SearchBar onSearch={handleSearch} />
        </div>

        {isLoading && (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        )}

        {searchResults.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">Search Results</h2>
            <div className="grid gap-4">
              {searchResults.map((result: any) => (
                <div key={result.id} className="card p-4">
                  <h3 className="font-medium text-gray-900">{result.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{result.type}</p>
                  {result.snippet && (
                    <p className="text-sm text-gray-700 mt-2">{result.snippet}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {!isLoading && searchResults.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            Enter a search query to find assets
          </div>
        )}
      </div>
    </MainLayout>
  )
}
