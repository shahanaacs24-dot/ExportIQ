interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  message?: string;
}

const sizeMap = { sm: 'h-4 w-4', md: 'h-8 w-8', lg: 'h-12 w-12' };

export default function Spinner({ size = 'md', className = '', message }: SpinnerProps) {
  return (
    <div className={`flex flex-col items-center justify-center ${className}`}>
      <div
        className={`animate-spin rounded-full border-2 border-gray-200 border-t-brand-600 ${sizeMap[size]}`}
        role="status"
        aria-label="Loading"
      />
      {message && <p className="mt-2 text-sm text-gray-500">{message}</p>}
    </div>
  );
}
