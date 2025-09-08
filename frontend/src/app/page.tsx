import { MainLayout } from '@/components/layout/MainLayout'
import { AssetBrowser } from '@/components/assets/AssetBrowser'
import { Header } from '@/components/layout/Header'
import { Sidebar } from '@/components/layout/Sidebar'

export default function HomePage() {
  return (
    <MainLayout>
      <Header />
      <div className="flex h-full">
        <Sidebar />
        <main className="flex-1 overflow-hidden">
          <AssetBrowser />
        </main>
      </div>
    </MainLayout>
  )
}
