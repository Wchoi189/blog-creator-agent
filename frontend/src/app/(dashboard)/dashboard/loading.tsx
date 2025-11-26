export default function Loading() {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="flex flex-col items-center space-y-4">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <p className="text-sm text-gray-600">Loading dashboard...</p>
      </div>
    </div>
  )
}
