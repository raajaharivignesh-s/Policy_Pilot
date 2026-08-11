export default function ProcessingStepper() {
  return (
    <div className="flex items-center gap-3 px-5 py-3.5 bg-white border border-gray-200 rounded-2xl shadow-sm animate-fade-up w-fit">
      {/* Three-dot typing animation */}
      <div className="flex items-end gap-1 h-4">
        <span
          className="w-1.5 h-1.5 rounded-full bg-[#FF5500] animate-bounce"
          style={{ animationDelay: '0ms', animationDuration: '900ms' }}
        />
        <span
          className="w-1.5 h-1.5 rounded-full bg-[#FF5500] animate-bounce"
          style={{ animationDelay: '160ms', animationDuration: '900ms' }}
        />
        <span
          className="w-1.5 h-1.5 rounded-full bg-[#FF5500] animate-bounce"
          style={{ animationDelay: '320ms', animationDuration: '900ms' }}
        />
      </div>
      <span className="text-sm font-medium text-gray-700">
        Analyzing government schemes…
      </span>
    </div>
  );
}
