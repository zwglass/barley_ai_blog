import { Inter } from 'next/font/google'
import SectionContainer from './SectionContainer'
import Footer from './Footer'
import { ReactNode } from 'react'
import Header from './Header'
import { LanguageProvider } from './LanguageProvider'

interface Props {
  children: ReactNode
}

const inter = Inter({
  subsets: ['latin'],
})

const LayoutWrapper = ({ children }: Props) => {
  return (
    <SectionContainer>
      <LanguageProvider>
        <div className={`${inter.className} flex h-screen flex-col justify-between font-sans`}>
          <Header />
          <main className="mb-auto">{children}</main>
          <Footer />
        </div>
      </LanguageProvider>
    </SectionContainer>
  )
}

export default LayoutWrapper
