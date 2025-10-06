'use client'

import { ReactNode } from 'react'
import { LanguageProvider } from './LanguageProvider'

const LanguageClient = ({ children }: { children: ReactNode }) => {
  return <LanguageProvider>{children}</LanguageProvider>
}

export default LanguageClient
