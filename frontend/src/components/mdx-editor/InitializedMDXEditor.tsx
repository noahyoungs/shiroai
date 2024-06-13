'use client'
// InitializedMDXEditor.tsx
import type { ForwardedRef } from 'react'
import {
  headingsPlugin,
  listsPlugin,
  quotePlugin,
  thematicBreakPlugin,
  markdownShortcutPlugin,
  MDXEditor,
  toolbarPlugin,
  jsxPlugin,
  type MDXEditorMethods,
  type MDXEditorProps,
  JsxComponentDescriptor,
  GenericJsxEditor,
  tablePlugin
} from '@mdxeditor/editor'
import { Button } from '@nextui-org/react'
import { Icon } from '@iconify/react'

// Define the additional props that InitializedMDXEditor accepts
interface InitializedMDXEditorProps extends MDXEditorProps {
  editorRef: ForwardedRef<MDXEditorMethods> | null;
  toolbarContents: React.ReactNode;
}

const jsxComponentDescriptors: JsxComponentDescriptor[] = [
  {
    name: 'Footnote',
    kind: 'text',
    props: [
      { name: 'foo', type: 'string' } // Textual property type
    ],
    hasChildren: true,
    Editor: GenericJsxEditor
  }
]


// Update the type definition of InitializedMDXEditor to include the additional props
export default function InitializedMDXEditor({
  editorRef,
  toolbarContents,
  ...props
}: InitializedMDXEditorProps) {
  return (
    <MDXEditor
      plugins={[
        // Example Plugin Usage
        headingsPlugin(),
        listsPlugin(),
        quotePlugin(),
        thematicBreakPlugin(),
        markdownShortcutPlugin(),
        tablePlugin(),
        toolbarPlugin({
          toolbarContents: () => toolbarContents
        }),
        jsxPlugin({ jsxComponentDescriptors }),
      ]}
      {...props}
      ref={editorRef}
    />
  )
}

