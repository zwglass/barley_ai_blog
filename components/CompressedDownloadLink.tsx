'use client'

import { useState, type MouseEvent } from 'react'
import JSZip from 'jszip'
import { saveAs } from 'file-saver'

type CompressedDownloadLinkProps = {
  /** 要打包的文件路径数组（可以是相对路径或完整 URL） */
  files: string[]
  /** 下载时生成的 zip 文件名 */
  fileName?: string
  /** 样式类名 */
  className?: string
  /** 按钮显示文字 */
  children: React.ReactNode
}

const buildDownloadName = (fileName?: string) => {
  if (!fileName || fileName.trim().length === 0) return 'download.zip'
  return fileName.endsWith('.zip') ? fileName : `${fileName}.zip`
}

const CompressedDownloadLink = ({
  files,
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
      const zip = new JSZip()

      for (const fileUrl of files) {
        const response = await fetch(fileUrl)
        if (!response.ok) throw new Error(`无法获取文件: ${fileUrl}`)
        const blob = await response.blob()
        const name = fileUrl.split('/').pop() || 'file'
        zip.file(name, blob)
      }

      const content = await zip.generateAsync({ type: 'blob' })
      const label = buildDownloadName(fileName)
      saveAs(content, label)
    } catch (err) {
      const msg = err instanceof Error ? err.message : '压缩下载失败，请检查文件路径是否正确。'
      setError(msg)
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
        {isLoading ? '正在打包…' : children}
      </button>
      {error && <span className="mt-1 text-sm text-red-600">{error}</span>}
    </div>
  )
}

export default CompressedDownloadLink
