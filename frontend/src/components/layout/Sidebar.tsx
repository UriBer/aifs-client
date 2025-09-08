'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  FolderIcon, 
  MagnifyingGlassIcon, 
  ShareIcon, 
  ChatBubbleLeftRightIcon,
  Cog6ToothIcon,
  CloudIcon,
  CloudArrowUpIcon
} from '@heroicons/react/24/outline'
import { clsx } from 'clsx'

const navigation = [
  { name: 'Assets', icon: FolderIcon, href: '/' },
  { name: 'Search', icon: MagnifyingGlassIcon, href: '/search' },
  { name: 'Upload', icon: CloudArrowUpIcon, href: '/upload' },
  { name: 'RAG Chat', icon: ChatBubbleLeftRightIcon, href: '/rag-chat' },
  { name: 'Lineage', icon: ShareIcon, href: '/lineage' },
  { name: 'Cloud', icon: CloudIcon, href: '/cloud' },
  { name: 'Settings', icon: Cog6ToothIcon, href: '/settings' },
]

export function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const pathname = usePathname()

  return (
    <div className={clsx(
      'bg-white border-r border-gray-200 transition-all duration-300',
      isCollapsed ? 'w-16' : 'w-64'
    )}>
      <div className="flex flex-col h-full">
        {/* Toggle Button */}
        <div className="p-4 border-b border-gray-200">
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="w-full flex items-center justify-center p-2 text-gray-400 hover:text-gray-600"
          >
            <div className="w-6 h-6 bg-gray-200 rounded"></div>
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-4 space-y-2">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                className={clsx(
                  'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                  isActive
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                )}
              >
                <item.icon
                  className={clsx(
                    'flex-shrink-0 w-5 h-5',
                    isActive ? 'text-primary-500' : 'text-gray-400 group-hover:text-gray-500'
                  )}
                />
                {!isCollapsed && (
                  <span className="ml-3">{item.name}</span>
                )}
              </Link>
            )
          })}
        </nav>

        {/* Footer */}
        {!isCollapsed && (
          <div className="p-4 border-t border-gray-200">
            <div className="text-xs text-gray-500">
              <div>Version 1.0.0</div>
              <div className="mt-1">AIFS Client</div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
