import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'CollegeHelper',
  description: 'Aplicativo que ajuda você à criar sua grade horária alimentado por IA',
  generator: 'v0.dev',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
