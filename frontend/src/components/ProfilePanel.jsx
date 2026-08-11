import { useState } from 'react';

const STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
  'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
  'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
  'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
  'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
  'Delhi', 'Puducherry', 'Jammu & Kashmir', 'Ladakh',
];

const OCCUPATIONS = [
  'Farmer', 'Agricultural Labourer', 'Student', 'Teacher', 'Government Employee',
  'Private Employee', 'Self-employed / Business', 'Daily Wage Worker',
  'Homemaker', 'Unemployed', 'Other',
];

const DEFAULT_PROFILE = {
  age: '', state: '', district: '', occupation: '', annual_income: '',
  land_acres: '', is_student: false, is_farmer: false,
};

export default function ProfilePanel({ profile, onChange }) {
  const [open, setOpen] = useState(false);

  const handleChange = (field, value) => onChange({ ...profile, [field]: value });

  const hasData = Object.entries(profile).some(([k, v]) =>
    k === 'is_student' || k === 'is_farmer' ? v : v !== ''
  );

  return (
    <div className="card overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-5 py-4 bg-gray-50 border-b border-gray-200 hover:bg-gray-100 transition-colors"
      >
        <span className="flex items-center gap-2 text-sm font-semibold text-gray-700">
          👤 Your Profile
          {hasData && (
            <span className="w-2 h-2 rounded-full bg-brand-500" title="Profile has data" />
          )}
        </span>
        <span className={`text-gray-400 text-xs transition-transform duration-200 ${open ? 'rotate-180' : ''}`}>
          ▼
        </span>
      </button>

      {open && (
        <div className="p-5 flex flex-col gap-4">
          <p className="text-xs text-gray-400 leading-relaxed -mt-1">
            Optional — helps the AI check your eligibility more accurately.
          </p>

          {/* Age + State */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Age</label>
              <input
                type="number" min="1" max="120"
                value={profile.age}
                onChange={e => handleChange('age', e.target.value)}
                className="input-field"
                placeholder="e.g. 28"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">District</label>
              <input
                type="text"
                value={profile.district}
                onChange={e => handleChange('district', e.target.value)}
                className="input-field"
                placeholder="e.g. Erode"
              />
            </div>
          </div>

          {/* State */}
          <div>
            <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">State</label>
            <select
              value={profile.state}
              onChange={e => handleChange('state', e.target.value)}
              className="input-field"
            >
              <option value="">Select state…</option>
              {STATES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>

          {/* Occupation */}
          <div>
            <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Occupation</label>
            <select
              value={profile.occupation}
              onChange={e => handleChange('occupation', e.target.value)}
              className="input-field"
            >
              <option value="">Select occupation…</option>
              {OCCUPATIONS.map(o => <option key={o} value={o}>{o}</option>)}
            </select>
          </div>

          {/* Annual Income + Land */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Annual Income (₹)</label>
              <input
                type="number" min="0"
                value={profile.annual_income}
                onChange={e => handleChange('annual_income', e.target.value)}
                className="input-field"
                placeholder="e.g. 150000"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Land (Acres)</label>
              <input
                type="number" min="0" step="0.1"
                value={profile.land_acres}
                onChange={e => handleChange('land_acres', e.target.value)}
                className="input-field"
                placeholder="e.g. 2.5"
              />
            </div>
          </div>

          {/* Toggles */}
          <div className="flex flex-col gap-3 pt-1 border-t border-gray-100">
            {[
              { field: 'is_student', label: 'Currently a student' },
              { field: 'is_farmer',  label: 'Currently a farmer'  },
            ].map(({ field, label }) => (
              <label key={field} className="flex items-center justify-between cursor-pointer">
                <span className="text-sm text-gray-700">{label}</span>
                <div className="relative">
                  <input
                    type="checkbox"
                    checked={profile[field]}
                    onChange={e => handleChange(field, e.target.checked)}
                    className="sr-only"
                  />
                  <div
                    onClick={() => handleChange(field, !profile[field])}
                    className={`w-10 h-5 rounded-full cursor-pointer transition-colors duration-200 ${profile[field] ? 'bg-brand-500' : 'bg-gray-300'}`}
                  >
                    <div className={`absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform duration-200 ${profile[field] ? 'translate-x-5' : ''}`} />
                  </div>
                </div>
              </label>
            ))}
          </div>

          {/* Clear */}
          <button
            onClick={() => onChange(DEFAULT_PROFILE)}
            className="w-full text-xs text-gray-400 hover:text-gray-600 py-1 transition-colors"
          >
            Clear profile
          </button>
        </div>
      )}
    </div>
  );
}
