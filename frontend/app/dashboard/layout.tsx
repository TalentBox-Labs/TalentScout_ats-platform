import Link from 'next/link'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="flex h-screen">
        <aside className="w-64 border-r bg-card">
          <div className="flex h-16 items-center border-b px-6 text-lg font-semibold">
            ATS Dashboard
          </div>
          <nav className="flex flex-col gap-1 p-4 text-sm">
            <Link
              href="/dashboard"
              className="rounded-md px-3 py-2 text-left hover:bg-accent hover:text-accent-foreground"
            >
              Overview
            </Link>
            <Link
              href="/dashboard/jobs"
              className="rounded-md px-3 py-2 text-left hover:bg-accent hover:text-accent-foreground"
            >
              Jobs
            </Link>
            <Link
              href="/dashboard/candidates"
              className="rounded-md px-3 py-2 text-left hover:bg-accent hover:text-accent-foreground"
            >
              Candidates
            </Link>
          </nav>
        </aside>
        <main className="flex-1 overflow-y-auto bg-muted/40 p-6">
          <div className="mx-auto max-w-6xl">{children}</div>
        </main>
      </div>
    </div>
  )
}

