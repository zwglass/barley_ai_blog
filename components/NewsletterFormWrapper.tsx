'use client'

import { useEffect, useState } from 'react'
import NewsletterForm from 'pliny/ui/NewsletterForm'

interface NewsletterFormWrapperProps {
  title?: string
  apiUrl?: string
}

const NewsletterFormWrapper = (props: NewsletterFormWrapperProps) => {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return null
  }

  return <NewsletterForm {...props} />
}

export default NewsletterFormWrapper
