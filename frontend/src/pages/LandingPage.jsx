import HeroSection from '../components/HeroSection';

export default function LandingPage({ onOpenDashboard, onDomainSelect }) {
  return (
    <div className="min-h-screen flex flex-col font-sans">
      <main className="flex-1">
        <HeroSection
          onOpenDashboard={onOpenDashboard}
          onDomainSelect={onDomainSelect}
        />
      </main>
    </div>
  );
}
