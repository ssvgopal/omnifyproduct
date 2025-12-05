'use client';

/**
 * Sparkline Component
 * 
 * A minimal inline chart for showing trends in cards.
 * Per FACE_Wireframes_v1: Sparklines on risk cards.
 */

interface SparklineProps {
  data: number[];
  width?: number;
  height?: number;
  color?: string;
  showDots?: boolean;
  className?: string;
}

export function Sparkline({
  data,
  width = 80,
  height = 24,
  color = '#8b5cf6',
  showDots = false,
  className = '',
}: SparklineProps) {
  if (!data || data.length < 2) {
    return null;
  }

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;

  // Calculate points for the SVG path
  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * width;
    const y = height - ((value - min) / range) * height;
    return { x, y };
  });

  // Create SVG path
  const pathD = points
    .map((point, index) => {
      if (index === 0) return `M ${point.x} ${point.y}`;
      return `L ${point.x} ${point.y}`;
    })
    .join(' ');

  // Determine trend color
  const isPositive = data[data.length - 1] >= data[0];
  const trendColor = color === 'auto' 
    ? (isPositive ? '#22c55e' : '#ef4444')
    : color;

  return (
    <svg
      width={width}
      height={height}
      className={className}
      viewBox={`0 0 ${width} ${height}`}
    >
      {/* Line */}
      <path
        d={pathD}
        fill="none"
        stroke={trendColor}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      
      {/* Area fill (optional gradient) */}
      <path
        d={`${pathD} L ${width} ${height} L 0 ${height} Z`}
        fill={trendColor}
        fillOpacity={0.1}
      />

      {/* Dots at start and end */}
      {showDots && (
        <>
          <circle
            cx={points[0].x}
            cy={points[0].y}
            r={2}
            fill={trendColor}
          />
          <circle
            cx={points[points.length - 1].x}
            cy={points[points.length - 1].y}
            r={2}
            fill={trendColor}
          />
        </>
      )}
    </svg>
  );
}

/**
 * SparklineWithLabel - Sparkline with value label
 */
interface SparklineWithLabelProps extends SparklineProps {
  label?: string;
  currentValue?: string;
  change?: number;
}

export function SparklineWithLabel({
  data,
  label,
  currentValue,
  change,
  ...sparklineProps
}: SparklineWithLabelProps) {
  const isPositive = change !== undefined ? change >= 0 : true;
  const changeColor = isPositive ? 'text-green-600' : 'text-red-600';

  return (
    <div className="flex items-center gap-2">
      <Sparkline data={data} color="auto" {...sparklineProps} />
      <div className="flex flex-col">
        {label && (
          <span className="text-xs text-gray-500">{label}</span>
        )}
        {currentValue && (
          <span className="text-sm font-medium">{currentValue}</span>
        )}
        {change !== undefined && (
          <span className={`text-xs ${changeColor}`}>
            {isPositive ? '+' : ''}{change.toFixed(1)}%
          </span>
        )}
      </div>
    </div>
  );
}
