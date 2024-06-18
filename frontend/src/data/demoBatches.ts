type DemoBatch = {
  name: string;
  caseNames: string[];
}

export const demoBatches = [
  {
    name: 'Texas Power',
    caseNames: [
      'Texas Renewable Power System',
      'Texas Renewables with Natural Gas',
    ]
  },
  {
    name: 'California Power',
    caseNames: [
      'California Renewable Power System',
      'California Renewables with Natural Gas',
    ]
  },
  {
    name: 'Power Paths',
    isFocusLinkActive: false,
    caseNames: [
      'Solar Power',
      'Natural Gas Power',
      'Coal Power',
    ]
  },
  {
    name: 'Car Decarbonization Options',
    caseNames: [
      'Rapid Electrification',
      'Limited Change',
    ]
  },
  {
    name: 'Clean H2',
    caseNames: [
      'Blue Hydrogen',
      'Electrolytic Hydrogen',
      'Green Hydrogen',
    ]
  },
  // congress
  {
    name: 'Role of Electricity in Aluminum Production',
    caseNames: [
      'Aluminum - IEA SDS',
      'Aluminum - Solar',
    ]
  },
  {
    name: 'CCS in Iron & Steel',
    caseNames: [
      'Iron & Steel - BF-BOF',
      'Iron & Steel - BF-BOF + CCS',
    ]
  },
  {
    name: 'California with and without the 2035 ICE Ban',
    caseNames: [
      'California: AEO20',
      'California: 2035 ICE Ban',
    ]
  },
  // power greenfield
  {
    name: 'Texas: High Decarbonization for Low Cost',
    caseNames: [
      'Texas: Low Renewables',
      'Texas: Medium Renewables',
      'Texas: High Renewables',
    ]
  },
  {
    name: 'California: Impact of Price Trends and Carbon Taxes',
    caseNames: [
      'California',
      'California: High Renewables',
      'California: Decreased Renewables Cost',
    ]
  },
  {
    name: 'Florida: 100% Renewable Options',
    caseNames: [
      'Florida: 100% Solar',
      'Florida: Solar & Wind',
      'Florida: Solar, Wind & Nuclear',
    ]
  },
  {
    name: 'Regional Variability',
    caseNames: [
      'Regional Variability: Southeast',
      'Regional Variability: Northwest',
      'Regional Variability: North Central',
    ]
  },
]