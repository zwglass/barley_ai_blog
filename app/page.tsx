import { sortPosts } from 'pliny/utils/contentlayer'
import { allBlogs } from 'contentlayer/generated'
import Main from './Main'
import { buildTranslatedSummaries } from '@/lib/posts'

export default async function Page() {
  const sortedPosts = sortPosts(allBlogs)
  const posts = buildTranslatedSummaries(sortedPosts)
  return <Main posts={posts} />
}
