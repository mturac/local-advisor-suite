"use client"

import ReactMarkdown from "react-markdown"
import { cn } from "@/lib/utils"

export function Markdown({ children, className }: { children: string; className?: string }) {
  return (
    <div className={cn("text-sm leading-relaxed space-y-3", className)}>
      <ReactMarkdown
        components={{
          h1: ({ children }) => (
            <h1 className="text-xl font-semibold tracking-tight mt-6 first:mt-0">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-lg font-semibold tracking-tight mt-6 first:mt-0 border-b border-border pb-1">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-base font-semibold mt-5 first:mt-0">{children}</h3>
          ),
          p: ({ children }) => <p className="text-muted-foreground">{children}</p>,
          ul: ({ children }) => (
            <ul className="list-disc pl-5 space-y-1 text-muted-foreground">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal pl-5 space-y-1 text-muted-foreground">{children}</ol>
          ),
          code: ({ children }) => (
            <code className="font-mono text-xs bg-muted rounded px-1.5 py-0.5">{children}</code>
          ),
          pre: ({ children }) => (
            <pre className="font-mono text-xs bg-muted rounded-lg p-3 overflow-x-auto border border-border">
              {children}
            </pre>
          ),
          a: ({ children, href }) => (
            <a href={href} className="text-emerald-600 dark:text-emerald-400 underline underline-offset-2" target="_blank" rel="noreferrer">
              {children}
            </a>
          ),
          table: ({ children }) => (
            <div className="overflow-x-auto border border-border rounded-lg">
              <table className="w-full text-xs">{children}</table>
            </div>
          ),
          th: ({ children }) => (
            <th className="border-b border-border bg-muted px-3 py-1.5 text-left font-medium">{children}</th>
          ),
          td: ({ children }) => <td className="border-b border-border/50 px-3 py-1.5">{children}</td>,
          hr: () => <hr className="border-border" />,
          blockquote: ({ children }) => (
            <blockquote className="border-l-2 border-emerald-500/50 pl-3 text-muted-foreground italic">
              {children}
            </blockquote>
          ),
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  )
}
