/**
 * PolicyPilot brand logo mark — a clean 8-pointed star SVG.
 * Use `size` to control dimensions, `color` to set fill (default: #FF5500).
 */
export default function LogoMark({ size = 28, color = '#FF5500' }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      {/* 8-pointed star / compass-rose shape */}
      <path
        d="M16 2 L18.5 13.5 L30 16 L18.5 18.5 L16 30 L13.5 18.5 L2 16 L13.5 13.5 Z"
        fill={color}
      />
      <path
        d="M16 7 L17.6 13.5 L24 16 L17.6 18.5 L16 25 L14.4 18.5 L8 16 L14.4 13.5 Z"
        fill="white"
        opacity="0.35"
      />
    </svg>
  );
}
