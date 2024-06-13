// ForwardRefEditor.tsx
'use client'

import { MDXEditorMethods, MDXEditorProps } from '@mdxeditor/editor'
import dynamic from 'next/dynamic'
import { forwardRef } from 'react'

// This is the only place InitializedMDXEditor is imported directly.
const Editor = dynamic(() => import('./InitializedMDXEditor'), {
  // Make sure we turn SSR off
  ssr: false
})

// Define the additional props that ForwardRefEditor accepts
interface ForwardRefEditorProps extends MDXEditorProps {
  toolbarContents: React.ReactNode;
}

// Update the type definition of ForwardRefEditor to include the additional props
export const ForwardRefEditor = forwardRef<MDXEditorMethods, ForwardRefEditorProps>(
  ({ toolbarContents, ...props }, ref) => (
    <Editor {...props} editorRef={ref} toolbarContents={toolbarContents} />
  )
)

// TS complains without the following line
ForwardRefEditor.displayName = 'ForwardRefEditor'