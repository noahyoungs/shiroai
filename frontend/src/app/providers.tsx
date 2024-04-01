// app/providers.tsx
'use client'

import { NextUIProvider } from '@nextui-org/react'
import { ThemeProvider } from 'next-themes';
import { useRouter } from 'next/navigation'

type Props = {
  children?: React.ReactNode;
};

export function Providers({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  return (
    <ThemeProvider attribute="class" enableSystem={true}>
      <NextUIProvider navigate={router.push}>
        {children}
      </NextUIProvider>
    </ThemeProvider>
  )
}