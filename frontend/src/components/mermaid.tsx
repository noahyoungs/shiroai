"use client"
import React, { useEffect } from 'react';
import mermaid from 'mermaid';
import { Inter } from 'next/font/google'
import { useTheme } from 'next-themes'
import { cn } from '@/utils/cn';

const inter = Inter({ subsets: ['latin'] })

interface MermaidProps {
  chart: string;
  className?: string;
}
const Mermaid: React.FC<MermaidProps> = ({ chart, className}) => {
  const { theme } = useTheme()
  useEffect(() => {
    mermaid.initialize({
      startOnLoad: true,
      theme: theme === 'dark' ? 'dark' : 'default',
      securityLevel: 'loose',
      fontFamily: inter.style.fontFamily,
      htmlLabels: true,
      flowchart: {
        diagramPadding: 1,
        padding: 20,
      },
    });
    mermaid.contentLoaded();
  }, [theme]);
  return <div className={cn("mermaid", className)}>{chart}</div>;
}
export default Mermaid;