# How can I serve downloads as ZIP archives?

The project includes a `CompressedDownloadLink` component that automatically compresses files into a `.zip` archive before serving them.

## 1. Place the source file

- Put the original file under `public/downloads`. Sub-folders are allowed (e.g. `public/downloads/guides/whitepaper.pdf`).

## 2. Use the component in MDX

```mdx
<CompressedDownloadLink file="guides/whitepaper.pdf">
  下载白皮书
</CompressedDownloadLink>
```

- `file`: path of the original file relative to `public/downloads`.
- `fileName` (optional): override the resulting archive name.

`CompressedDownloadLink` is registered in `components/MDXComponents.tsx`, so you can reference it directly without adding an `import` line in the MDX file. When the link is clicked, the browser calls `/api/compress-download`. The API compresses the requested file with the server's `zip` utility and streams the archive back to the user.

> [!NOTE]
> The API relies on the `zip` command being available in the server runtime. Most Linux and macOS environments include it by default.
