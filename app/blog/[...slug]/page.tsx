import 'css/prism.css'
import 'katex/dist/katex.css'

import { components } from '@/components/MDXComponents'
import { MDXLayoutRenderer } from 'pliny/mdx-components'
import { sortPosts, coreContent } from 'pliny/utils/contentlayer'
import { allBlogs, allAuthors } from 'contentlayer/generated'
import type { Authors } from 'contentlayer/generated'
import type { ReactNode } from 'react'
import PostSimple from '@/layouts/PostSimple'
import PostLayout from '@/layouts/PostLayout'
import PostBanner from '@/layouts/PostBanner'
import { Metadata } from 'next'
import siteMetadata from '@/data/siteMetadata'
import { notFound } from 'next/navigation'
import { buildTranslatedDetails, buildTranslatedSummaries } from '@/lib/posts'
import { DEFAULT_LANGUAGE, LanguageCode } from '@/lib/language'

const defaultLayout = 'PostLayout'
const layouts = {
  PostSimple,
  PostLayout,
  PostBanner,
}

export async function generateMetadata(props: {
  params: Promise<{ slug: string[] }>
}): Promise<Metadata | undefined> {
  const params = await props.params
  const slug = decodeURI(params.slug.join('/'))
  const matchingPosts = allBlogs.filter((p) => (p.translationKey || p.slug) === slug)
  if (matchingPosts.length === 0) {
    return
  }
  const detail = buildTranslatedDetails(matchingPosts)
  const activeLanguage = (
    detail.posts[DEFAULT_LANGUAGE] ? DEFAULT_LANGUAGE : Object.keys(detail.posts)[0]
  ) as LanguageCode | undefined
  if (!activeLanguage) {
    return
  }
  const post = detail.posts[activeLanguage]
  const summary = detail.summaries[activeLanguage]
  if (!post || !summary) {
    return
  }
  const authorList = post?.authors || ['default']
  const authorDetails = authorList.map((author) => {
    const authorResults = allAuthors.find((p) => p.slug === author)
    return coreContent(authorResults as Authors)
  })

  const publishedAt = new Date(post.date).toISOString()
  const modifiedAt = new Date(post.lastmod || post.date).toISOString()
  const authors = authorDetails.map((author) => author.name)
  let imageList = [siteMetadata.socialBanner]
  if (post.images) {
    imageList = typeof post.images === 'string' ? [post.images] : post.images
  }
  const ogImages = imageList.map((img) => {
    return {
      url: img && img.includes('http') ? img : siteMetadata.siteUrl + img,
    }
  })

  return {
    title: summary.title,
    description: summary.summary,
    openGraph: {
      title: summary.title,
      description: summary.summary,
      siteName: siteMetadata.title,
      locale: 'en_US',
      type: 'article',
      publishedTime: publishedAt,
      modifiedTime: modifiedAt,
      url: './',
      images: ogImages,
      authors: authors.length > 0 ? authors : [siteMetadata.author],
    },
    twitter: {
      card: 'summary_large_image',
      title: summary.title,
      description: summary.summary,
      images: imageList,
    },
  }
}

export const generateStaticParams = async () => {
  const uniqueSlugs = Array.from(
    new Set(allBlogs.map((p) => (p.translationKey || p.slug) ?? p.slug))
  )
  return uniqueSlugs.map((slug) => ({ slug: slug.split('/').map((name) => decodeURI(name)) }))
}

export default async function Page(props: { params: Promise<{ slug: string[] }> }) {
  const params = await props.params
  const slug = decodeURI(params.slug.join('/'))
  const matchingPosts = allBlogs.filter((p) => (p.translationKey || p.slug) === slug)
  if (matchingPosts.length === 0) {
    return notFound()
  }
  const detail = buildTranslatedDetails(matchingPosts)
  const activeLanguage = (
    detail.posts[DEFAULT_LANGUAGE] ? DEFAULT_LANGUAGE : Object.keys(detail.posts)[0]
  ) as LanguageCode | undefined
  if (!activeLanguage) {
    return notFound()
  }
  const post = detail.posts[activeLanguage]
  const mainContent = detail.summaries[activeLanguage]
  if (!post || !mainContent) {
    return notFound()
  }
  const authorList = post?.authors || ['default']
  const authorDetails = authorList.map((author) => {
    const authorResults = allAuthors.find((p) => p.slug === author)
    return coreContent(authorResults as Authors)
  })
  const translatedSummaries = buildTranslatedSummaries(sortPosts(allBlogs))
  const postIndex = translatedSummaries.findIndex((entry) => entry.translationKey === slug)
  const prevEntry = postIndex !== -1 ? translatedSummaries[postIndex + 1] : undefined
  const nextEntry = postIndex !== -1 ? translatedSummaries[postIndex - 1] : undefined
  const prevSummary = prevEntry
    ? prevEntry.summaries[DEFAULT_LANGUAGE] || Object.values(prevEntry.summaries)[0]
    : undefined
  const nextSummary = nextEntry
    ? nextEntry.summaries[DEFAULT_LANGUAGE] || Object.values(nextEntry.summaries)[0]
    : undefined
  const jsonLd = post.structuredData
  jsonLd['author'] = authorDetails.map((author) => {
    return {
      '@type': 'Person',
      name: author.name,
    }
  })

  const Layout = layouts[post.layout || defaultLayout]

  const translationNodes: Partial<Record<LanguageCode, ReactNode>> = {}
  Object.entries(detail.posts).forEach(([lang, translation]) => {
    if (!translation) return
    translationNodes[lang as LanguageCode] = (
      <MDXLayoutRenderer
        code={translation.body.code}
        components={components}
        toc={translation.toc}
      />
    )
  })
  const defaultNode =
    translationNodes[DEFAULT_LANGUAGE] || Object.values(translationNodes).find(Boolean) || null

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <Layout
        content={mainContent}
        authorDetails={authorDetails}
        prev={prevSummary ? { path: prevSummary.path, title: prevSummary.title } : undefined}
        next={nextSummary ? { path: nextSummary.path, title: nextSummary.title } : undefined}
        translations={detail.summaries}
        translationNodes={translationNodes}
      >
        {defaultNode}
      </Layout>
    </>
  )
}
