import { useState } from 'react';
import QueryForm from './QueryForm';
import ProfilePanel from './ProfilePanel';

const INITIAL_PROFILE = {
  age: '',
  state: '',
  district: '',
  occupation: '',
  annual_income: '',
  land_acres: '',
  is_student: false,
  is_farmer: false,
};

export default function QuerySection({ queryText, setQueryText, isLoading, onSubmit }) {
  const [profile, setProfile] = useState(INITIAL_PROFILE);
  const [activeDomain, setActiveDomain] = useState(null);

  const handleSubmit = () => {
    onSubmit(profile);
  };

  return (
    <section id="query-section" className="py-16 px-6 max-w-6xl mx-auto scroll-mt-16">
      <div className="text-center max-w-2xl mx-auto mb-10">
        <span className="section-label mb-2">Search &amp; Evaluate</span>
        <h2 className="font-heading font-bold text-3xl md:text-4xl text-gray-900 mb-3">
          Discover Scheme Benefits
        </h2>
        <p className="text-gray-500 text-sm md:text-base">
          Select a domain or type your question below. Optionally expand the profile tab for customized eligibility checking.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-6 items-start">
        {/* Main Form */}
        <QueryForm
          queryText={queryText}
          setQueryText={setQueryText}
          isLoading={isLoading}
          onSubmit={handleSubmit}
          activeDomain={activeDomain}
          setActiveDomain={setActiveDomain}
        />

        {/* Profile Sidebar */}
        <ProfilePanel profile={profile} onChange={setProfile} />
      </div>
    </section>
  );
}
