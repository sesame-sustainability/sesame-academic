export const hydrogenDemoCases = [
  {
    "type": "lca-tea",
    "name": "Gray Hydrogen",
    "createdAt": new Date("2022-03-14T19:54:28.128Z"),
    focusedInputs: ['loss_factor', 'distance', 'user_ngprice'],
    "data": {
      "analysisResult": {
        "LCA": {
          "columns": ["value", "stage", "sub_stage", "pathway"],
          "data": [
            [0, "Enduse", "aggregate", "New Case 2"],
            [4.927644999999999, "GateToEnduse", "aggregate", "New Case 2"],
            [
              13.660373,
              "Process",
              "G.H2 Compression and Precooling",
              "New Case 2"
            ],
            [36.897648000000004, "Process", "G.H2 Production", "New Case 2"],
            [
              46.544683000000006,
              "Process",
              "G.H2 Production: Non-Combustion Emissions",
              "New Case 2"
            ],
            [
              -11.830449999999999,
              "Process",
              "Production of Displaced Steam",
              "New Case 2"
            ],
            [3.895997, "Midstream", "aggregate", "New Case 2"],
            [3.0515129999999995, "Upstream", "Processing", "New Case 2"],
            [
              0.7094739999999999,
              "Upstream",
              "Processing: Non-Combustion ",
              "New Case 2"
            ],
            [9.37932, "Upstream", "Recovery", "New Case 2"]
          ],
          "params": {"indicator": "GWP"},
          "sensitivity": {
            "base_value": 107.23521900000001,
            "inputs": [
              {
                "default_value": 750,
                "label": "Distance, Process to Use (mi)",
                "max_value": 108.71352500000002,
                "maximizing_value": 975,
                "min_value": 105.75688500000003,
                "minimizing_value": 525,
                "name": "distance",
                "unit": null
              },
              {
                "default_value": 0,
                "label": "Loss, Process to Use (%)",
                "max_value": 107.23521900000001,
                "maximizing_value": 0,
                "min_value": 107.23521900000001,
                "minimizing_value": 0,
                "name": "loss",
                "unit": null
              },
              {
                "default_value": 750,
                "label": "Distance, Upstream to Process",
                "max_value": 108.40421900000003,
                "maximizing_value": 975,
                "min_value": 106.06645600000002,
                "minimizing_value": 525,
                "name": "distance",
                "unit": "mi"
              },
              {
                "default_value": 0.0225932,
                "label": "Loss, Upstream to Process",
                "max_value": 107.236101,
                "maximizing_value": 0.02937116,
                "min_value": 107.234335,
                "minimizing_value": 0.01581524,
                "name": "loss_factor",
                "unit": "%"
              },
              {
                "default_value": "Mix (~50/50 Conventional/Shale)",
                "label": "Natural Gas Type",
                "max_value": 107.469254,
                "maximizing_value": "Shale",
                "min_value": 106.98134500000002,
                "minimizing_value": "Conventional",
                "name": "ng_type",
                "unit": null
              },
              {
                "default_value": "Yes",
                "label": "Count Emissions from Building Well Infrastructure",
                "max_value": 107.23521900000001,
                "maximizing_value": "Yes",
                "min_value": 105.57742900000001,
                "minimizing_value": "No",
                "name": "well_infrastructure",
                "unit": null
              },
              {
                "default_value": "EPA 2019",
                "label": "Methane Leakage Parameter",
                "max_value": 110.375871,
                "maximizing_value": "EDF 2019",
                "min_value": 107.23521900000001,
                "minimizing_value": "EPA 2019",
                "name": "leakage_param",
                "unit": null
              }
            ]
          },
          "title": "Lifecycle GHG Emissions",
          "unit": "gCO₂e/MJ",
          "value": "MJ"
        },
        "TEA": {
          "columns": [
            "value",
            "cost_category",
            "cost_category_by_parts",
            "pathway"
          ],
          "data": [
            [0.25033080798238927, "Capital", "Capital", "Hydrogen"],
            [0.1605992036780571, "Fixed", "Fixed", "Hydrogen"],
            [
              0.5631677796749002,
              "Fuel (gas or power)",
              "Fuel (gas or power)",
              "Hydrogen"
            ],
            [
              0.00989010989010989,
              "Non-fuel variable",
              "Non-fuel variable",
              "Hydrogen"
            ],
            [0.8046699999999999, "H2 transport", "H2 transport", "Hydrogen"],
            [0, "CO2 transport", "CO2 transport", "Hydrogen"],
            [0, "CO2 storage", "CO2 storage", "Hydrogen"]
          ],
          "sensitivity": {
            "base_value": 6.891137528290745,
            "inputs": [
              {
                "default_value": 57.2,
                "label": "Hydrogen Production Efficiency",
                "max_value": 8.62904028093136,
                "maximizing_value": 74.36,
                "min_value": 5.137104287142048,
                "minimizing_value": 40.04,
                "name": "effic",
                "unit": "kWh/kg_H₂"
              },
              {
                "default_value": 750,
                "label": "Distance, Process to Use",
                "max_value": 7.132538528290745,
                "maximizing_value": 975,
                "min_value": 6.649736528290745,
                "minimizing_value": 525,
                "name": "distance",
                "unit": "mi"
              },
              {
                "default_value": 300,
                "label": "Hydrogen Production Rate",
                "max_value": 6.831759565213471,
                "maximizing_value": 390,
                "min_value": 6.978367333279849,
                "minimizing_value": 210,
                "name": "H2_produced",
                "unit": "m³/hr"
              },
              {
                "default_value": 1771,
                "label": "Capital Cost",
                "max_value": 7.171724131301025,
                "maximizing_value": 2302.3,
                "min_value": 6.610550925280465,
                "minimizing_value": 1239.6999999999998,
                "name": "capex",
                "unit": "$/kW"
              },
              {
                "default_value": 75,
                "label": "Fixed Operating Cost",
                "max_value": 7.054216458492963,
                "maximizing_value": 97.5,
                "min_value": 6.728058598088527,
                "minimizing_value": 52.5,
                "name": "fom",
                "unit": "$/kW/yr"
              },
              {
                "default_value": 90,
                "label": "Asset Capacity Factor",
                "max_value": 6.5498563488965145,
                "maximizing_value": 117,
                "min_value": 7.524945432880029,
                "minimizing_value": 62.99999999999999,
                "name": "capacity_factor",
                "unit": "%"
              },
              {
                "default_value": 0.75,
                "label": "Capital Cost Scaling Factor",
                "max_value": 6.899427658286257,
                "maximizing_value": 0.9750000000000001,
                "min_value": 6.8829202340296245,
                "minimizing_value": 0.5249999999999999,
                "name": "scaling_factor",
                "unit": null
              },
              {
                "default_value": 4,
                "label": "Discount Rate",
                "max_value": 6.993170269340446,
                "maximizing_value": 5.2,
                "min_value": 6.794499658920168,
                "minimizing_value": 2.8,
                "name": "discount_rate",
                "unit": "%"
              },
              {
                "default_value": 20,
                "label": "Lifetime",
                "max_value": 6.751135212963183,
                "maximizing_value": 26,
                "min_value": 7.159174650977688,
                "minimizing_value": 14,
                "name": "lifetime",
                "unit": null
              },
              {
                "default_value": 80,
                "label": "Power Price ($/MWh)",
                "max_value": 8.262566099719317,
                "maximizing_value": 104,
                "min_value": 5.519708956862173,
                "minimizing_value": 56,
                "name": "Power_Price",
                "unit": null
              }
            ]
          },
          "table": null,
          "title": "TEA Cost Breakdown",
          "unit": "$/kg",
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
            "nodeChosen": "midstream-ngnonelectricitytransportation",
            "inputValues": {
              "mode": "Pipeline",
              "distance": "750",
              "loss_factor": "0.03"
            }
          },
          {
            "nodeChosen": "process-productionusingsmr",
            "inputValues": {
              "plant_type": "Central Plants",
              "h2_phase": "Gas",
              "co_produce_steam": "Yes",
              "model_source": "Industry data",
              "use_CCS": "No",
              "cap_percent_plant": "",
              "user_ci": "",
              "cap_percent_regen": "",
              "pipeline_miles": "",
              "H2_produced": "100000",
              "capex": "678",
              "fom": "23",
              "capacity_factor": "90",
              "scaling_factor": "0.6",
              "discount_rate": "4",
              "lifetime": "20",
              "Gas_Cost": "3",
              "storage_cost_source": "",
              "storage_cost": ""
            }
          },
          {
            "nodeChosen": "gatetoenduse-hydrogengastransportation",
            "inputValues": {
              "mode": "default mix",
              "distance": "750",
              "loss": "0"
            }
          },
          {"nodeChosen": "enduse-hydrogen", "inputValues": {}}
        ],
        "customInputValues": {
          "startWith": "product",
          "selectedProduct": "Chemical",
          "selectedProductType": "Hydrogen",
          "selectedResource": "Natural Gas",
          "additionalBackendInputValues": {"compute_cost": true},
          "dataSourcesChosen": [null, null, null, null, null, null]
        }
      },
    },
  },
  {
    "type": "lca-tea",
    "name": "Blue Hydrogen",
    "createdAt": new Date("2022-03-14T19:55:50.368Z"),
    focusedInputs: ['loss_factor', 'distance', 'user_ngprice'],
    "data": {
      "analysisResult": {
        "LCA": {
          "columns": ["value", "stage", "sub_stage", "pathway"],
          "data": [
            [0, "Enduse", "aggregate", "New Case 1"],
            [4.927644999999999, "GateToEnduse", "aggregate", "New Case 1"],
            [19.07238439207447, "Process", "aggregate", "New Case 1"],
            [4.4205119999999996, "Midstream", "aggregate", "New Case 1"],
            [3.462364, "Upstream", "Processing", "New Case 1"],
            [0.805, "Upstream", "Processing: Non-Combustion ", "New Case 1"],
            [10.642413999999999, "Upstream", "Recovery", "New Case 1"]
          ],
          "params": {"indicator": "GWP"},
          "sensitivity": {
            "base_value": 107.23521900000001,
            "inputs": [
              {
                "default_value": 750,
                "label": "Distance, Process to Use (mi)",
                "max_value": 108.71352500000002,
                "maximizing_value": 975,
                "min_value": 105.75688500000003,
                "minimizing_value": 525,
                "name": "distance",
                "unit": null
              },
              {
                "default_value": 0,
                "label": "Loss, Process to Use (%)",
                "max_value": 107.23521900000001,
                "maximizing_value": 0,
                "min_value": 107.23521900000001,
                "minimizing_value": 0,
                "name": "loss",
                "unit": null
              },
              {
                "default_value": 750,
                "label": "Distance, Upstream to Process",
                "max_value": 108.40421900000003,
                "maximizing_value": 975,
                "min_value": 106.06645600000002,
                "minimizing_value": 525,
                "name": "distance",
                "unit": "mi"
              },
              {
                "default_value": 0.0225932,
                "label": "Loss, Upstream to Process",
                "max_value": 107.236101,
                "maximizing_value": 0.02937116,
                "min_value": 107.234335,
                "minimizing_value": 0.01581524,
                "name": "loss_factor",
                "unit": "%"
              },
              {
                "default_value": "Mix (~50/50 Conventional/Shale)",
                "label": "Natural Gas Type",
                "max_value": 107.469254,
                "maximizing_value": "Shale",
                "min_value": 106.98134500000002,
                "minimizing_value": "Conventional",
                "name": "ng_type",
                "unit": null
              },
              {
                "default_value": "Yes",
                "label": "Count Emissions from Building Well Infrastructure",
                "max_value": 107.23521900000001,
                "maximizing_value": "Yes",
                "min_value": 105.57742900000001,
                "minimizing_value": "No",
                "name": "well_infrastructure",
                "unit": null
              },
              {
                "default_value": "EPA 2019",
                "label": "Methane Leakage Parameter",
                "max_value": 110.375871,
                "maximizing_value": "EDF 2019",
                "min_value": 107.23521900000001,
                "minimizing_value": "EPA 2019",
                "name": "leakage_param",
                "unit": null
              }
            ]
          },
          "title": "Lifecycle GHG Emissions",
          "unit": "gCO₂e/MJ",
          "value": "MJ"
        },
        "TEA": {
          "columns": [
            "value",
            "cost_category",
            "cost_category_by_parts",
            "pathway"
          ],
          "data": [
            [0.40375959754087165, "Capital", "Capital", "Hydrogen"],
            [0.1822226652012477, "Fixed", "Fixed", "Hydrogen"],
            [
              0.6389940388808818,
              "Fuel (gas or power)",
              "Fuel (gas or power)",
              "Hydrogen"
            ],
            [
              0.19178658521824146,
              "Non-fuel variable",
              "Non-fuel variable",
              "Hydrogen"
            ],
            [0.8046699999999999, "H2 transport", "H2 transport", "Hydrogen"],
            [0.0983553303847854, "CO2 transport", "CO2 transport", "Hydrogen"],
            [0.0655702202565236, "CO2 storage", "CO2 storage", "Hydrogen"]
          ],
          "sensitivity": {
            "base_value": 6.891137528290745,
            "inputs": [
              {
                "default_value": 57.2,
                "label": "Hydrogen Production Efficiency",
                "max_value": 8.62904028093136,
                "maximizing_value": 74.36,
                "min_value": 5.137104287142048,
                "minimizing_value": 40.04,
                "name": "effic",
                "unit": "kWh/kg_H₂"
              },
              {
                "default_value": 750,
                "label": "Distance, Process to Use",
                "max_value": 7.132538528290745,
                "maximizing_value": 975,
                "min_value": 6.649736528290745,
                "minimizing_value": 525,
                "name": "distance",
                "unit": "mi"
              },
              {
                "default_value": 300,
                "label": "Hydrogen Production Rate",
                "max_value": 6.831759565213471,
                "maximizing_value": 390,
                "min_value": 6.978367333279849,
                "minimizing_value": 210,
                "name": "H2_produced",
                "unit": "m³/hr"
              },
              {
                "default_value": 1771,
                "label": "Capital Cost",
                "max_value": 7.171724131301025,
                "maximizing_value": 2302.3,
                "min_value": 6.610550925280465,
                "minimizing_value": 1239.6999999999998,
                "name": "capex",
                "unit": "$/kW"
              },
              {
                "default_value": 75,
                "label": "Fixed Operating Cost",
                "max_value": 7.054216458492963,
                "maximizing_value": 97.5,
                "min_value": 6.728058598088527,
                "minimizing_value": 52.5,
                "name": "fom",
                "unit": "$/kW/yr"
              },
              {
                "default_value": 90,
                "label": "Asset Capacity Factor",
                "max_value": 6.5498563488965145,
                "maximizing_value": 117,
                "min_value": 7.524945432880029,
                "minimizing_value": 62.99999999999999,
                "name": "capacity_factor",
                "unit": "%"
              },
              {
                "default_value": 0.75,
                "label": "Capital Cost Scaling Factor",
                "max_value": 6.899427658286257,
                "maximizing_value": 0.9750000000000001,
                "min_value": 6.8829202340296245,
                "minimizing_value": 0.5249999999999999,
                "name": "scaling_factor",
                "unit": null
              },
              {
                "default_value": 4,
                "label": "Discount Rate",
                "max_value": 6.993170269340446,
                "maximizing_value": 5.2,
                "min_value": 6.794499658920168,
                "minimizing_value": 2.8,
                "name": "discount_rate",
                "unit": "%"
              },
              {
                "default_value": 20,
                "label": "Lifetime",
                "max_value": 6.751135212963183,
                "maximizing_value": 26,
                "min_value": 7.159174650977688,
                "minimizing_value": 14,
                "name": "lifetime",
                "unit": null
              },
              {
                "default_value": 80,
                "label": "Power Price ($/MWh)",
                "max_value": 8.262566099719317,
                "maximizing_value": 104,
                "min_value": 5.519708956862173,
                "minimizing_value": 56,
                "name": "Power_Price",
                "unit": null
              }
            ]
          },
          "table": null,
          "title": "TEA Cost Breakdown",
          "unit": "$/kg",
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
            "nodeChosen": "midstream-ngnonelectricitytransportation",
            "inputValues": {
              "mode": "Pipeline",
              "distance": "750",
              "loss_factor": "0.03"
            }
          },
          {
            "nodeChosen": "process-productionusingsmr",
            "inputValues": {
              "plant_type": "Central Plants",
              "h2_phase": "Gas",
              "co_produce_steam": "Yes",
              "model_source": "Industry data",
              "use_CCS": "Yes",
              "cap_percent_plant": "85",
              "user_ci": "460",
              "cap_percent_regen": "85",
              "pipeline_miles": "240",
              "H2_produced": "100000",
              "capex": "678",
              "fom": "23",
              "capacity_factor": "90",
              "scaling_factor": "0.6",
              "discount_rate": "4",
              "lifetime": "20",
              "Gas_Cost": "3",
              "storage_cost_source": "Default",
              "storage_cost": ""
            }
          },
          {
            "nodeChosen": "gatetoenduse-hydrogengastransportation",
            "inputValues": {
              "mode": "default mix",
              "distance": "750",
              "loss": "0"
            }
          },
          {"nodeChosen": "enduse-hydrogen", "inputValues": {}}
        ],
        "customInputValues": {
          "startWith": "product",
          "selectedProduct": "Chemical",
          "selectedProductType": "Hydrogen",
          "selectedResource": "Natural Gas",
          "additionalBackendInputValues": {"compute_cost": true},
          "dataSourcesChosen": [null, null, null, null, null, null]
        }
      },
    },
  },
  {
    "type": "lca-tea",
    "name": "Electrolytic Hydrogen",
    "createdAt": new Date("2022-03-14T20:04:23.674Z"),
    focusedInputs: ['capacity_factor', 'distance'],
    "data": {
      "analysisResult": {
        "LCA": {
          "columns": ["value", "stage", "sub_stage", "pathway"],
          "data": [
            [0, "Enduse", "aggregate", "New Case 1"],
            [4.927644999999999, "GateToEnduse", "aggregate", "New Case 1"],
            [
              13.842505999999998,
              "Process",
              "G.H2 Compression and Precooling",
              "New Case 1"
            ],
            [180.202105, "Process", "G.H2 Production", "New Case 1"],
            [0, "Upstream", "aggregate", "New Case 1"]
          ],
          "params": {"indicator": "GWP"},
          "sensitivity": {
            "base_value": 198.972256,
            "inputs": [
              {
                "default_value": 750,
                "label": "Distance, Process to Use (mi)",
                "max_value": 200.450562,
                "maximizing_value": 975,
                "min_value": 197.493922,
                "minimizing_value": 525,
                "name": "distance",
                "unit": null
              },
              {
                "default_value": 0,
                "label": "Loss, Process to Use (%)",
                "max_value": 198.972256,
                "maximizing_value": 0,
                "min_value": 198.972256,
                "minimizing_value": 0,
                "name": "loss",
                "unit": null
              }
            ]
          },
          "title": "Lifecycle GHG Emissions",
          "unit": "gCO₂e/MJ",
          "value": "MJ"
        },
        "TEA": {
          "columns": [
            "value",
            "cost_category",
            "cost_category_by_parts",
            "pathway"
          ],
          "data": [
            [0.782231712180645, "Capital", "Capital", "Hydrogen"],
            [0.42834751839649166, "Fixed", "Fixed", "Hydrogen"],
            [
              3.6022312907071368,
              "Fuel (gas or power)",
              "Fuel (gas or power)",
              "Hydrogen"
            ],
            [
              0.036153846153846154,
              "Non-fuel variable",
              "Non-fuel variable",
              "Hydrogen"
            ],
            [0.8046699999999999, "H2 transport", "H2 transport", "Hydrogen"],
            [0, "CO2 transport", "CO2 transport", "Hydrogen"],
            [0, "CO2 storage", "CO2 storage", "Hydrogen"]
          ],
          "sensitivity": {
            "base_value": 6.891137528290745,
            "inputs": [
              {
                "default_value": 57.2,
                "label": "Hydrogen Production Efficiency",
                "max_value": 8.62904028093136,
                "maximizing_value": 74.36,
                "min_value": 5.137104287142048,
                "minimizing_value": 40.04,
                "name": "effic",
                "unit": "kWh/kg_H₂"
              },
              {
                "default_value": 750,
                "label": "Distance, Process to Use",
                "max_value": 7.132538528290745,
                "maximizing_value": 975,
                "min_value": 6.649736528290745,
                "minimizing_value": 525,
                "name": "distance",
                "unit": "mi"
              },
              {
                "default_value": 300,
                "label": "Hydrogen Production Rate",
                "max_value": 6.831759565213471,
                "maximizing_value": 390,
                "min_value": 6.978367333279849,
                "minimizing_value": 210,
                "name": "H2_produced",
                "unit": "m³/hr"
              },
              {
                "default_value": 1771,
                "label": "Capital Cost",
                "max_value": 7.171724131301025,
                "maximizing_value": 2302.3,
                "min_value": 6.610550925280465,
                "minimizing_value": 1239.6999999999998,
                "name": "capex",
                "unit": "$/kW"
              },
              {
                "default_value": 75,
                "label": "Fixed Operating Cost",
                "max_value": 7.054216458492963,
                "maximizing_value": 97.5,
                "min_value": 6.728058598088527,
                "minimizing_value": 52.5,
                "name": "fom",
                "unit": "$/kW/yr"
              },
              {
                "default_value": 90,
                "label": "Asset Capacity Factor",
                "max_value": 6.5498563488965145,
                "maximizing_value": 117,
                "min_value": 7.524945432880029,
                "minimizing_value": 62.99999999999999,
                "name": "capacity_factor",
                "unit": "%"
              },
              {
                "default_value": 0.75,
                "label": "Capital Cost Scaling Factor",
                "max_value": 6.899427658286257,
                "maximizing_value": 0.9750000000000001,
                "min_value": 6.8829202340296245,
                "minimizing_value": 0.5249999999999999,
                "name": "scaling_factor",
                "unit": null
              },
              {
                "default_value": 4,
                "label": "Discount Rate",
                "max_value": 6.993170269340446,
                "maximizing_value": 5.2,
                "min_value": 6.794499658920168,
                "minimizing_value": 2.8,
                "name": "discount_rate",
                "unit": "%"
              },
              {
                "default_value": 20,
                "label": "Lifetime",
                "max_value": 6.751135212963183,
                "maximizing_value": 26,
                "min_value": 7.159174650977688,
                "minimizing_value": 14,
                "name": "lifetime",
                "unit": null
              },
              {
                "default_value": 80,
                "label": "Power Price ($/MWh)",
                "max_value": 8.262566099719317,
                "maximizing_value": 104,
                "min_value": 5.519708956862173,
                "minimizing_value": 56,
                "name": "Power_Price",
                "unit": null
              },
              {
                "default_value": "PEM",
                "label": "Production Type",
                "max_value": 6.891137528290745,
                "maximizing_value": "PEM",
                "min_value": 6.586918482092183,
                "minimizing_value": "Alk",
                "name": "pt",
                "unit": null
              },
              {
                "default_value": "Gas",
                "label": "Hydrogen Phase",
                "max_value": 7.884467528290745,
                "maximizing_value": "Liquid",
                "min_value": 6.891137528290745,
                "minimizing_value": "Gas",
                "name": "state",
                "unit": null
              }
            ]
          },
          "table": null,
          "title": "TEA Cost Breakdown",
          "unit": "$/kg",
          "value": "Cost"
        }
      },
      "inputValues": {},
      "customData": {
        "inputValuesByStage": [
          {"nodeChosen": "upstream-electricity", "inputValues": {}},
          {"nodeChosen": null, "inputValues": {}},
          {"nodeChosen": null, "inputValues": {}},
          {
            "nodeChosen": "process-productionusingelectrolysis",
            "inputValues": {
              "plant_type": "Central Plants",
              "h2_phase": "Gas",
              "co_produce_steam": "No",
              "model_source": "Industry data",
              "power_source": "US Grid Average",
              "custom_power_source_ci": "",
              "pt": "PEM",
              "H2_produced": "300",
              "capex": "1771",
              "fom": "75",
              "capacity_factor": "90",
              "scaling_factor": "0.75",
              "discount_rate": "4",
              "lifetime": "20",
              "Gas_Cost": "",
              "Power_Price": "80"
            }
          },
          {
            "nodeChosen": "gatetoenduse-hydrogengastransportation",
            "inputValues": {
              "mode": "default mix",
              "distance": "750",
              "loss": "0"
            }
          },
          {"nodeChosen": "enduse-hydrogen", "inputValues": {}}
        ],
        "customInputValues": {
          "startWith": "product",
          "selectedProduct": "Chemical",
          "selectedProductType": "Hydrogen",
          "selectedResource": "Electricity",
          "additionalBackendInputValues": {"compute_cost": true},
          "dataSourcesChosen": [null, null, null, null, null, null]
        }
      },
    },
  },
  {
    "type": "lca-tea",
    "name": "Green Hydrogen",
    "createdAt": new Date("2022-03-14T19:58:49.670Z"),
    focusedInputs: ['capacity_factor', 'distance'],
    "data": {
      "analysisResult": {
        "LCA": {
          "columns": ["value", "stage", "sub_stage", "pathway"],
          "data": [
            [0, "Enduse", "aggregate", "New Case 3"],
            [4.927644999999999, "GateToEnduse", "aggregate", "New Case 3"],
            [
              0.6344481916666667,
              "Process",
              "G.H2 Compression and Precooling",
              "New Case 3"
            ],
            [8.259263145833332, "Process", "G.H2 Production", "New Case 3"],
            [0, "Upstream", "aggregate", "New Case 3"]
          ],
          "params": {"indicator": "GWP"},
          "sensitivity": {
            "base_value": 198.972256,
            "inputs": [
              {
                "default_value": 750,
                "label": "Distance, Process to Use (mi)",
                "max_value": 200.450562,
                "maximizing_value": 975,
                "min_value": 197.493922,
                "minimizing_value": 525,
                "name": "distance",
                "unit": null
              },
              {
                "default_value": 0,
                "label": "Loss, Process to Use (%)",
                "max_value": 198.972256,
                "maximizing_value": 0,
                "min_value": 198.972256,
                "minimizing_value": 0,
                "name": "loss",
                "unit": null
              }
            ]
          },
          "title": "Lifecycle GHG Emissions",
          "unit": "gCO₂e/MJ",
          "value": "MJ"
        },
        "TEA": {
          "columns": [
            "value",
            "cost_category",
            "cost_category_by_parts",
            "pathway"
          ],
          "data": [
            [0.782231712180645, "Capital", "Capital", "Hydrogen"],
            [0.42834751839649166, "Fixed", "Fixed", "Hydrogen"],
            [
              3.6022312907071368,
              "Fuel (gas or power)",
              "Fuel (gas or power)",
              "Hydrogen"
            ],
            [
              0.036153846153846154,
              "Non-fuel variable",
              "Non-fuel variable",
              "Hydrogen"
            ],
            [0.8046699999999999, "H2 transport", "H2 transport", "Hydrogen"],
            [0, "CO2 transport", "CO2 transport", "Hydrogen"],
            [0, "CO2 storage", "CO2 storage", "Hydrogen"]
          ],
          "sensitivity": {
            "base_value": 6.891137528290745,
            "inputs": [
              {
                "default_value": 57.2,
                "label": "Hydrogen Production Efficiency",
                "max_value": 8.62904028093136,
                "maximizing_value": 74.36,
                "min_value": 5.137104287142048,
                "minimizing_value": 40.04,
                "name": "effic",
                "unit": "kWh/kg_H₂"
              },
              {
                "default_value": 750,
                "label": "Distance, Process to Use",
                "max_value": 7.132538528290745,
                "maximizing_value": 975,
                "min_value": 6.649736528290745,
                "minimizing_value": 525,
                "name": "distance",
                "unit": "mi"
              },
              {
                "default_value": 300,
                "label": "Hydrogen Production Rate",
                "max_value": 6.831759565213471,
                "maximizing_value": 390,
                "min_value": 6.978367333279849,
                "minimizing_value": 210,
                "name": "H2_produced",
                "unit": "m³/hr"
              },
              {
                "default_value": 1771,
                "label": "Capital Cost",
                "max_value": 7.171724131301025,
                "maximizing_value": 2302.3,
                "min_value": 6.610550925280465,
                "minimizing_value": 1239.6999999999998,
                "name": "capex",
                "unit": "$/kW"
              },
              {
                "default_value": 75,
                "label": "Fixed Operating Cost",
                "max_value": 7.054216458492963,
                "maximizing_value": 97.5,
                "min_value": 6.728058598088527,
                "minimizing_value": 52.5,
                "name": "fom",
                "unit": "$/kW/yr"
              },
              {
                "default_value": 90,
                "label": "Asset Capacity Factor",
                "max_value": 6.5498563488965145,
                "maximizing_value": 117,
                "min_value": 7.524945432880029,
                "minimizing_value": 62.99999999999999,
                "name": "capacity_factor",
                "unit": "%"
              },
              {
                "default_value": 0.75,
                "label": "Capital Cost Scaling Factor",
                "max_value": 6.899427658286257,
                "maximizing_value": 0.9750000000000001,
                "min_value": 6.8829202340296245,
                "minimizing_value": 0.5249999999999999,
                "name": "scaling_factor",
                "unit": null
              },
              {
                "default_value": 4,
                "label": "Discount Rate",
                "max_value": 6.993170269340446,
                "maximizing_value": 5.2,
                "min_value": 6.794499658920168,
                "minimizing_value": 2.8,
                "name": "discount_rate",
                "unit": "%"
              },
              {
                "default_value": 20,
                "label": "Lifetime",
                "max_value": 6.751135212963183,
                "maximizing_value": 26,
                "min_value": 7.159174650977688,
                "minimizing_value": 14,
                "name": "lifetime",
                "unit": null
              },
              {
                "default_value": 80,
                "label": "Power Price ($/MWh)",
                "max_value": 8.262566099719317,
                "maximizing_value": 104,
                "min_value": 5.519708956862173,
                "minimizing_value": 56,
                "name": "Power_Price",
                "unit": null
              },
              {
                "default_value": "PEM",
                "label": "Production Type",
                "max_value": 6.891137528290745,
                "maximizing_value": "PEM",
                "min_value": 6.586918482092183,
                "minimizing_value": "Alk",
                "name": "pt",
                "unit": null
              },
              {
                "default_value": "Gas",
                "label": "Hydrogen Phase",
                "max_value": 7.884467528290745,
                "maximizing_value": "Liquid",
                "min_value": 6.891137528290745,
                "minimizing_value": "Gas",
                "name": "state",
                "unit": null
              }
            ]
          },
          "table": null,
          "title": "TEA Cost Breakdown",
          "unit": "$/kg",
          "value": "Cost"
        }
      },
      "inputValues": {},
      "customData": {
        "inputValuesByStage": [
          {"nodeChosen": "upstream-electricity", "inputValues": {}},
          {"nodeChosen": null, "inputValues": {}},
          {"nodeChosen": null, "inputValues": {}},
          {
            "nodeChosen": "process-productionusingelectrolysis",
            "inputValues": {
              "plant_type": "Central Plants",
              "h2_phase": "Gas",
              "co_produce_steam": "No",
              "model_source": "Industry data",
              "power_source": "Renewable / Nuclear Electricity",
              "custom_power_source_ci": "",
              "pt": "PEM",
              "H2_produced": "300",
              "capex": "1771",
              "fom": "75",
              "capacity_factor": "90",
              "scaling_factor": "0.75",
              "discount_rate": "4",
              "lifetime": "20",
              "Gas_Cost": "",
              "Power_Price": "80"
            }
          },
          {
            "nodeChosen": "gatetoenduse-hydrogengastransportation",
            "inputValues": {
              "mode": "default mix",
              "distance": "750",
              "loss": "0"
            }
          },
          {"nodeChosen": "enduse-hydrogen", "inputValues": {}}
        ],
        "customInputValues": {
          "startWith": "product",
          "selectedProduct": "Chemical",
          "selectedProductType": "Hydrogen",
          "selectedResource": "Electricity",
          "additionalBackendInputValues": {"compute_cost": true},
          "dataSourcesChosen": [null, null, null, null, null, null]
        }
      },
    },
  },
]