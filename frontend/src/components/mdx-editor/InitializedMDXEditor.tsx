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
  UndoRedo,
  BoldItalicUnderlineToggles,
  ButtonWithTooltip,
  type MDXEditorMethods,
  type MDXEditorProps
} from '@mdxeditor/editor'
import { Button } from '@nextui-org/react'
import { Icon } from '@iconify/react'

// Only import this to the next file
export default function InitializedMDXEditor({
  editorRef,
  saveSlideMarkdown,
  ...props
}: { editorRef: ForwardedRef<MDXEditorMethods> | null } & MDXEditorProps) {
  return (
    <MDXEditor
      plugins={[
        // Example Plugin Usage
        headingsPlugin(),
        listsPlugin(),
        quotePlugin(),
        thematicBreakPlugin(),
        markdownShortcutPlugin(),
        toolbarPlugin({
          toolbarContents: () => (
            <>
              {' '}
              <UndoRedo />
              <BoldItalicUnderlineToggles />
              <ButtonWithTooltip
                onClick={saveSlideMarkdown}
                title="Save"
                >
                  <Icon icon="tabler:circle-check" width="23" height="23" />
                </ButtonWithTooltip>
            </>
          )
        })
      ]}
      {...props}
      ref={editorRef}
    />
  )
}

