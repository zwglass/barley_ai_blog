import { spawn } from 'child_process'
import type { NextRequest } from 'next/server'
import { NextResponse } from 'next/server'
import { promises as fs } from 'fs'
import { randomUUID } from 'crypto'
import { tmpdir } from 'os'
import { basename, resolve, join } from 'path'

export const runtime = 'nodejs'

const DOWNLOAD_ROOT = resolve(process.cwd(), 'public', 'downloads')

const jsonResponse = (status: number, message: string) =>
  new NextResponse(JSON.stringify({ message }), {
    status,
    headers: { 'content-type': 'application/json' },
  })

const runZip = (outputPath: string, inputPath: string) =>
  new Promise<void>((resolvePromise, rejectPromise) => {
    const zipProcess = spawn('zip', ['-j', outputPath, inputPath])
    let stderr = ''

    zipProcess.stderr.on('data', (data) => {
      stderr += data.toString()
    })

    zipProcess.on('error', (error) => {
      rejectPromise(error)
    })

    zipProcess.on('close', (code) => {
      if (code === 0) {
        resolvePromise()
      } else {
        rejectPromise(new Error(stderr || `zip command exited with code ${code}`))
      }
    })
  })

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const fileParam = searchParams.get('file')

  if (!fileParam) {
    return jsonResponse(400, 'Missing "file" query parameter')
  }

  const sanitizedPath = fileParam.replace(/^\/+/, '')
  const normalizedPath = (() => {
    if (sanitizedPath.startsWith('public/downloads/')) {
      return sanitizedPath.slice('public/downloads/'.length)
    }

    if (sanitizedPath.startsWith('downloads/')) {
      return sanitizedPath.slice('downloads/'.length)
    }

    return sanitizedPath
  })()

  if (!normalizedPath) {
    return jsonResponse(400, 'Invalid file path')
  }

  const absoluteFilePath = resolve(DOWNLOAD_ROOT, normalizedPath)

  if (!absoluteFilePath.startsWith(DOWNLOAD_ROOT)) {
    return jsonResponse(400, 'Invalid file path')
  }

  try {
    const fileStat = await fs.stat(absoluteFilePath)
    if (!fileStat.isFile()) {
      return jsonResponse(404, 'Requested file does not exist')
    }
  } catch (error) {
    return jsonResponse(404, 'Requested file does not exist')
  }

  const tempZipPath = join(tmpdir(), `download-${randomUUID()}.zip`)

  try {
    await runZip(tempZipPath, absoluteFilePath)
    const zipBuffer = await fs.readFile(tempZipPath)
    await fs.unlink(tempZipPath)

    const downloadName = `${basename(absoluteFilePath)}.zip`

    return new NextResponse(zipBuffer, {
      status: 200,
      headers: {
        'content-type': 'application/zip',
        'content-disposition': `attachment; filename="${downloadName}"`,
        'content-length': String(zipBuffer.length),
      },
    })
  } catch (error) {
    try {
      await fs.unlink(tempZipPath)
    } catch (cleanupError) {
      // Ignore cleanup error
    }

    const message =
      error instanceof Error ? error.message : 'An unexpected error occurred generating archive'

    return jsonResponse(500, message)
  }
}
