'use client'
import './globals.css'

import { GeistProvider, CssBaseline } from '@geist-ui/core'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
        <head title={"121 Search"}>
            <style>
                {/*{`*/}
                {/*  thead {*/}
                {/*    display: none;*/}
                {/*  }*/}
                {/*`}*/}
            </style>
        </head>
      <body>
        <GeistProvider themeType={"dark"}>
          <CssBaseline />
          {children}
        </GeistProvider>
      </body>
    </html>
  )
}
