import type { Blog } from 'contentlayer/generated'
import { coreContent } from 'pliny/utils/contentlayer'
import type { CoreContent } from 'pliny/utils/contentlayer'
import type { LanguageCode } from '@/lib/language'
import { DEFAULT_LANGUAGE } from '@/lib/language'

export interface PostSummary {
  translationKey: string
  language: LanguageCode
  path: string
  slug: string
  date: string
  title: string
  summary?: string
  tags?: string[]
}

export interface TranslatedPostSummaries {
  translationKey: string
  summaries: Partial<Record<LanguageCode, PostSummary>>
}

export const buildTranslatedSummaries = (blogs: Blog[]): TranslatedPostSummaries[] => {
  const grouped = new Map<string, TranslatedPostSummaries>()

  blogs.forEach((blog) => {
    const key = blog.translationKey || blog.slug
    if (!grouped.has(key)) {
      grouped.set(key, { translationKey: key, summaries: {} })
    }
    const summary = coreContent(blog)
    grouped.get(key)!.summaries[blog.language as LanguageCode] = {
      translationKey: key,
      language: blog.language as LanguageCode,
      path: summary.path,
      slug: summary.slug,
      date: summary.date,
      title: summary.title,
      summary: summary.summary,
      tags: summary.tags,
    }
  })

  return Array.from(grouped.values()).sort((a, b) => {
    const aDate = a.summaries[DEFAULT_LANGUAGE]?.date || Object.values(a.summaries)[0]?.date
    const bDate = b.summaries[DEFAULT_LANGUAGE]?.date || Object.values(b.summaries)[0]?.date
    return new Date(bDate || 0).getTime() - new Date(aDate || 0).getTime()
  })
}

export type TranslationSummaries = Partial<Record<LanguageCode, CoreContent<Blog>>>

export interface TranslatedPostDetail {
  translationKey: string
  posts: Partial<Record<LanguageCode, Blog>>
  summaries: TranslationSummaries
}

export const buildTranslatedDetails = (blogs: Blog[]): TranslatedPostDetail => {
  if (blogs.length === 0) {
    return { translationKey: '', posts: {}, summaries: {} }
  }
  const key = blogs[0].translationKey || blogs[0].slug
  const record: TranslatedPostDetail = { translationKey: key, posts: {}, summaries: {} }
  blogs.forEach((blog) => {
    const language = blog.language as LanguageCode
    const summary = coreContent(blog)
    record.posts[language] = blog
    record.summaries[language] = summary
  })
  return record
}

export const pickSummaryForLanguage = (
  entry: TranslatedPostSummaries,
  language: LanguageCode
): PostSummary | undefined => {
  return (
    entry.summaries[language] ||
    entry.summaries[DEFAULT_LANGUAGE] ||
    Object.values(entry.summaries)[0]
  )
}
