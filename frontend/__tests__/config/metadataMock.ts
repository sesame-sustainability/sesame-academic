export const links: Link[] = [
  {
    node: {
      start: "enduse-steam",
      end: "process-coalsteamproduction",
      id: "enduse-steam-process-coalsteamproduction",
    },
  },
  {
    node: {
      start: "enduse-steam",
      end: "process-naturalgassteamproduction",
      id: "enduse-steam-process-naturalgassteamproduction",
    },
  },
  {
    node: {
      start: "enduse-electricity",
      end: "gatetoenduse-transmission",
      id: "enduse-electricity-gatetoenduse-transmission",
    },
  },
  {
    node: {
      start: "enduse-methanol",
      end: "gatetoenduse-methanoltransportation",
      id: "enduse-methanol-gatetoenduse-methanoltransportation",
    },
  },
  {
    node: {
      start: "enduse-lng",
      end: "gatetoenduse-lngtransportation",
      id: "enduse-lng-gatetoenduse-lngtransportation",
    },
  },
  {
    node: {
      start: "enduse-gasoline",
      end: "gatetoenduse-gasolinetransportation",
      id: "enduse-gasoline-gatetoenduse-gasolinetransportation",
    },
  },
  {
    node: {
      start: "enduse-diesel",
      end: "gatetoenduse-dieseltransportation",
      id: "enduse-diesel-gatetoenduse-dieseltransportation",
    },
  },
  {
    node: {
      start: "enduse-lpg",
      end: "gatetoenduse-lpgtransportation",
      id: "enduse-lpg-gatetoenduse-lpgtransportation",
    },
  },
  {
    node: {
      start: "enduse-dimethylether",
      end: "gatetoenduse-dmetransportation",
      id: "enduse-dimethylether-gatetoenduse-dmetransportation",
    },
  },
  {
    node: {
      start: "enduse-hydrogen",
      end: "gatetoenduse-hydrogengastransportation",
      id: "enduse-hydrogen-gatetoenduse-hydrogengastransportation",
    },
  },
  {
    node: {
      start: "gatetoenduse-transmission",
      end: "process-ngpowerproduction",
      id: "gatetoenduse-transmission-process-ngpowerproduction",
    },
  },
  {
    node: {
      start: "gatetoenduse-transmission",
      end: "process-coalpowerproduction",
      id: "gatetoenduse-transmission-process-coalpowerproduction",
    },
  },
  {
    node: {
      start: "gatetoenduse-transmission",
      end: "process-windpowerproduction",
      id: "gatetoenduse-transmission-process-windpowerproduction",
    },
  },
  {
    node: {
      start: "gatetoenduse-transmission",
      end: "process-solarpowerproduction",
      id: "gatetoenduse-transmission-process-solarpowerproduction",
    },
  },
  {
    node: {
      start: "gatetoenduse-methanoltransportation",
      end: "process-methanolproduction",
      id: "gatetoenduse-methanoltransportation-process-methanolproduction",
    },
  },
  {
    node: {
      start: "gatetoenduse-lngtransportation",
      end: "process-lngproduction",
      id: "gatetoenduse-lngtransportation-process-lngproduction",
    },
  },
  {
    node: {
      start: "gatetoenduse-gasolinetransportation",
      end: "process-gasolineproduction",
      id: "gatetoenduse-gasolinetransportation-process-gasolineproduction",
    },
  },
  {
    node: {
      start: "gatetoenduse-dieseltransportation",
      end: "process-dieselproduction",
      id: "gatetoenduse-dieseltransportation-process-dieselproduction",
    },
  },
  {
    node: {
      start: "gatetoenduse-lpgtransportation",
      end: "process-lpgproduction",
      id: "gatetoenduse-lpgtransportation-process-lpgproduction",
    },
  },
  {
    node: {
      start: "gatetoenduse-dmetransportation",
      end: "process-dmeproduction",
      id: "gatetoenduse-dmetransportation-process-dmeproduction",
    },
  },
  {
    node: {
      start: "gatetoenduse-hydrogengastransportation",
      end: "process-hydrogenproductionsmr",
      id:
        "gatetoenduse-hydrogengastransportation-process-hydrogenproductionsmr",
    },
  },
  {
    node: {
      start: "gatetoenduse-hydrogengastransportation",
      end: "process-hydrogenproductioncoal",
      id:
        "gatetoenduse-hydrogengastransportation-process-hydrogenproductioncoal",
    },
  },
  {
    node: {
      start: "gatetoenduse-hydrogengastransportation",
      end: "process-hydrogenproductionelec",
      id:
        "gatetoenduse-hydrogengastransportation-process-hydrogenproductionelec",
    },
  },
  {
    node: {
      start: "gatetoenduse-transmission",
      end: "process-hydropowerproduction",
      id: "gatetoenduse-transmission-process-hydropowerproduction",
    },
  },
  {
    node: {
      start: "gatetoenduse-transmission",
      end: "process-lwrnuclearpowerproduction",
      id: "gatetoenduse-transmission-process-lwrnuclearpowerproduction",
    },
  },
  {
    node: {
      start: "gatetoenduse-transmission",
      end: "process-htgrnuclearpowerproduction",
      id: "gatetoenduse-transmission-process-htgrnuclearpowerproduction",
    },
  },
  {
    node: {
      start: "gatetoenduse-ethanoltransportation",
      end: "process-cornethanolproduction",
      id: "gatetoenduse-ethanoltransportation-process-cornethanolproduction",
    },
  },
  {
    node: {
      start: "gatetoenduse-ethanoltransportation-1",
      end: "process-cornstoverethanolproduction",
      id:
        "gatetoenduse-ethanoltransportation-1-process-cornstoverethanolproduction",
    },
  },
  {
    node: {
      start: "process-ngpowerproduction",
      end: "midstream-ngelectricitytransportation",
      id: "process-ngpowerproduction-midstream-ngelectricitytransportation",
    },
  },
  {
    node: {
      start: "process-coalpowerproduction",
      end: "midstream-coaltransportation",
      id: "process-coalpowerproduction-midstream-coaltransportation",
    },
  },
  {
    node: {
      start: "process-methanolproduction",
      end: "midstream-ngnonelectricitytransportation",
      id: "process-methanolproduction-midstream-ngnonelectricitytransportation",
    },
  },
  {
    node: {
      start: "process-lngproduction",
      end: "midstream-ngnonelectricitytransportation",
      id: "process-lngproduction-midstream-ngnonelectricitytransportation",
    },
  },
  {
    node: {
      start: "process-gasolineproduction",
      end: "midstream-crudetransportation",
      id: "process-gasolineproduction-midstream-crudetransportation",
    },
  },
  {
    node: {
      start: "process-dieselproduction",
      end: "midstream-crudetransportation",
      id: "process-dieselproduction-midstream-crudetransportation",
    },
  },
  {
    node: {
      start: "process-lpgproduction",
      end: "midstream-crudetransportation",
      id: "process-lpgproduction-midstream-crudetransportation",
    },
  },
  {
    node: {
      start: "process-dmeproduction",
      end: "midstream-ngnonelectricitytransportation",
      id: "process-dmeproduction-midstream-ngnonelectricitytransportation",
    },
  },
  {
    node: {
      start: "process-hydrogenproductionsmr",
      end: "midstream-ngnonelectricitytransportation",
      id:
        "process-hydrogenproductionsmr-midstream-ngnonelectricitytransportation",
    },
  },
  {
    node: {
      start: "process-hydrogenproductioncoal",
      end: "midstream-coaltransportation",
      id: "process-hydrogenproductioncoal-midstream-coaltransportation",
    },
  },
  {
    node: {
      start: "process-coalsteamproduction",
      end: "midstream-coaltransportation",
      id: "process-coalsteamproduction-midstream-coaltransportation",
    },
  },
  {
    node: {
      start: "process-naturalgassteamproduction",
      end: "midstream-ngnonelectricitytransportation",
      id:
        "process-naturalgassteamproduction-midstream-ngnonelectricitytransportation",
    },
  },
  {
    node: {
      start: "process-cornethanolproduction",
      end: "midstream-corntransportation",
      id: "process-cornethanolproduction-midstream-corntransportation",
    },
  },
  {
    node: {
      start: "process-cornstoverethanolproduction",
      end: "midstream-cornstovertransportation",
      id:
        "process-cornstoverethanolproduction-midstream-cornstovertransportation",
    },
  },
  {
    node: {
      start: "enduse-ethanol_withbiogen",
      end: "gatetoenduse-ethanoltransportation-1",
      id: "enduse-ethanol_withbiogen-gatetoenduse-ethanoltransportation-1",
    },
  },
  {
    node: {
      start: "enduse-ethanol_nobiogen",
      end: "gatetoenduse-ethanoltransportation",
      id: "enduse-ethanol_nobiogen-gatetoenduse-ethanoltransportation",
    },
  },
  {
    node: {
      start: "process-lwrnuclearpowerproduction",
      end: "midstream-uraniumtransportation",
      id: "process-lwrnuclearpowerproduction-midstream-uraniumtransportation",
    },
  },
  {
    node: {
      start: "process-htgrnuclearpowerproduction",
      end: "midstream-uraniumtransportation",
      id: "process-htgrnuclearpowerproduction-midstream-uraniumtransportation",
    },
  },
  {
    node: {
      start: "midstream-ngelectricitytransportation",
      end: "upstream-naturalgas",
      id: "midstream-ngelectricitytransportation-upstream-naturalgas",
    },
  },
  {
    node: {
      start: "midstream-ngnonelectricitytransportation",
      end: "upstream-naturalgas",
      id: "midstream-ngnonelectricitytransportation-upstream-naturalgas",
    },
  },
  {
    node: {
      start: "midstream-coaltransportation",
      end: "upstream-coal",
      id: "midstream-coaltransportation-upstream-coal",
    },
  },
  {
    node: {
      start: "midstream-crudetransportation",
      end: "upstream-conventionalcrudeoil",
      id: "midstream-crudetransportation-upstream-conventionalcrudeoil",
    },
  },
  {
    node: {
      start: "midstream-corntransportation",
      end: "upstream-corn(nobiogeniccarbonaccounting)",
      id:
        "midstream-corntransportation-upstream-corn(nobiogeniccarbonaccounting)",
    },
  },
  {
    node: {
      start: "midstream-cornstovertransportation",
      end: "upstream-cornstover(withbiogeniccarbonaccounting)",
      id:
        "midstream-cornstovertransportation-upstream-cornstover(withbiogeniccarbonaccounting)",
    },
  },
  {
    node: {
      start: "midstream-uraniumtransportation",
      end: "upstream-uraniumforlwrnuclearpowerproduction",
      id:
        "midstream-uraniumtransportation-upstream-uraniumforlwrnuclearpowerproduction",
    },
  },
  {
    node: {
      start: "midstream-uraniumtransportation",
      end: "upstream-uraniumforhtgrnuclearpowerproduction",
      id:
        "midstream-uraniumtransportation-upstream-uraniumforhtgrnuclearpowerproduction",
    },
  },
  {
    node: {
      start: "process-hydropowerproduction",
      end: "upstream-hydropower",
      id: "process-hydropowerproduction-upstream-hydropower",
    },
  },
  {
    node: {
      start: "process-windpowerproduction",
      end: "upstream-wind",
      id: "process-windpowerproduction-upstream-wind",
    },
  },
  {
    node: {
      start: "process-solarpowerproduction",
      end: "upstream-solar",
      id: "process-solarpowerproduction-upstream-solar",
    },
  },
  {
    node: {
      start: "process-hydrogenproductionelec",
      end: "upstream-hydropower",
      id: "process-hydrogenproductionelec-upstream-hydropower",
    },
  },
];
export const stages: Stage[] = [
  {
    node: {
      id: "enduse",
      name: "Enduse",
      activities: [
        {
          category: "Electricity",
          id: "enduse-electricity",
          name: "Electricity",
          sources: [
            {
              id: "enduse-electricity-default",
              name: "Default",
              user_inputs: [
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "1" }],
                  label: "Amount in kWh",
                  name: "amount",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: "Chemical",
          id: "enduse-dimethylether",
          name: "Dimethyl Ether",
          sources: [
            {
              id: "enduse-dimethylether-default",
              name: "Default",
              user_inputs: [
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "1" }],
                  label: "Amount in kg",
                  name: "amount",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: "Chemical",
          id: "enduse-hydrogen",
          name: "Hydrogen",
          sources: [
            {
              id: "enduse-hydrogen-default",
              name: "Default",
              user_inputs: [
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "1" }],
                  label: "Amount in MJ",
                  name: "amount",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: "Chemical",
          id: "enduse-methanol",
          name: "Methanol",
          sources: [
            {
              id: "enduse-methanol-default",
              name: "Default",
              user_inputs: [
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "1" }],
                  label: "Amount in kg",
                  name: "amount",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: "Chemical",
          id: "enduse-lng",
          name: "LNG",
          sources: [
            {
              id: "enduse-lng-default",
              name: "Default",
              user_inputs: [
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "1" }],
                  label: "Amount in kg",
                  name: "amount",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: "Fuel",
          id: "enduse-gasoline",
          name: "Gasoline",
          sources: [
            {
              id: "enduse-gasoline-default",
              name: "Default",
              user_inputs: [
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "1" }],
                  label: "Amount in MJ",
                  name: "amount",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: "Fuel",
          id: "enduse-diesel",
          name: "Diesel",
          sources: [
            {
              id: "enduse-diesel-default",
              name: "Default",
              user_inputs: [
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "1" }],
                  label: "Amount in MJ",
                  name: "amount",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: "Fuel",
          id: "enduse-lpg",
          name: "LPG",
          sources: [
            {
              id: "enduse-lpg-default",
              name: "Default",
              user_inputs: [
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "1" }],
                  label: "Amount in MJ",
                  name: "amount",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: "Fuel",
          id: "enduse-steam",
          name: "Steam",
          sources: [
            {
              id: "enduse-steam-default",
              name: "Default",
              user_inputs: [
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [],
                  label: "Amount in MJ",
                  name: "amount",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: "Fuel",
          id: "enduse-ethanol_nobiogen",
          name: "Ethanol_nobiogen",
          sources: [
            {
              id: "enduse-ethanol_nobiogen-default",
              name: "Default",
              user_inputs: [
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "1" }],
                  label: "Amount in MJ",
                  name: "amount",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: "Fuel",
          id: "enduse-ethanol_withbiogen",
          name: "Ethanol_withbiogen",
          sources: [
            {
              id: "enduse-ethanol_withbiogen-default",
              name: "Default",
              user_inputs: [
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "1" }],
                  label: "Amount in MJ",
                  name: "amount",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
              ],
            },
          ],
        },
      ],
      categories: ["Electricity", "Chemical", "Fuel"],
    },
  },
  {
    node: {
      id: "gatetoenduse",
      name: "GateToEnduse",
      activities: [
        {
          category: null,
          id: "gatetoenduse-transmission",
          name: "Transmission",
          sources: [
            {
              id: "gatetoenduse-transmission-literaturereview",
              name: "Literature review",
              user_inputs: [
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "4.671" }],
                  label: "Electricity loss in transmission (%)",
                  name: "loss",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [100], name: "lt" },
                    { args: [0], name: "gte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "gatetoenduse-methanoltransportation",
          name: "MethanolTransportation",
          sources: [
            {
              id: "gatetoenduse-methanoltransportation-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"default mix"' }],
                  label: "Mode",
                  name: "mode",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [
                    {
                      conditionals: [
                        {
                          args: ["mode", "default mix"],
                          name: "input_equal_to",
                        },
                      ],
                      value: "472.5",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "barge"], name: "input_equal_to" },
                      ],
                      value: "520.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "pipeline"], name: "input_equal_to" },
                      ],
                      value: "564.9122807",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "rail"], name: "input_equal_to" },
                      ],
                      value: "664.9122807",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "truck"], name: "input_equal_to" },
                      ],
                      value: "110.0",
                    },
                  ],
                  label: "Distance in miles",
                  name: "distance",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "0.025" }],
                  label: "Transportation Loss in %",
                  name: "loss",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                    { args: [100], name: "lte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "gatetoenduse-gasolinetransportation",
          name: "GasolineTransportation",
          sources: [
            {
              id: "gatetoenduse-gasolinetransportation-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"truck"' }],
                  label: "Mode",
                  name: "mode",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [
                    {
                      conditionals: [
                        { args: ["mode", "truck"], name: "input_equal_to" },
                      ],
                      value: "30.0",
                    },
                  ],
                  label: "Distance in miles",
                  name: "distance",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "0.081" }],
                  label: "Transportation Loss in %",
                  name: "loss",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                    { args: [100], name: "lte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "gatetoenduse-dieseltransportation",
          name: "DieselTransportation",
          sources: [
            {
              id: "gatetoenduse-dieseltransportation-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"default mix"' }],
                  label: "Mode",
                  name: "mode",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [
                    {
                      conditionals: [
                        {
                          args: ["mode", "default mix"],
                          name: "input_equal_to",
                        },
                      ],
                      value: "255.03",
                    },
                    {
                      conditionals: [
                        {
                          args: ["mode", "ocean tanker"],
                          name: "input_equal_to",
                        },
                      ],
                      value: "1300.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "barge"], name: "input_equal_to" },
                      ],
                      value: "200.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "pipeline"], name: "input_equal_to" },
                      ],
                      value: "110.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "rail"], name: "input_equal_to" },
                      ],
                      value: "490.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "truck"], name: "input_equal_to" },
                      ],
                      value: "30.0",
                    },
                  ],
                  label: "Distance in miles",
                  name: "distance",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "0.004" }],
                  label: "Transportation Loss in %",
                  name: "loss",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                    { args: [100], name: "lte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "gatetoenduse-dmetransportation",
          name: "DMETransportation",
          sources: [
            {
              id: "gatetoenduse-dmetransportation-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"default mix"' }],
                  label: "Mode",
                  name: "mode",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [
                    {
                      conditionals: [
                        {
                          args: ["mode", "default mix"],
                          name: "input_equal_to",
                        },
                      ],
                      value: "652.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "barge"], name: "input_equal_to" },
                      ],
                      value: "520.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "pipeline"], name: "input_equal_to" },
                      ],
                      value: "550.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "rail"], name: "input_equal_to" },
                      ],
                      value: "800.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "truck"], name: "input_equal_to" },
                      ],
                      value: "30.0",
                    },
                  ],
                  label: "Distance in miles",
                  name: "distance",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "0.004" }],
                  label: "Transportation Loss in %",
                  name: "loss",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                    { args: [100], name: "lte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "gatetoenduse-lngtransportation",
          name: "LNGTransportation",
          sources: [
            {
              id: "gatetoenduse-lngtransportation-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"default mix"' }],
                  label: "Mode",
                  name: "mode",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [
                    {
                      conditionals: [
                        {
                          args: ["mode", "default mix"],
                          name: "input_equal_to",
                        },
                      ],
                      value: "690.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "barge"], name: "input_equal_to" },
                      ],
                      value: "520.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "rail"], name: "input_equal_to" },
                      ],
                      value: "800.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "truck"], name: "input_equal_to" },
                      ],
                      value: "30.0",
                    },
                  ],
                  label: "Distance in miles",
                  name: "distance",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "1.3159999999999998" }],
                  label: "Transportation Loss in %",
                  name: "loss",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                    { args: [100], name: "lte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "gatetoenduse-lpgtransportation",
          name: "LPGTransportation",
          sources: [
            {
              id: "gatetoenduse-lpgtransportation-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"default mix"' }],
                  label: "Mode",
                  name: "mode",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [
                    {
                      conditionals: [
                        {
                          args: ["mode", "default mix"],
                          name: "input_equal_to",
                        },
                      ],
                      value: "666.8",
                    },
                    {
                      conditionals: [
                        {
                          args: ["mode", "ocean tanker"],
                          name: "input_equal_to",
                        },
                      ],
                      value: "1560.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "barge"], name: "input_equal_to" },
                      ],
                      value: "520.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "pipeline"], name: "input_equal_to" },
                      ],
                      value: "400.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "rail"], name: "input_equal_to" },
                      ],
                      value: "800.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "truck"], name: "input_equal_to" },
                      ],
                      value: "30.0",
                    },
                  ],
                  label: "Distance in miles",
                  name: "distance",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "0.006" }],
                  label: "Transportation Loss in %",
                  name: "loss",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                    { args: [100], name: "lte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "gatetoenduse-hydrogengastransportation",
          name: "HydrogenGasTransportation",
          sources: [
            {
              id: "gatetoenduse-hydrogengastransportation-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"default mix"' }],
                  label: "Mode",
                  name: "mode",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [
                    {
                      conditionals: [
                        {
                          args: ["mode", "default mix"],
                          name: "input_equal_to",
                        },
                      ],
                      value: "750.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "pipeline"], name: "input_equal_to" },
                      ],
                      value: "750.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "truck"], name: "input_equal_to" },
                      ],
                      value: "30.0",
                    },
                  ],
                  label: "Distance in miles",
                  name: "distance",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "0.0" }],
                  label: "Transportation Loss in %",
                  name: "loss",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                    { args: [100], name: "lte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "gatetoenduse-ethanoltransportation",
          name: "Ethanol transportation",
          sources: [
            {
              id: "gatetoenduse-ethanoltransportation-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"default mix"' }],
                  label: "Mode",
                  name: "mode",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [
                    {
                      conditionals: [
                        {
                          args: ["mode", "default mix"],
                          name: "input_equal_to",
                        },
                      ],
                      value: "736.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "barge"], name: "input_equal_to" },
                      ],
                      value: "520.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "pipeline"], name: "input_equal_to" },
                      ],
                      value: "600.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "rail"], name: "input_equal_to" },
                      ],
                      value: "800.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "truck"], name: "input_equal_to" },
                      ],
                      value: "110.0",
                    },
                  ],
                  label: "Distance in miles",
                  name: "distance",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "0.05" }],
                  label: "Transportation Loss in %",
                  name: "loss",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                    { args: [100], name: "lte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "gatetoenduse-ethanoltransportation-1",
          name: "Ethanol transportation",
          sources: [
            {
              id: "gatetoenduse-ethanoltransportation-greet-1",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"default mix"' }],
                  label: "Mode",
                  name: "mode",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [
                    {
                      conditionals: [
                        {
                          args: ["mode", "default mix"],
                          name: "input_equal_to",
                        },
                      ],
                      value: "736.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "barge"], name: "input_equal_to" },
                      ],
                      value: "520.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "pipeline"], name: "input_equal_to" },
                      ],
                      value: "600.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "rail"], name: "input_equal_to" },
                      ],
                      value: "800.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "truck"], name: "input_equal_to" },
                      ],
                      value: "110.0",
                    },
                  ],
                  label: "Distance in miles",
                  name: "distance",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "0.05" }],
                  label: "Transportation Loss in %",
                  name: "loss",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                    { args: [100], name: "lte" },
                  ],
                },
              ],
            },
          ],
        },
      ],
      categories: [],
    },
  },
  {
    node: {
      id: "process",
      name: "Process",
      activities: [
        {
          category: null,
          id: "process-coalsteamproduction",
          name: "Coal steam production",
          sources: [
            {
              id: "process-coalsteamproduction-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Coal type",
                  name: "coal_type",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [],
                  label:
                    "Industrial Boiler Efficiency (%), between 75 and 90 recommended",
                  name: "boiler_efficiency",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                    { args: [100], name: "lte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "process-naturalgassteamproduction",
          name: "Natural gas steam production",
          sources: [
            {
              id: "process-naturalgassteamproduction-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [],
                  label:
                    "Industrial Boiler Efficiency (%), between 70 and 86 recommended",
                  name: "boiler_efficiency",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                    { args: [100], name: "lte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "process-solarpowerproduction",
          name: "SolarPowerProduction",
          sources: [
            {
              id: "process-solarpowerproduction-default",
              name: "Default",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [
                    {
                      conditionals: [],
                      value:
                        '"location with approximate average irradiance of US PV sites (2019)"',
                    },
                  ],
                  label: "Location of Installation",
                  name: "location",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [
                    {
                      conditionals: [],
                      value: '"multi crystal Si (most common)"',
                    },
                  ],
                  label: "Cell Type",
                  name: "cell_type",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [
                    {
                      name: "input_equal_to",
                      args: [["cell_type"], ["multi crystal Si (most common)"]],
                    },
                  ],
                  defaults: [{ conditionals: [], value: '"China"' }],
                  label: "Panel Produced in",
                  name: "panel_type",
                  options: [
                    { conditionals: [], value: "Europe" },
                    { conditionals: [], value: "China" },
                  ],
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [
                    { conditionals: [], value: '"utility, 1-axis tracking"' },
                  ],
                  label: "Installation Type",
                  name: "install_type",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "2.5" }],
                  label: "Shading Losses (%)",
                  name: "shading",
                  options: [
                    { conditionals: [], value: "0" },
                    { conditionals: [], value: "2.5" },
                    { conditionals: [], value: "5" },
                    { conditionals: [], value: "7.5" },
                    { conditionals: [], value: "10" },
                  ],
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "30" }],
                  label: "Lifetime (year)",
                  name: "lifetime",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "18" }],
                  label: "Efficiency, STC Rated (%)",
                  name: "efficiency",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "0.8" }],
                  label: "Degradation Rate (%/year)",
                  name: "degradation",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "1.3" }],
                  label: "Inverter Loading Ratio",
                  name: "ilr",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "660" }],
                  label: "Emissions in Panel Production (gCO₂e/kWh)",
                  name: "panel_ghg",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "510" }],
                  label: "Emissions in BOS Production (gCO₂e/kWh)",
                  name: "bos_ghg",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "20000" }],
                  label:
                    "Shipping Distance from Panel Production to Installation (km)",
                  name: "shipping_dist",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "process-windpowerproduction",
          name: "WindPowerProduction",
          sources: [
            {
              id: "process-windpowerproduction-default",
              name: "Default",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [
                    { conditionals: [], value: '"onshore wind farm > 50MW"' },
                  ],
                  label: "Installation Type",
                  name: "install_type",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"Wind Speed"' }],
                  label: "Choose Capacity Factor or Wind Speed",
                  name: "choice",
                  options: [
                    { conditionals: [], value: "Capacity Factor" },
                    { conditionals: [], value: "Wind Speed" },
                  ],
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [
                    {
                      name: "input_equal_to",
                      args: [["choice"], ["Wind Speed"]],
                    },
                  ],
                  defaults: [{ conditionals: [], value: '"medium (8 m/s)"' }],
                  label: "Avg Wind Speed",
                  name: "wind_speed",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [
                    {
                      name: "input_equal_to",
                      args: [["choice"], ["Capacity Factor"]],
                    },
                  ],
                  defaults: [],
                  label: "Capacity Factor (in %)",
                  name: "cap_fac",
                  options: [
                    { conditionals: [], value: "20" },
                    { conditionals: [], value: "25" },
                    { conditionals: [], value: "30" },
                    { conditionals: [], value: "35" },
                    { conditionals: [], value: "40" },
                    { conditionals: [], value: "45" },
                    { conditionals: [], value: "50" },
                  ],
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "100" }],
                  label: "Hub Height (m)",
                  name: "hub_height",
                  options: [
                    { conditionals: [], value: "70" },
                    { conditionals: [], value: "80" },
                    { conditionals: [], value: "90" },
                    { conditionals: [], value: "100" },
                    { conditionals: [], value: "110" },
                    { conditionals: [], value: "120" },
                  ],
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"2014-2016"' }],
                  label: "Year Installed",
                  name: "years",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [
                    { conditionals: [], value: '"Typical Onshore md-spd"' },
                  ],
                  label: "Turbine Model",
                  name: "turbine_model",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "20" }],
                  label: "Lifetime (years)",
                  name: "lifetime",
                  options: [
                    { conditionals: [], value: "5" },
                    { conditionals: [], value: "10" },
                    { conditionals: [], value: "20" },
                    { conditionals: [], value: "30" },
                    { conditionals: [], value: "40" },
                  ],
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "600" }],
                  label: "Emissions in Manufacturing (gCO₂e/kWh)",
                  name: "carbon_intensity",
                  options: [
                    { conditionals: [], value: "50" },
                    { conditionals: [], value: "100" },
                    { conditionals: [], value: "200" },
                    { conditionals: [], value: "400" },
                    { conditionals: [], value: "600" },
                    { conditionals: [], value: "800" },
                    { conditionals: [], value: "1000" },
                  ],
                  validators: [],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "process-ngpowerproduction",
          name: "NGPowerProduction",
          sources: [
            {
              id: "process-ngpowerproduction-aspen",
              name: "ASPEN",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Turbine",
                  name: "turbine",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Model",
                  name: "model",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [],
                  label: "Loading",
                  name: "loading_ratio",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                    { args: [1], name: "lte" },
                  ],
                },
              ],
            },
            {
              id: "process-ngpowerproduction-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [
                    {
                      conditionals: [],
                      value: '"Based on Generator Type and Region"',
                    },
                  ],
                  label: "Efficiency Source",
                  name: "efficiency_source",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [
                    {
                      name: "input_equal_to",
                      args: [["efficiency_source"], ["User-Specified"]],
                    },
                  ],
                  defaults: [],
                  label:
                    "Power Generation Efficiency (%), between 28 and 55 recommended",
                  name: "efficiency",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                    { args: [100], name: "lte" },
                  ],
                },
                {
                  categorical: true,
                  conditionals: [
                    {
                      name: "input_equal_to",
                      args: [
                        ["efficiency_source"],
                        ["Based on Generator Type and Region"],
                      ],
                    },
                  ],
                  defaults: [{ conditionals: [], value: '"US"' }],
                  label: "Generation Region",
                  name: "generation_region",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [
                    {
                      name: "input_equal_to",
                      args: [
                        ["efficiency_source"],
                        ["Based on Generator Type and Region"],
                      ],
                    },
                  ],
                  defaults: [
                    {
                      conditionals: [],
                      value:
                        '"Mix (9% Boiler + 6% Gas Turbine + 84% Combined Cycle + 1% Internal Combustion Engine) (Efficiency - 50.1%)"',
                    },
                  ],
                  label: "Generator Type",
                  name: "generator_type",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"yes"' }],
                  label: "Include Plant Infrastructure Emissions?",
                  name: "infrastructure_emission_inclusion",
                  validators: [],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "process-coalpowerproduction",
          name: "CoalPowerProduction",
          sources: [
            {
              id: "process-coalpowerproduction-aspen",
              name: "ASPEN",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Plant Type",
                  name: "plant_type",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Location",
                  name: "location",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Loading",
                  name: "loading_ratio",
                  validators: [],
                },
              ],
            },
            {
              id: "process-coalpowerproduction-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [
                    {
                      conditionals: [],
                      value:
                        '"Mix (50% bituminous_40% subbituminous_4.4% lignite_5.1% other)"',
                    },
                  ],
                  label: "Coal Rank",
                  name: "coal_rank",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [
                    {
                      conditionals: [],
                      value: '"Based on Generator Type and Region"',
                    },
                  ],
                  label: "Efficiency Source",
                  name: "efficiency_source",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [
                    {
                      name: "input_equal_to",
                      args: [["efficiency_source"], ["User-Specified"]],
                    },
                  ],
                  defaults: [],
                  label:
                    "Power Generation Efficiency (%), between 28 and 55 recommended",
                  name: "efficiency",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                    { args: [100], name: "lte" },
                  ],
                },
                {
                  categorical: true,
                  conditionals: [
                    {
                      name: "input_equal_to",
                      args: [
                        ["efficiency_source"],
                        ["Based on Generator Type and Region"],
                      ],
                    },
                  ],
                  defaults: [{ conditionals: [], value: '"US"' }],
                  label: "Generation Region",
                  name: "generation_region",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [
                    {
                      name: "input_equal_to",
                      args: [
                        ["efficiency_source"],
                        ["Based on Generator Type and Region"],
                      ],
                    },
                  ],
                  defaults: [
                    { conditionals: [], value: '"Mix (Efficiency - 36.03%)"' },
                  ],
                  label: "Generator Type",
                  name: "generator_type",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"yes"' }],
                  label: "Include Plant Infrastructure Emissions?",
                  name: "infrastructure_emission_inclusion",
                  validators: [],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "process-methanolproduction",
          name: "MethanolProduction",
          sources: [
            {
              id: "process-methanolproduction-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Plant Design Type",
                  name: "plant_type",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Method for Estimating Credits of Co-Products",
                  name: "method",
                  validators: [],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "process-gasolineproduction",
          name: "GasolineProduction",
          sources: [
            {
              id: "process-gasolineproduction-greet",
              name: "GREET",
              user_inputs: [],
            },
          ],
        },
        {
          category: null,
          id: "process-dieselproduction",
          name: "DieselProduction",
          sources: [
            {
              id: "process-dieselproduction-greet",
              name: "GREET",
              user_inputs: [],
            },
          ],
        },
        {
          category: null,
          id: "process-lngproduction",
          name: "LNGProduction",
          sources: [
            {
              id: "process-lngproduction-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Leakage Parameter",
                  name: "leakage_param",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Well Infrastructure Emissions",
                  name: "infrastructure_emissions",
                  validators: [],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "process-lpgproduction",
          name: "LPGProduction",
          sources: [
            {
              id: "process-lpgproduction-greet",
              name: "GREET",
              user_inputs: [],
            },
          ],
        },
        {
          category: null,
          id: "process-dmeproduction",
          name: "DMEProduction",
          sources: [
            {
              id: "process-dmeproduction-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Plant Design Type",
                  name: "plant_type",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Method for Estimating Credits of Co-Products",
                  name: "method",
                  validators: [],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "process-hydrogenproductionsmr",
          name: "HydrogenProductionSMR",
          sources: [
            {
              id: "process-hydrogenproductionsmr-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Plant Type",
                  name: "plant_type",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Hydrogen Phase",
                  name: "h2_phase",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Plant Design Type",
                  name: "design_type",
                  validators: [],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "process-hydrogenproductioncoal",
          name: "HydrogenProductionCoal",
          sources: [
            {
              id: "process-hydrogenproductioncoal-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Plant Type",
                  name: "plant_type",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Hydrogen Phase",
                  name: "h2_phase",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Plant Design Type",
                  name: "design_type",
                  validators: [],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "process-hydrogenproductionelec",
          name: "HydrogenProductionElec",
          sources: [
            {
              id: "process-hydrogenproductionelec-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Plant Type",
                  name: "plant_type",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Hydrogen Phase",
                  name: "h2_phase",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Plant Design Type",
                  name: "design_type",
                  validators: [],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "process-hydropowerproduction",
          name: "Hydro power production",
          sources: [
            {
              id: "process-hydropowerproduction-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"US"' }],
                  label: "Generation Region",
                  name: "generation_region",
                  validators: [],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "process-lwrnuclearpowerproduction",
          name: "LWR Nuclear power production",
          sources: [
            {
              id: "process-lwrnuclearpowerproduction-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"US"' }],
                  label: "Generation Region",
                  name: "generation_region",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [
                    {
                      conditionals: [],
                      value: '"Mix (100% PWR_Pressurized Water Reactor)"',
                    },
                  ],
                  label: "LWR Sub-Type",
                  name: "lwr_sub_type",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"yes"' }],
                  label: "Include Infrastructure Emissions?",
                  name: "infrastructure_emission_inclusion",
                  validators: [],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "process-htgrnuclearpowerproduction",
          name: "HTGR Nuclear power production",
          sources: [
            {
              id: "process-htgrnuclearpowerproduction-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"US"' }],
                  label: "Generation Region",
                  name: "generation_region",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"yes"' }],
                  label: "Include Infrastructure Emissions?",
                  name: "infrastructure_emission_inclusion",
                  validators: [],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "process-cornethanolproduction",
          name: "Corn ethanol production",
          sources: [
            {
              id: "process-cornethanolproduction-mixedsources",
              name: "Mixed sources",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Natural Gas & Power Emissions Model",
                  name: "natural_gas_and_power_emissions_model",
                  validators: [],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "process-cornstoverethanolproduction",
          name: "Corn stover ethanol production",
          sources: [
            {
              id: "process-cornstoverethanolproduction-mixedsources",
              name: "Mixed sources",
              user_inputs: [],
            },
          ],
        },
      ],
      categories: [],
    },
  },
  {
    node: {
      id: "midstream",
      name: "Midstream",
      activities: [
        {
          category: null,
          id: "midstream-uraniumtransportation",
          name: "Uranium transportation",
          sources: [
            {
              id: "midstream-uraniumtransportation-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"truck"' }],
                  label: "Mode",
                  name: "mode",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [
                    {
                      conditionals: [
                        { args: ["mode", "truck"], name: "input_equal_to" },
                      ],
                      value: "1360.0",
                    },
                  ],
                  label: "Distance in miles",
                  name: "distance",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "0.0" }],
                  label: "Loss Factor in %",
                  name: "loss_factor",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                    { args: [100], name: "lte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "midstream-corntransportation",
          name: "Corn transportation",
          sources: [
            {
              id: "midstream-corntransportation-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"default mix"' }],
                  label: "Mode",
                  name: "mode",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [
                    {
                      conditionals: [
                        {
                          args: ["mode", "default mix"],
                          name: "input_equal_to",
                        },
                      ],
                      value: "50.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "barge"], name: "input_equal_to" },
                      ],
                      value: "350.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "rail"], name: "input_equal_to" },
                      ],
                      value: "400.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "truck"], name: "input_equal_to" },
                      ],
                      value: "50.0",
                    },
                  ],
                  label: "Distance in miles",
                  name: "distance",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "0.0" }],
                  label: "Loss Factor in %",
                  name: "loss_factor",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                    { args: [100], name: "lte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "midstream-cornstovertransportation",
          name: "Corn stover transportation",
          sources: [
            {
              id: "midstream-cornstovertransportation-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"truck"' }],
                  label: "Mode",
                  name: "mode",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [
                    {
                      conditionals: [
                        { args: ["mode", "truck"], name: "input_equal_to" },
                      ],
                      value: "53.30846678",
                    },
                  ],
                  label: "Distance in miles",
                  name: "distance",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "0.0" }],
                  label: "Loss Factor in %",
                  name: "loss_factor",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                    { args: [100], name: "lte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "midstream-ngelectricitytransportation",
          name: "NGElectricityTransportation",
          sources: [
            {
              id: "midstream-ngelectricitytransportation-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"pipeline"' }],
                  label: "Mode",
                  name: "mode",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [
                    {
                      conditionals: [
                        { args: ["mode", "pipeline"], name: "input_equal_to" },
                      ],
                      value: "750.0",
                    },
                  ],
                  label: "Distance in miles",
                  name: "distance",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "0.1129" }],
                  label: "Loss Factor in %",
                  name: "loss_factor",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                    { args: [100], name: "lte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "midstream-ngnonelectricitytransportation",
          name: "NGNonElectricityTransportation",
          sources: [
            {
              id: "midstream-ngnonelectricitytransportation-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"pipeline"' }],
                  label: "Mode",
                  name: "mode",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [
                    {
                      conditionals: [
                        { args: ["mode", "pipeline"], name: "input_equal_to" },
                      ],
                      value: "750.0",
                    },
                  ],
                  label: "Distance in miles",
                  name: "distance",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "0.0225932" }],
                  label: "Loss Factor in %",
                  name: "loss_factor",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                    { args: [100], name: "lte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "midstream-coaltransportation",
          name: "CoalTransportation",
          sources: [
            {
              id: "midstream-coaltransportation-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"mix"' }],
                  label: "Sub Feed",
                  name: "sub_feed",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"default mix"' }],
                  label: "Mode",
                  name: "mode",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [
                    {
                      conditionals: [
                        {
                          args: ["mode", "default mix"],
                          name: "input_equal_to",
                        },
                      ],
                      value: "699.91",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "barge"], name: "input_equal_to" },
                      ],
                      value: "320.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "rail"], name: "input_equal_to" },
                      ],
                      value: "740.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "truck"], name: "input_equal_to" },
                      ],
                      value: "150.0",
                    },
                  ],
                  label: "Distance in miles",
                  name: "distance",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "0.0" }],
                  label: "Loss Factor in %",
                  name: "loss_factor",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                    { args: [100], name: "lte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "midstream-crudetransportation",
          name: "CrudeTransportation",
          sources: [
            {
              id: "midstream-crudetransportation-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"default mix"' }],
                  label: "Mode",
                  name: "mode",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [
                    {
                      conditionals: [
                        {
                          args: ["mode", "default mix"],
                          name: "input_equal_to",
                        },
                      ],
                      value: "2507.276661",
                    },
                    {
                      conditionals: [
                        {
                          args: ["mode", "ocean tanker"],
                          name: "input_equal_to",
                        },
                      ],
                      value: "7812.026849",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "barge"], name: "input_equal_to" },
                      ],
                      value: "750.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "pipeline"], name: "input_equal_to" },
                      ],
                      value: "587.415895",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "rail"], name: "input_equal_to" },
                      ],
                      value: "797.0",
                    },
                    {
                      conditionals: [
                        { args: ["mode", "truck"], name: "input_equal_to" },
                      ],
                      value: "30.0",
                    },
                  ],
                  label: "Distance in miles",
                  name: "distance",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                  ],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "0.0062" }],
                  label: "Loss Factor in %",
                  name: "loss_factor",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                    { args: [100], name: "lte" },
                  ],
                },
              ],
            },
          ],
        },
      ],
      categories: [],
    },
  },
  {
    node: {
      id: "upstream",
      name: "Upstream",
      activities: [
        {
          category: null,
          id: "upstream-solar",
          name: "Solar",
          sources: [
            { id: "upstream-solar-default", name: "Default", user_inputs: [] },
          ],
        },
        {
          category: null,
          id: "upstream-wind",
          name: "Wind",
          sources: [
            { id: "upstream-wind-default", name: "Default", user_inputs: [] },
          ],
        },
        {
          category: null,
          id: "upstream-hydropower",
          name: "Hydropower",
          sources: [
            {
              id: "upstream-hydropower-default",
              name: "Default",
              user_inputs: [],
            },
          ],
        },
        {
          category: null,
          id: "upstream-naturalgas",
          name: "Natural Gas",
          sources: [
            {
              id: "upstream-naturalgas-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [
                    {
                      conditionals: [],
                      value: '"Mix (48% conventional, 52% shale)"',
                    },
                  ],
                  label: "Natural Gas Type",
                  name: "ng_type",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"Yes"' }],
                  label: "Include Well Infrastructure Emissions?",
                  name: "well_infrastructure",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"EPA 2019"' }],
                  label: "Leakage Parameter",
                  name: "leakage_param",
                  validators: [],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "upstream-coal",
          name: "Coal",
          sources: [
            {
              id: "upstream-coal-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: '"Yes"' }],
                  label: "Include Well Infrastructure Emissions?",
                  name: "well_infrastructure",
                  validators: [],
                },
                {
                  categorical: false,
                  conditionals: [],
                  defaults: [{ conditionals: [], value: "31" }],
                  label: "% Underground Mining Share",
                  name: "underground_share",
                  validators: [
                    { args: [], name: "numeric" },
                    { args: [0], name: "gte" },
                    { args: [100], name: "lte" },
                  ],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "upstream-conventionalcrudeoil",
          name: "Conventional Crude Oil",
          sources: [
            {
              id: "upstream-conventionalcrudeoil-greet",
              name: "GREET",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Crude Type",
                  name: "crude_type",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [
                    {
                      name: "input_included_in",
                      args: [["crude_type"], ["Oil Sand", "Shale Oil"]],
                    },
                  ],
                  defaults: [],
                  label: "Crude Sub-Type",
                  name: "crude_sub_type",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Include Well Infrastructure Emissions?",
                  name: "well_infrastructure",
                  validators: [],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "upstream-corn(nobiogeniccarbonaccounting)",
          name: "Corn (no biogenic carbon accounting)",
          sources: [
            {
              id: "upstream-corn(nobiogeniccarbonaccounting)-mixedsource",
              name: "Mixed source",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "LUC Model",
                  name: "luc_model",
                  validators: [],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "upstream-cornstover(withbiogeniccarbonaccounting)",
          name: "Corn stover (with biogenic carbon accounting)",
          sources: [
            {
              id:
                "upstream-cornstover(withbiogeniccarbonaccounting)-mixedsource",
              name: "Mixed source",
              user_inputs: [
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Farm Management Scenario (Corn Only)",
                  name: "farm_management_corn_only)",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Farm Management Scenario (Corn & Stover)",
                  name: "farm_management_corn_and_stover)",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "LUC Model",
                  name: "luc_model",
                  validators: [],
                },
                {
                  categorical: true,
                  conditionals: [],
                  defaults: [],
                  label: "Harvesting Method",
                  name: "harvesting_method",
                  validators: [],
                },
              ],
            },
          ],
        },
        {
          category: null,
          id: "upstream-uraniumforlwrnuclearpowerproduction",
          name: "Uranium for LWR nuclear power production",
          sources: [
            {
              id: "upstream-uraniumforlwrnuclearpowerproduction-greet",
              name: "GREET",
              user_inputs: [],
            },
          ],
        },
        {
          category: null,
          id: "upstream-uraniumforhtgrnuclearpowerproduction",
          name: "Uranium for HTGR nuclear power production",
          sources: [
            {
              id: "upstream-uraniumforhtgrnuclearpowerproduction-greet",
              name: "GREET",
              user_inputs: [],
            },
          ],
        },
      ],
      categories: [],
    },
  },
];
export const indicators: LCAIndicator[] = [
  {
    label: "Global Warming Potential",
    value: "GWP",
    id: "GWP-Global Warming Potential",
  },
  {
    label: "Acidification Potential",
    value: "AP",
    id: "AP-Acidification Potential",
  },
  {
    label: "Eutrophication Potential",
    value: "EP",
    id: "EP-Eutrophication Potential",
  },
  { label: "Energy", value: "Energy", id: "Energy-Energy" },
  { label: "Water", value: "Water", id: "Water-Water" },
];
export const analyses: TEAAnalysis[] = [
  {
    analysis: {
      name: "wind",
      pathway_id: [
        "enduse-electricity",
        "process-windpowerproduction",
        "upstream-wind",
      ],
      user_inputs: [
        {
          categorical: true,
          conditionals: [],
          defaults: [],
          label: "Group By",
          name: "group_by",
          validators: [],
        },
        {
          categorical: true,
          conditionals: [],
          defaults: [],
          label: "Region",
          name: "region",
          validators: [],
        },
        {
          categorical: true,
          conditionals: [],
          defaults: [],
          label: "Installation Type",
          name: "install_type",
          validators: [],
        },
        {
          categorical: false,
          conditionals: [],
          defaults: [{ conditionals: [], value: '"NREL"' }],
          label: "Select Data Source for Technology Costs",
          name: "cost_source",
          options: [
            { conditionals: [], value: "NREL" },
            { conditionals: [], value: "EIA" },
          ],
          validators: [],
        },
        {
          categorical: false,
          conditionals: [],
          defaults: [{ conditionals: [], value: '"ATB"' }],
          label: "Select Data Source for Finance Costs",
          name: "finance_source",
          options: [
            { conditionals: [], value: "ATB" },
            { conditionals: [], value: "EIA" },
            { conditionals: [], value: "ReEDS" },
          ],
          validators: [],
        },
        {
          categorical: false,
          conditionals: [],
          defaults: [],
          label: "Tax Credits",
          name: "tax_credit",
          validators: [
            { args: [], name: "numeric" },
            { args: [0], name: "gte" },
          ],
        },
      ],
    },
    id: "enduse-electricity-process-windpowerproduction-upstream-wind",
  },
  {
    analysis: {
      name: "ng",
      pathway_id: [
        "enduse-electricity",
        "process-ngpowerproduction",
        "upstream-naturalgas",
      ],
      user_inputs: [
        {
          categorical: true,
          conditionals: [],
          defaults: [],
          label: "Turbine",
          name: "turbine",
          validators: [],
        },
        {
          categorical: true,
          conditionals: [],
          defaults: [],
          label: "Generation Region",
          name: "gr",
          validators: [],
        },
        {
          categorical: false,
          conditionals: [],
          defaults: [{ conditionals: [], value: "3" }],
          label: "Interest Rate in %",
          name: "interest_rate",
          validators: [
            { args: [], name: "numeric" },
            { args: [0], name: "gte" },
            { args: [100], name: "lte" },
          ],
        },
        {
          categorical: false,
          conditionals: [],
          defaults: [{ conditionals: [], value: "5" }],
          label: "Discount Rate in %",
          name: "discount_rate",
          validators: [
            { args: [], name: "numeric" },
            { args: [0], name: "gte" },
            { args: [100], name: "lte" },
          ],
        },
        {
          categorical: false,
          conditionals: [],
          defaults: [{ conditionals: [], value: "20" }],
          label: "Lifetime",
          name: "lifetime",
          validators: [
            { args: [], name: "integer" },
            { args: [0], name: "gte" },
          ],
        },
      ],
    },
    id: "enduse-electricity-process-ngpowerproduction-upstream-naturalgas",
  },
  {
    analysis: {
      name: "coal",
      pathway_id: [
        "enduse-electricity",
        "process-coalpowerproduction",
        "upstream-coal",
      ],
      user_inputs: [
        {
          categorical: true,
          conditionals: [],
          defaults: [],
          label: "Generator Type",
          name: "gt",
          validators: [],
        },
        {
          categorical: true,
          conditionals: [],
          defaults: [],
          label: "Generation Region",
          name: "gr",
          validators: [],
        },
        {
          categorical: false,
          conditionals: [],
          defaults: [{ conditionals: [], value: "3" }],
          label: "Interest Rate in %",
          name: "interest_rate",
          validators: [
            { args: [], name: "numeric" },
            { args: [0], name: "gte" },
            { args: [100], name: "lte" },
          ],
        },
        {
          categorical: false,
          conditionals: [],
          defaults: [{ conditionals: [], value: "5" }],
          label: "Discount Rate in %",
          name: "discount_rate",
          validators: [
            { args: [], name: "numeric" },
            { args: [0], name: "gte" },
            { args: [100], name: "lte" },
          ],
        },
        {
          categorical: false,
          conditionals: [],
          defaults: [{ conditionals: [], value: "20" }],
          label: "Lifetime",
          name: "lifetime",
          validators: [
            { args: [], name: "integer" },
            { args: [0], name: "gte" },
          ],
        },
      ],
    },
    id: "enduse-electricity-process-coalpowerproduction-upstream-coal",
  },
  {
    analysis: {
      name: "hydrogen",
      pathway_id: [
        "enduse-electricity",
        "process-hydrogenproductionsmr",
        "upstream-naturalgas",
      ],
      user_inputs: [
        {
          categorical: true,
          conditionals: [],
          defaults: [],
          label: "Production Type",
          name: "pt",
          validators: [],
        },
        {
          categorical: false,
          conditionals: [],
          defaults: [{ conditionals: [], value: "300" }],
          label: "Hydrogen Production Rate [m3/hr]",
          name: "H2_produced",
          validators: [
            { args: [], name: "numeric" },
            { args: [0], name: "gte" },
            { args: [1000000], name: "lte" },
          ],
        },
        {
          categorical: false,
          conditionals: [],
          defaults: [{ conditionals: [], value: "20" }],
          label: "Asset Capacity Factor in %",
          name: "capacity_factor",
          validators: [
            { args: [], name: "numeric" },
            { args: [0], name: "gte" },
            { args: [100], name: "lte" },
          ],
        },
        {
          categorical: false,
          conditionals: [],
          defaults: [{ conditionals: [], value: "12" }],
          label: "CO2 Transport Cost in $/ton",
          name: "CO2_Cost",
          validators: [
            { args: [], name: "numeric" },
            { args: [0], name: "gte" },
            { args: [1000], name: "lte" },
          ],
        },
        {
          categorical: false,
          conditionals: [],
          defaults: [{ conditionals: [], value: "200" }],
          label: "Distance from Production Site to Demand Center (km)",
          name: "distance",
          validators: [
            { args: [], name: "numeric" },
            { args: [0], name: "gte" },
            { args: [1000], name: "lte" },
          ],
        },
        {
          categorical: false,
          conditionals: [],
          defaults: [{ conditionals: [], value: "20" }],
          label: "Price of Power or Cost of Power [$/MWh]",
          name: "Power_Price",
          validators: [
            { args: [], name: "numeric" },
            { args: [0], name: "gte" },
            { args: [1000], name: "lte" },
          ],
        },
        {
          categorical: false,
          conditionals: [
            { args: ["Production Type", "Alk"], name: "input_not_equal_to" },
            { args: ["Production Type", "PEM"], name: "input_not_equal_to" },
          ],
          defaults: [{ conditionals: [], value: "2" }],
          label: "Natural Gas Price [$/MMBtu]",
          name: "Gas_Cost",
          validators: [
            { args: [], name: "numeric" },
            { args: [0], name: "gte" },
            { args: [100], name: "lte" },
          ],
        },
        {
          categorical: false,
          conditionals: [],
          defaults: [{ conditionals: [], value: "10" }],
          label: "Discount Rate in % ",
          name: "discount_rate",
          validators: [
            { args: [], name: "numeric" },
            { args: [0], name: "gte" },
            { args: [100], name: "lte" },
          ],
        },
        {
          categorical: false,
          conditionals: [],
          defaults: [{ conditionals: [], value: "20" }],
          label: "Lifetime",
          name: "lifetime",
          validators: [
            { args: [], name: "integer" },
            { args: [0], name: "gte" },
          ],
        },
      ],
    },
    id: "enduse-electricity-process-hydrogenproductionsmr-upstream-naturalgas",
  },
];
