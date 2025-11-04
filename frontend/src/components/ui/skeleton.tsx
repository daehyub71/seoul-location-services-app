import { cn } from '@/lib/utils'

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string
}

export function Skeleton({ className, ...props }: SkeletonProps) {
  return (
    <div
      className={cn('animate-pulse rounded-md bg-gray-200', className)}
      {...props}
    />
  )
}

export function MapSkeleton() {
  return (
    <div className="relative w-full h-full bg-gray-100">
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 mx-auto border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-gray-600 font-medium">지도를 불러오는 중...</p>
        </div>
      </div>
    </div>
  )
}

export function ServiceCardSkeleton() {
  return (
    <div className="flex gap-3 p-3 border border-gray-200 rounded-lg bg-white">
      {/* Thumbnail skeleton */}
      <Skeleton className="w-24 h-24 flex-shrink-0" />

      {/* Content skeleton */}
      <div className="flex-1 space-y-2">
        {/* Category badge */}
        <Skeleton className="h-5 w-20" />

        {/* Title */}
        <Skeleton className="h-6 w-full" />

        {/* Address */}
        <Skeleton className="h-4 w-3/4" />

        {/* Distance */}
        <Skeleton className="h-4 w-24" />
      </div>

      {/* Favorite button */}
      <div className="flex-shrink-0">
        <Skeleton className="h-8 w-8 rounded-full" />
      </div>
    </div>
  )
}

export function ServiceListSkeleton({ count = 5 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, index) => (
        <ServiceCardSkeleton key={index} />
      ))}
    </div>
  )
}
