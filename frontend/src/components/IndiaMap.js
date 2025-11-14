import React from 'react';

const IndiaMap = ({ onStateSelect }) => {
  // All 28 States + 8 UTs
  const states = [
    // States (28)
    { id: 'AP', name: 'Andhra Pradesh', region: 'south' },
    { id: 'AR', name: 'Arunachal Pradesh', region: 'northeast' },
    { id: 'AS', name: 'Assam', region: 'northeast' },
    { id: 'BR', name: 'Bihar', region: 'east' },
    { id: 'CT', name: 'Chhattisgarh', region: 'central' },
    { id: 'GA', name: 'Goa', region: 'west' },
    { id: 'GJ', name: 'Gujarat', region: 'west' },
    { id: 'HR', name: 'Haryana', region: 'north' },
    { id: 'HP', name: 'Himachal Pradesh', region: 'north' },
    { id: 'JH', name: 'Jharkhand', region: 'east' },
    { id: 'KA', name: 'Karnataka', region: 'south' },
    { id: 'KL', name: 'Kerala', region: 'south' },
    { id: 'MP', name: 'Madhya Pradesh', region: 'central' },
    { id: 'MH', name: 'Maharashtra', region: 'west' },
    { id: 'MN', name: 'Manipur', region: 'northeast' },
    { id: 'ML', name: 'Meghalaya', region: 'northeast' },
    { id: 'MZ', name: 'Mizoram', region: 'northeast' },
    { id: 'NL', name: 'Nagaland', region: 'northeast' },
    { id: 'OD', name: 'Odisha', region: 'east' },
    { id: 'PB', name: 'Punjab', region: 'north' },
    { id: 'RJ', name: 'Rajasthan', region: 'north' },
    { id: 'SK', name: 'Sikkim', region: 'northeast' },
    { id: 'TN', name: 'Tamil Nadu', region: 'south' },
    { id: 'TG', name: 'Telangana', region: 'south' },
    { id: 'TR', name: 'Tripura', region: 'northeast' },
    { id: 'UP', name: 'Uttar Pradesh', region: 'north' },
    { id: 'UT', name: 'Uttarakhand', region: 'north' },
    { id: 'WB', name: 'West Bengal', region: 'east' },
    // Union Territories (8)
    { id: 'AN', name: 'Andaman and Nicobar Islands', region: 'islands' },
    { id: 'CH', name: 'Chandigarh', region: 'north' },
    { id: 'DN', name: 'Dadra and Nagar Haveli and Daman and Diu', region: 'west' },
    { id: 'DL', name: 'Delhi', region: 'north' },
    { id: 'JK', name: 'Jammu and Kashmir', region: 'north' },
    { id: 'LA', name: 'Ladakh', region: 'north' },
    { id: 'LD', name: 'Lakshadweep', region: 'islands' },
    { id: 'PY', name: 'Puducherry', region: 'south' }
  ];

  const regionColors = {
    north: 'bg-blue-100 hover:bg-blue-200',
    south: 'bg-green-100 hover:bg-green-200',
    east: 'bg-yellow-100 hover:bg-yellow-200',
    west: 'bg-orange-100 hover:bg-orange-200',
    central: 'bg-purple-100 hover:bg-purple-200',
    northeast: 'bg-pink-100 hover:bg-pink-200',
    islands: 'bg-teal-100 hover:bg-teal-200'
  };

  // Group states by region
  const groupedStates = states.reduce((acc, state) => {
    if (!acc[state.region]) acc[state.region] = [];
    acc[state.region].push(state);
    return acc;
  }, {});

  const regionNames = {
    north: 'North India',
    south: 'South India',
    east: 'East India',
    west: 'West India',
    central: 'Central India',
    northeast: 'Northeast India',
    islands: 'Island Territories'
  };

  return (
    <div className="w-full bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-2xl font-bold text-gray-800 mb-4 text-center">
        Select Your State
      </h3>
      <p className="text-gray-600 mb-6 text-center">
        Choose your state to view car buying groups in your region
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {Object.keys(regionNames).map((region) => (
          <div key={region} className="space-y-2">
            <h4 className="font-semibold text-sm text-gray-700 uppercase tracking-wide border-b-2 pb-1">
              {regionNames[region]}
            </h4>
            <div className="space-y-1">
              {groupedStates[region]?.map((state) => (
                <button
                  key={state.id}
                  onClick={() => onStateSelect(state.name)}
                  className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 ${regionColors[region]} border border-transparent hover:border-gray-300 hover:shadow-md`}
                >
                  {state.name}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default IndiaMap;
