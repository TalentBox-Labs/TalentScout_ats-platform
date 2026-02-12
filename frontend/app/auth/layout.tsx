export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-blue-50 to-white dark:from-gray-900 dark:to-gray-950">
      <div className="w-full max-w-md rounded-xl border bg-card p-8 shadow-lg">
        {children}
      </div>
    </div>
  )
}

