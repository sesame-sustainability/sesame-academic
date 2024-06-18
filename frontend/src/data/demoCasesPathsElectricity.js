export const pathsElectricityDemoCases = [
  {
    "type": "lca-tea",
    "name": "Solar Power",
    "createdAt": new Date("2022-03-14T14:10:00.541Z"),
    focusedInputs: ["location", "install_type", "panel_ghg"],
    "data": {
      "analysisResult": {
        "LCA": {
          "columns": ["value", "stage", "sub_stage", "pathway"],
          "data": [
            [0, "Enduse", "aggregate", "New Case 1"],
            [0, "GateToEnduse", "aggregate", "New Case 1"],
            [
              0.9148589410870825,
              "Process",
              "installation,open ground, 570kWp, utility, fixed tilt, utility, 1-axis tracking",
              "New Case 1"
            ],
            [
              0.002754700944383389,
              "Process",
              "operation, open ground, 570kWp, utility, fixed tilt, utility, 1-axis tracking",
              "New Case 1"
            ],
            [
              1.4250545677884734,
              "Upstream",
              "MG-Si production, single crystal Si NA, multi crystal Si Europe,",
              "New Case 1"
            ],
            [
              8.422994293903816,
              "Upstream",
              "SG-Si production, single crystal Si NA,  multi crystal Si Europe,",
              "New Case 1"
            ],
            [
              1.2904071416565026,
              "Upstream",
              "cell production, sc, single crystal Si NA",
              "New Case 1"
            ],
            [
              0.2171974394579227,
              "Upstream",
              "electric installation, 570kWp plant, tracking, utility, 1-axis tracking",
              "New Case 1"
            ],
            [
              1.281774887989045,
              "Upstream",
              "inverter, 500kW, utility, fixed tilt, utility, 1-axis tracking",
              "New Case 1"
            ],
            [
              7.45436322214726,
              "Upstream",
              "mounting, open ground, tracking, utility, 1-axis tracking",
              "New Case 1"
            ],
            [
              5.213755721741576,
              "Upstream",
              "panel production, sc, single crystal Si NA",
              "New Case 1"
            ],
            [
              8.456362730331396,
              "Upstream",
              "sc-crystallization, single crystal Si NA",
              "New Case 1"
            ],
            [
              0.007489447328998071,
              "Upstream",
              "silica sand acquisition, single crystal Si NA, multi crystal Si China, multi crystal Si Europe,",
              "New Case 1"
            ],
            [
              2.714613252932009,
              "Upstream",
              "wafer production, sc, single crystal Si NA",
              "New Case 1"
            ]
          ],
          "params": {"indicator": "GWP"},
          "sensitivity": {
            "base_value": 37.40162634730847,
            "inputs": [
              {
                "default_value": 4.7,
                "label": "Power Lost in Transmission",
                "max_value": 37.9633080295931,
                "maximizing_value": 6.11,
                "min_value": 36.85632293349702,
                "minimizing_value": 3.29,
                "name": "loss",
                "unit": "%"
              },
              {
                "default_value": "location with approximate average irradiance of US PV sites (2019)",
                "label": "Location",
                "max_value": 53.970397505800634,
                "maximizing_value": "US NW (Seattle)",
                "min_value": 33.213617263173624,
                "minimizing_value": "US SW (Phoenix)",
                "name": "location",
                "unit": null
              },
              {
                "default_value": "utility, 1-axis tracking",
                "label": "Installation Type",
                "max_value": 42.059046544697196,
                "maximizing_value": "residential",
                "min_value": 37.40162634730847,
                "minimizing_value": "utility, 1-axis tracking",
                "name": "install_type",
                "unit": null
              },
              {
                "default_value": "single Si",
                "label": "Cell Type",
                "max_value": 37.40162634730847,
                "maximizing_value": "single Si",
                "min_value": 14.429876622840055,
                "minimizing_value": "CdTe",
                "name": "cell_type",
                "unit": null
              },
              {
                "default_value": 20,
                "label": "Rated Efficiency",
                "max_value": 52.51553263449551,
                "maximizing_value": 14,
                "min_value": 34.19784953466676,
                "minimizing_value": 22,
                "name": "efficiency",
                "unit": "%"
              },
              {
                "default_value": 30,
                "label": "Lifetime",
                "max_value": 53.40164625665595,
                "maximizing_value": 20,
                "min_value": 29.5303406135694,
                "minimizing_value": 40,
                "name": "lifetime",
                "unit": "years"
              },
              {
                "default_value": 0.8,
                "label": "Degradation Rate",
                "max_value": 39.99549249299656,
                "maximizing_value": 1.18,
                "min_value": 34.46096165017641,
                "minimizing_value": 0.3,
                "name": "degradation",
                "unit": "%/year"
              },
              {
                "default_value": 2.5,
                "label": "Shading Loss",
                "max_value": 39.42600651674201,
                "maximizing_value": 7.5,
                "min_value": 36.465448447900776,
                "minimizing_value": 0,
                "name": "shading",
                "unit": "%"
              },
              {
                "default_value": 1.3,
                "label": "Inverter Loading Ratio",
                "max_value": 38.062397570374635,
                "maximizing_value": 1,
                "min_value": 37.24429986562604,
                "minimizing_value": 1.4,
                "name": "ilr",
                "unit": null
              },
              {
                "default_value": 500,
                "label": "Power Emissions in Panel Production",
                "max_value": 53.72958806507188,
                "maximizing_value": 950,
                "min_value": 29.0562236915627,
                "minimizing_value": 270,
                "name": "panel_ghg",
                "unit": "gCO₂e/kWh"
              },
              {
                "default_value": 10500,
                "label": "Shipping Distance from Panel Production to Installation",
                "max_value": 37.55252672229428,
                "maximizing_value": 18000,
                "min_value": 37.40162634730847,
                "minimizing_value": 10500,
                "name": "shipping_dist",
                "unit": "km"
              }
            ]
          },
          "title": "Lifecycle GHG Emissions",
          "unit": "gCO₂e/kWh",
          "value": "kWh"
        },
        "TEA": {
          "columns": [
            "value",
            "cost_category",
            "cost_category_by_parts",
            "pathway"
          ],
          "data": [
            [33.21302509400033, "Capital", "Capital", "Solar"],
            [12.858282946425113, "Fixed", "Fixed", "Solar"],
            [0, "Fuel", "Fuel", "Solar"],
            [0, "Non-fuel variable", "Non-fuel variable", "Solar"],
            [49.317943336831064, "Delivery", "Delivery", "Solar"],
            [6.057217462455788, "Tax", "Tax", "Solar"]
          ],
          "sensitivity": {
            "base_value": 101.44646883971228,
            "inputs": [
              {
                "default_value": "location with approximate average irradiance of US PV sites (2019)",
                "label": "Location",
                "max_value": 123.5341410648444,
                "maximizing_value": "US NW (Seattle)",
                "min_value": 96.19382703409781,
                "minimizing_value": "US SW (Phoenix)",
                "name": "location",
                "unit": null
              },
              {
                "default_value": "utility, 1-axis tracking",
                "label": "Installation Type",
                "max_value": 181.19142545784837,
                "maximizing_value": "residential",
                "min_value": 101.44646883971228,
                "minimizing_value": "utility, 1-axis tracking",
                "name": "install_type",
                "unit": null
              },
              {
                "default_value": "single Si",
                "label": "Cell Type",
                "max_value": 101.44646883971228,
                "maximizing_value": "single Si",
                "min_value": 96.30078031257761,
                "minimizing_value": "CdTe",
                "name": "cell_type",
                "unit": null
              },
              {
                "default_value": 20,
                "label": "Rated Efficiency",
                "max_value": 122.48583746788974,
                "maximizing_value": 14,
                "min_value": 96.98671762844967,
                "minimizing_value": 22,
                "name": "efficiency",
                "unit": "%"
              },
              {
                "default_value": 30,
                "label": "Lifetime",
                "max_value": 112.37008046588953,
                "maximizing_value": 20,
                "min_value": 96.73329028330187,
                "minimizing_value": 40,
                "name": "lifetime",
                "unit": "years"
              },
              {
                "default_value": 0.8,
                "label": "Degradation Rate",
                "max_value": 104.84485490527814,
                "maximizing_value": 1.18,
                "min_value": 97.5937395003112,
                "minimizing_value": 0.3,
                "name": "degradation",
                "unit": "%/year"
              },
              {
                "default_value": 2.5,
                "label": "Shading Loss",
                "max_value": 104.09873439633041,
                "maximizing_value": 7.5,
                "min_value": 100.21992758739262,
                "minimizing_value": 0,
                "name": "shading",
                "unit": "%"
              },
              {
                "default_value": 40,
                "label": "System Capacity DC",
                "max_value": 110.77986412038103,
                "maximizing_value": 5,
                "min_value": 97.33377635897726,
                "minimizing_value": 100,
                "name": "size",
                "unit": "MW"
              },
              {
                "default_value": 4,
                "label": "Interest Rate, Nominal",
                "max_value": 107.26710206407428,
                "maximizing_value": 6,
                "min_value": 96.14355137990263,
                "minimizing_value": 2,
                "name": "interest_rate",
                "unit": "%/year"
              },
              {
                "default_value": 4.7,
                "label": "Power Lost in Transmission",
                "max_value": 102.95898275212546,
                "maximizing_value": 6.1,
                "min_value": 99.97775057316011,
                "minimizing_value": 3.3,
                "name": "transm_loss",
                "unit": "%"
              }
            ]
          },
          "table": null,
          "title": "TEA Cost Breakdown",
          "unit": "$/MWh",
          "value": "Cost"
        }
      },
      "inputValues": {},
      "customData": {
        "inputValuesByStage": [
          {"nodeChosen": "upstream-solar", "inputValues": {}},
          {"nodeChosen": null, "inputValues": {}},
          {"nodeChosen": null, "inputValues": {}},
          {
            "nodeChosen": "process-solarpowerproduction",
            "inputValues": {
              "location": "location with approximate average irradiance of US PV sites (2019)",
              "install_type": "utility, 1-axis tracking",
              "cell_type": "single Si",
              "efficiency": "20",
              "lifetime": "30",
              "degradation": "0.8",
              "shading": "2.5",
              "ilr": "1.3",
              "production_region": "",
              "panel_ghg": "500",
              "bos_ghg": "500",
              "shipping_dist": "10500",
              "interest_rate": "4",
              "size": "40",
              "user_trans_dist_cost": "47",
              "tax_rate": "6.35"
            }
          },
          {
            "nodeChosen": "gatetoenduse-transmission",
            "inputValues": {"loss": "4.7"}
          },
          {"nodeChosen": "enduse-electricity", "inputValues": {}}
        ],
        "customInputValues": {
          "startWith": "product",
          "selectedProduct": "Electricity",
          "selectedProductType": "Electricity",
          "selectedResource": "Solar",
          "additionalBackendInputValues": {"compute_cost": true},
          "dataSourcesChosen": [null, null, null, null, null, null]
        }
      },
    },
  },
  {
    "type": "lca-tea",
    "name": "Natural Gas Power",
    "createdAt": new Date("2022-03-14T14:10:04.102Z"),
    focusedInputs: ['generator_type', 'use_CCS', 'user_ngprice', 'loss_factor'],
    "data": {
      "analysisResult": {
        "LCA": {
          "columns": ["value", "stage", "sub_stage", "pathway"],
          "data": [
            [0, "Enduse", "aggregate", "New Case 2"],
            [0, "GateToEnduse", "aggregate", "New Case 2"],
            [98.94635100489376, "Process", "aggregate", "New Case 2"],
            [28.967218999999996, "Midstream", "aggregate", "New Case 2"],
            [22.708778000000002, "Upstream", "Processing", "New Case 2"],
            [5.279701, "Upstream", "Processing: Non-Combustion ", "New Case 2"],
            [69.799112, "Upstream", "Recovery", "New Case 2"]
          ],
          "params": {"indicator": "GWP"},
          "sensitivity": {
            "base_value": 566.7912509999999,
            "inputs": [
              {
                "default_value": 4.7,
                "label": "Power Lost in Transmission",
                "max_value": 575.30307,
                "maximizing_value": 6.11,
                "min_value": 558.5274509999999,
                "minimizing_value": 3.29,
                "name": "loss",
                "unit": "%"
              },
              {
                "default_value": "US",
                "label": "Region",
                "max_value": 744.3645849999999,
                "maximizing_value": "ASCC",
                "min_value": 539.9018940000001,
                "minimizing_value": "WECC",
                "name": "generation_region",
                "unit": null
              },
              {
                "default_value": "Mix",
                "label": "Generator Type",
                "max_value": 832.3027689999999,
                "maximizing_value": "Gas Turbine",
                "min_value": 513.824052,
                "minimizing_value": "Combined Cycle",
                "name": "generator_type",
                "unit": null
              },
              {
                "default_value": "No",
                "label": "Use CCS (Carbon Capture & Sequester)",
                "max_value": 566.7912509999999,
                "maximizing_value": "No",
                "min_value": 225.69418800489376,
                "minimizing_value": "Yes",
                "name": "use_CCS",
                "unit": null
              },
              {
                "default_value": 750,
                "label": "Distance, Upstream to Process",
                "max_value": 573.729211,
                "maximizing_value": 975,
                "min_value": 559.853584,
                "minimizing_value": 525,
                "name": "distance",
                "unit": "mi"
              },
              {
                "default_value": 0.1129,
                "label": "Loss, Upstream to Process",
                "max_value": 566.8177129999999,
                "maximizing_value": 0.14677,
                "min_value": 566.7647999999999,
                "minimizing_value": 0.07902999999999999,
                "name": "loss_factor",
                "unit": "%"
              },
              {
                "default_value": "Mix (~50/50 Conventional/Shale)",
                "label": "Natural Gas Type",
                "max_value": 568.1808389999999,
                "maximizing_value": "Shale",
                "min_value": 565.282032,
                "minimizing_value": "Conventional",
                "name": "ng_type",
                "unit": null
              },
              {
                "default_value": "Yes",
                "label": "Count Emissions from Building Well Infrastructure",
                "max_value": 566.7912509999999,
                "maximizing_value": "Yes",
                "min_value": 556.941303,
                "minimizing_value": "No",
                "name": "well_infrastructure",
                "unit": null
              },
              {
                "default_value": "EPA 2019",
                "label": "Methane Leakage Parameter",
                "max_value": 585.4504279999999,
                "maximizing_value": "EDF 2019",
                "min_value": 566.7912509999999,
                "minimizing_value": "EPA 2019",
                "name": "leakage_param",
                "unit": null
              }
            ]
          },
          "title": "Lifecycle GHG Emissions",
          "unit": "gCO₂e/kWh",
          "value": "kWh"
        },
        "TEA": {
          "columns": [
            "value",
            "cost_category",
            "cost_category_by_parts",
            "pathway"
          ],
          "data": [
            [27.45367212262453, "Capital", "Capital", "Natural gas"],
            [2.6881902128731086, "Fixed", "Fixed", "Natural gas"],
            [27.285471683294425, "Fuel", "Fuel", "Natural gas"],
            [
              15.04706222141838,
              "Non-fuel variable",
              "Non-fuel variable",
              "Natural gas"
            ],
            [51.363925434104814, "Delivery", "Delivery", "Natural gas"],
            [4.6021241612533625, "Tax", "Tax", "Natural gas"]
          ],
          "sensitivity": {
            "base_value": 95.6457134296784,
            "inputs": [
              {
                "default_value": "Mix",
                "label": "Generator Type",
                "max_value": 171.51579497932843,
                "maximizing_value": "Gas Turbine",
                "min_value": 93.57315012337695,
                "minimizing_value": "Combined Cycle",
                "name": "turbine",
                "unit": null
              },
              {
                "default_value": "US",
                "label": "Region",
                "max_value": 165.0872215572268,
                "maximizing_value": "HICC",
                "min_value": 93.50187515215664,
                "minimizing_value": "FRCC",
                "name": "gr",
                "unit": null
              },
              {
                "default_value": 750,
                "label": "Powerplant Size",
                "max_value": 102.65538231595319,
                "maximizing_value": 300,
                "min_value": 94.53207021451328,
                "minimizing_value": 900,
                "name": "plant_size",
                "unit": "MW"
              },
              {
                "default_value": 4.7,
                "label": "Power Lost in Transmission",
                "max_value": 97.07174110594622,
                "maximizing_value": 6.1,
                "min_value": 94.26097714424355,
                "minimizing_value": 3.3,
                "name": "transm_loss",
                "unit": "%"
              },
              {
                "default_value": 47,
                "label": "Transmission & Distribution Cost",
                "max_value": 110.44109643072771,
                "maximizing_value": 61.1,
                "min_value": 61.01822129956297,
                "minimizing_value": 14,
                "name": "user_trans_dist_cost",
                "unit": "$/MWh"
              },
              {
                "default_value": "No",
                "label": "Use CCS (Carbon Capture & Sequester)",
                "max_value": 123.45494041761648,
                "maximizing_value": "Yes",
                "min_value": 95.6457134296784,
                "minimizing_value": "No",
                "name": "use_CCS",
                "unit": null
              },
              {
                "default_value": 5,
                "label": "Interest Rate",
                "max_value": 101.56407085180408,
                "maximizing_value": 10,
                "min_value": 92.5138917926244,
                "minimizing_value": 2,
                "name": "interest_rate",
                "unit": "%/yr"
              },
              {
                "default_value": 30,
                "label": "Lifetime",
                "max_value": 99.40133355747437,
                "maximizing_value": 20,
                "min_value": 93.96395469767717,
                "minimizing_value": 40,
                "name": "lifetime",
                "unit": "years"
              }
            ]
          },
          "table": null,
          "title": "TEA Cost Breakdown",
          "unit": "$/MWh",
          "value": "Cost"
        }
      },
      "inputValues": {},
      "customData": {
        "inputValuesByStage": [
          {
            "nodeChosen": "upstream-naturalgas",
            "inputValues": {
              "ng_type": "Mix (~50/50 Conventional/Shale)",
              "well_infrastructure": "Yes",
              "leakage_param": "EPA 2019"
            }
          },
          {"nodeChosen": null, "inputValues": {}},
          {
            "nodeChosen": "midstream-ngelectricitytransportation",
            "inputValues": {
              "mode": "Pipeline",
              "distance": "750",
              "loss_factor": "0.12"
            }
          },
          {
            "nodeChosen": "process-ngpowerproduction",
            "inputValues": {
              "generation_region": "US",
              "generator_type": "Mix",
              "infrastructure_emission_inclusion": "Yes",
              "use_CCS": "Yes",
              "cap_percent_plant": "85",
              "use_user_ci": "",
              "user_ci": "",
              "cap_percent_regen": "85",
              "pipeline_miles": "240",
              "plant_size": "750",
              "economies_of_scale_factor": "0.6",
              "user_ngprice": "2.99",
              "user_trans_dist_cost": "47",
              "sale_tax_rate": "6.35",
              "storage_cost_source": "Default",
              "storage_cost": "",
              "use_user_crf": "Interest Rate",
              "user_crf": "",
              "interest_rate": "5",
              "lifetime": "30"
            }
          },
          {
            "nodeChosen": "gatetoenduse-transmission",
            "inputValues": {"loss": "4.7"}
          },
          {"nodeChosen": "enduse-electricity", "inputValues": {}}
        ],
        "customInputValues": {
          "startWith": "product",
          "selectedProduct": "Electricity",
          "selectedProductType": "Electricity",
          "selectedResource": "Natural Gas",
          "additionalBackendInputValues": {"compute_cost": true},
          "dataSourcesChosen": [null, null, null, null, null, null]
        }
      },
    },
  },
  {
    "type": "lca-tea",
    "name": "Coal Power",
    "createdAt": new Date("2022-03-14T19:47:09.949Z"),
    focusedInputs: ["coal_type", 'distance', "use_CCS"],
    "data": {
      "analysisResult": {
        "LCA": {
          "columns": ["value", "stage", "sub_stage", "pathway"],
          "data": [
            [0, "Enduse", "aggregate", "New Case 1"],
            [0, "GateToEnduse", "aggregate", "New Case 1"],
            [1036.6121339999997, "Process", "aggregate", "New Case 1"],
            [9.845793, "Midstream", "aggregate", "New Case 1"],
            [0, "Upstream", "Coal Cleaning: Non-Combustion ", "New Case 1"],
            [8.215834, "Upstream", "Coal Mining and Cleaning", "New Case 1"],
            [
              42.004424,
              "Upstream",
              "Coal Mining: Non-Combustion ",
              "New Case 1"
            ]
          ],
          "params": {"indicator": "GWP"},
          "sensitivity": {
            "base_value": 1096.6781849999998,
            "inputs": [
              {
                "default_value": 4.7,
                "label": "Power Lost in Transmission",
                "max_value": 1113.14761,
                "maximizing_value": 6.11,
                "min_value": 1080.689129,
                "minimizing_value": 3.29,
                "name": "loss",
                "unit": "%"
              },
              {
                "default_value": "US",
                "label": "Region",
                "max_value": 1694.870977,
                "maximizing_value": "HICC",
                "min_value": 1091.565555,
                "minimizing_value": "RFC",
                "name": "region",
                "unit": null
              },
              {
                "default_value": "Boiler (~99% of US coal turbines)",
                "label": "Generator Type",
                "max_value": 1096.6781849999998,
                "maximizing_value": "Boiler (~99% of US coal turbines)",
                "min_value": 981.5041279999999,
                "minimizing_value": "IGCC - Integrated Gasification Combined Cycle",
                "name": "plant_type",
                "unit": null
              },
              {
                "default_value": "Yes",
                "label": "Count Emissions from Building Powerplant",
                "max_value": 1096.6781849999998,
                "maximizing_value": "Yes",
                "min_value": 1095.5940610000002,
                "minimizing_value": "No",
                "name": "infrastructure_emission_inclusion",
                "unit": null
              },
              {
                "default_value": "No",
                "label": "Use CCS (Carbon Capture & Sequester)",
                "max_value": 1096.6781849999998,
                "maximizing_value": "No",
                "min_value": 367.91489147054693,
                "minimizing_value": "Yes",
                "name": "use_CCS",
                "unit": null
              },
              {
                "default_value": 700,
                "label": "Distance, Upstream to Process",
                "max_value": 1099.631974,
                "maximizing_value": 910,
                "min_value": 1093.7243969999997,
                "minimizing_value": 489.99999999999994,
                "name": "distance",
                "unit": "mi"
              },
              {
                "default_value": 0,
                "label": "Loss, Upstream to Process",
                "max_value": 1096.6781849999998,
                "maximizing_value": 0,
                "min_value": 1096.6781849999998,
                "minimizing_value": 0,
                "name": "loss_factor",
                "unit": "%"
              }
            ]
          },
          "title": "Lifecycle GHG Emissions",
          "unit": "gCO₂e/kWh",
          "value": "kWh"
        },
        "TEA": {
          "columns": [
            "value",
            "cost_category",
            "cost_category_by_parts",
            "pathway"
          ],
          "data": [
            [58.81464067276186, "Capital", "Capital", "Coal"],
            [10.300829805078903, "Fixed", "Fixed", "Coal"],
            [20.618500938090243, "Fuel", "Fuel", "Coal"],
            [
              7.472455403987409,
              "Non-fuel variable",
              "Non-fuel variable",
              "Coal"
            ],
            [49.317943336831064, "Delivery", "Delivery", "Coal"],
            [6.17260810306482, "Tax", "Tax", "Coal"]
          ],
          "sensitivity": {
            "base_value": 152.69697825981427,
            "inputs": [
              {
                "default_value": "Boiler (~99% of US coal turbines)",
                "label": "Generator Type",
                "max_value": 154.4920775388791,
                "maximizing_value": "IGCC - Integrated Gasification Combined Cycle",
                "min_value": 152.69697825981427,
                "minimizing_value": "Boiler (~99% of US coal turbines)",
                "name": "gt",
                "unit": null
              },
              {
                "default_value": "US",
                "label": "Region",
                "max_value": 444.80766710121657,
                "maximizing_value": "NPCC",
                "min_value": 132.53694670778037,
                "minimizing_value": "MRO",
                "name": "gr",
                "unit": null
              },
              {
                "default_value": 650,
                "label": "Powerplant Size",
                "max_value": 175.36726513523422,
                "maximizing_value": 300,
                "min_value": 139.09344794160629,
                "minimizing_value": 1200,
                "name": "plant_size",
                "unit": "MW"
              },
              {
                "default_value": 4.7,
                "label": "Power Lost in Transmission",
                "max_value": 154.97361052353887,
                "maximizing_value": 6.1,
                "min_value": 150.4862670957632,
                "minimizing_value": 3.3,
                "name": "transm_loss",
                "unit": "%"
              },
              {
                "default_value": 47,
                "label": "Transmission & Distribution Cost",
                "max_value": 167.49236126086362,
                "maximizing_value": 61.1,
                "min_value": 118.06948612969886,
                "minimizing_value": 14,
                "name": "user_trans_dist_cost",
                "unit": "$/MWh"
              },
              {
                "default_value": "No",
                "label": "Use CCS (Carbon Capture & Sequester)",
                "max_value": 247.0098920632387,
                "maximizing_value": "Yes",
                "min_value": 152.69697825981427,
                "minimizing_value": "No",
                "name": "use_CCS",
                "unit": null
              },
              {
                "default_value": 5,
                "label": "Interest Rate",
                "max_value": 173.24080322787793,
                "maximizing_value": 10,
                "min_value": 141.62315541995264,
                "minimizing_value": 2,
                "name": "interest_rate",
                "unit": "%"
              },
              {
                "default_value": 30,
                "label": "Lifetime",
                "max_value": 166.49488558605188,
                "maximizing_value": 20,
                "min_value": 146.64476009599733,
                "minimizing_value": 40,
                "name": "lifetime",
                "unit": "years"
              }
            ]
          },
          "table": null,
          "title": "TEA Cost Breakdown",
          "unit": "$/MWh",
          "value": "Cost"
        }
      },
      "inputValues": {},
      "customData": {
        "inputValuesByStage": [
          {
            "nodeChosen": "upstream-coal",
            "inputValues": {
              "coal_type": "Mix (~50% Bituminous, 40% Sub-bituminous, 5% Lignite, 5% Other)",
              "underground_share": "31",
              "well_infrastructure": "Yes"
            }
          },
          {"nodeChosen": null, "inputValues": {}},
          {
            "nodeChosen": "midstream-coaltransportation",
            "inputValues": {
              "mode": "Default Mix",
              "distance": "700",
              "loss_factor": "0"
            }
          },
          {
            "nodeChosen": "process-coalpowerproduction",
            "inputValues": {
              "region": "US",
              "plant_type": "Boiler (~99% of US coal turbines)",
              "infrastructure_emission_inclusion": "Yes",
              "use_CCS": "No",
              "cap_percent_plant": "",
              "use_user_ci": "",
              "user_ci": "",
              "cap_percent_regen": "",
              "pipeline_miles": "",
              "plant_size": "650",
              "economies_of_scale_factor": "0.6",
              "user_coalprice": "2",
              "user_trans_dist_cost": "47",
              "sale_tax_rate": "6.35",
              "storage_cost_source": "",
              "storage_cost": "",
              "interest_rate_or_crf": "Interest Rate",
              "crf": "",
              "interest_rate": "5",
              "lifetime": "30"
            }
          },
          {
            "nodeChosen": "gatetoenduse-transmission",
            "inputValues": {"loss": "4.7"}
          },
          {"nodeChosen": "enduse-electricity", "inputValues": {}}
        ],
        "customInputValues": {
          "startWith": "product",
          "selectedProduct": "Electricity",
          "selectedProductType": "Electricity",
          "selectedResource": "Coal",
          "additionalBackendInputValues": {"compute_cost": true},
          "dataSourcesChosen": [null, null, null, null, null, null]
        }
      },
    },
  },
]