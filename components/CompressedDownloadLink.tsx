'use client'

import { useState, type MouseEvent } from 'react'
import type { ReactNode } from 'react'

type CompressedDownloadLinkProps = {
  file: string
  fileName?: string
  className?: string
  children: ReactNode
}

const buildDownloadName = (fileName?: string, fallback?: string) => {
  if (!fileName || fileName.trim().length === 0) {
    const candidate = fallback ?? 'download'
    return candidate.endsWith('.zip') ? candidate : `${candidate}.zip`
  }

  return fileName.endsWith('.zip') ? fileName : `${fileName}.zip`
}

const CompressedDownloadLink = ({
  file,
  fileName,
  className,
  children,
}: CompressedDownloadLinkProps) => {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleClick = async (event: MouseEvent<HTMLButtonElement>) => {
    event.preventDefault()
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(`/api/compress-download?file=${encodeURIComponent(file)}`)

      if (!response.ok) {
        let message = 'Unable to generate download archive.'
        try {
          const data = await response.json()
          if (typeof data?.message === 'string') {
            message = data.message
          }
        } catch (jsonError) {
          // Ignore JSON parse errors
        }
        throw new Error(message)
      }

      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const label = buildDownloadName(fileName, file.split('/').pop())

      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = label
      document.body.append(anchor)
      anchor.click()
      anchor.remove()
      URL.revokeObjectURL(url)
    } catch (downloadError) {
      const message =
        downloadError instanceof Error
          ? downloadError.message
          : 'Unable to complete download request.'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="inline-flex flex-col">
      <button
        type="button"
        onClick={handleClick}
        className={`text-primary-500 hover:text-primary-600 inline-flex items-center gap-2 font-semibold disabled:opacity-60 ${
          className ?? ''
        }`}
        disabled={isLoading}
      >
        {isLoading ? 'Generating download…' : children}
      </button>
      {error ? <span className="mt-1 text-sm text-red-600">{error}</span> : null}
    </div>
  )
}

export default CompressedDownloadLink
