/// <reference types="cypress" />

const { chooseRandomSelectOptionBySelector, getInput, runCaseAtIndex, getSelect, stubLogin, setInputTo, interceptAnalysis, getSelectForCaseIndex, runAllCases, duplicateCaseAtIndex, checkYAxisLockingForNCharts, expectNCharts, saveCaseAtIndexWithName, clearDatabase, addCase, loadCaseNameAtIndex, loadCaseAtIndexWithName, getInputAtCaseIndex, waitForAnalysis, openAccordion, setSelectTo, clickToggle, clickToggleAtIndex, saveBatchWithName, testBatchSaving, openAccordionAtIndex, stubPrompt, clickButtonAndEnterPromptValue, expectAccordionAtIndexToHaveOpenState, stubUserProfile } = require("../utils/utils")

stubLogin()
stubUserProfile()
clearDatabase()

const expectAccordionToHaveNChartControls = (accordionId, numControls) => {
  cy.get('#results #accordion--' + accordionId + ' .accordion-header .figure-controls').should('have.length', numControls)
}

const testDefaults = () => {
  cy.visit('/app/costs')
  cy.get('#tea-indicators-select').select('Hydrogen')
  setSelectTo('pt', 'SMR')
  getInput('input-capex').should('have.value', 678)
  setSelectTo('pt', 'PEM')
  getInput('input-capex').should('have.value', 1771)
}

const testShareTable = () => {
  cy.visit('/app/cars')
  openAccordion('sales')
  getInput('sedan_sales_shares-iceg-2019').should('have.value', 89);
  getInput('sedan_sales_shares-bev-2050').should('have.value', 83);
  // change region, make sure base year and input year values change
  cy.wait(100)
  setSelectTo('region', 'US, California');
  cy.wait(100)
  openAccordion('sales')
  getSelect('msps2').should('have.value', 'AEO20');
  getInput('sedan_sales_shares-bev-2050').should('have.value', 20);
  // change BEV input year value, make sure projection changes to user
  setInputTo('sedan_sales_shares-bev-2050', 19);
  getSelect('msps2').should('have.value', 'User');
  getInput('sedan_sales_shares-iceg-2019').should('have.value', 76);
  // make sure input year remainder changes
  getInput('sedan_sales_shares-iceg-2050').should('have.value', 77);
  // set projection to AEO20, make sure BEV value changes back
  setSelectTo('msps2', 'AEO20');
  getInput('sedan_sales_shares-bev-2050').should('have.value', 20);
  getInput('sedan_sales_shares-iceg-2050').should('have.value', 74);
  // set projection to static - should recalc 2050 values, 
  setSelectTo('msps2', 'Static');
  getInput('sedan_sales_shares-bev-2050').should('have.value', 11);

  // test dupe
  duplicateCaseAtIndex(0)
  getInputAtCaseIndex('sedan_sales_shares-bev-2050', 1).should('have.value', 11);

  // test save and load
  interceptAnalysis('/fleet/analysis')
  runCaseAtIndex(0)
  waitForAnalysis()
  cy.wait(500)
  cy.get('#columns-wrapper').scrollTo(0, 0);
  cy.wait(500)
  saveCaseAtIndexWithName(0, 'BEV19', {force: true});
  addCase()
  loadCaseAtIndexWithName(2, 'BEV19');
  getInputAtCaseIndex('sedan_sales_shares-bev-2050', 2).should('have.value', 11);
  getInputAtCaseIndex('sedan_sales_shares-iceg-2050', 2).should('have.value', 76);
}

const runCars = () => {
  interceptAnalysis('/fleet/analysis')
  // test FGI charts showing up
  cy.visit("/app/cars")
  cy.get('#user-inputs--select-region').select('US, California')
  cy.get('#accordion--fuel-production').click()
  clickToggle('fgi')
  runCaseAtIndex(0)
  cy.wait('@runAnalysis')
  // make sure at least one power chart data point is visible
  cy.get('#accordion--power-grid-results .highcharts-series path').should('have.length.at.least', 1)

  saveCaseAtIndexWithName(0, 'US')
  cy.get('#saved-case-menu-0 .saved-case-name').should('contain.text', 'US')
  addCase()
  loadCaseAtIndexWithName(1, 'US')
  // now... make sure there are two sets of chart controls
  expectNCharts(24)
  expectAccordionToHaveNChartControls('per-distance-results', 2)
}

const runCarsMultipleCases = () => {
  // reload page
  interceptAnalysis('/fleet/analysis')
  cy.visit('/app/cars')
    
  // cy.get('#user-inputs--select-region').children().then((options) => {
  //   // get random option
  //   const randomIndex = randomIntInRange(0, options.length)
  //   const randomOptionValue = options[randomIndex].value
  //   cy.get('#user-inputs--select-region').select(randomOptionValue)
  // })

  // case 1
  openAccordion('sales')
  cy.wait(100)
  setInputTo('sedan_sales_shares-fcev-2050', 2)
  getSelect('msps2').should('have.value', 'User')

  addCase()
  addCase()

  // case 2
  // select random region
  chooseRandomSelectOptionBySelector('#inputs--case-1 #user-inputs--select-region')
  chooseRandomSelectOptionBySelector('#inputs--case-2 #user-inputs--select-region')

  runAllCases()

  // set all selects to random values
  // cy.get('#inputs--case-2 select').each(($select) => {
  //   console.log($select)
  //   chooseRandomSelectOptionBySelector($select)
  // })

  cy.wait('@runAnalysis')
  // expect inputs to be collapsed after running
  cy.get('#inputs .column-content').should('not.be.visible')
  expectNCharts(30)
  // expect one set of figure controls in per distance views
  expectAccordionToHaveNChartControls('per-distance-results', 1)
  // expect one Y axis in summary figs
  cy.get('#accordion--summary .highcharts-container').eq(0).find('.highcharts-yaxis-labels').should('have.length', 1)
  
  // test batch saving
  // cy.get('#accordion--inputs').scrollIntoView()
  // openAccordion('inputs')
  testBatchSaving()

  // saveBatchWithName('Cars Batch')
  // cy.get('.saved-batch-name').should('have.text', 'Cars Batch')
  // // Test auto-incrementing names
  // cy.get('.saved-case-name').eq(0).should('have.text', 'Cars Batch 1')
  // cy.get('.saved-case-name').eq(1).should('have.text', 'Cars Batch 2')
  // cy.get('.saved-case-name').eq(2).should('have.text', 'Cars Batch 3')
  
}

const runIndustry = () => {
  interceptAnalysis('/industry/cement/analysis')
  cy.visit("/app/industry")

  // test industry switcher
  // cy.get('#inputs--case-0').find('label').eq(0).should('include.text', 'Cement')

  // cy.get('#select-industry-module').should('include.text', 'cement')
  duplicateCaseAtIndex(0)
  // run without and with CCS
  clickToggle('ccs')
  runAllCases()
  waitForAnalysis()
  expectNCharts(6)
  checkYAxisLockingForNCharts(3)

  // test steel
  cy.get('#select-industry-module').select('steel')
  cy.get('#inputs--case-0').find('label').eq(0).should('include.text', 'steel')
  setSelectTo('route', 'Scrap-EAF (Scrap Based Electric Arc Furnace)')
  runCaseAtIndex(0)
  expectNCharts(3)

  // test aluminum
  cy.get('#select-industry-module').select('aluminum')
  cy.get('#inputs--case-0').find('label').eq(0).should('include.text', 'Aluminum')
  setSelectTo('route', 'Primary Aluminum')
  runCaseAtIndex(0)
  expectNCharts(3)

}

const runPowerGreenfield = () => {
  interceptAnalysis('/pps/analysis')
  cy.visit('/app/power-greenfield')
  cy.wait(1000)
  cy.get('#custom-alert--confirm').click()
  cy.wait(2000)
  setInputTo('demand-solar', 29)
  getInput('demand-solar').should('have.value', 29)
  // setInputTo('demand-wind', 1)
  runCaseAtIndex(0)
  cy.wait('@runAnalysis')
  expectNCharts(9)
  // cy.get('#results .highcharts-container').should('have.length', 6)
  // saving and loading case should preserve share table value
  let caseName = '29% Solar'
  saveCaseAtIndexWithName(0, caseName)
  addCase()
  cy.wait(3000)
  loadCaseAtIndexWithName(1, caseName)
  getInputAtCaseIndex('demand-solar', 1).should('have.value', 29)
}

const testDuplicateCase = () => {
  cy.visit('/app/power-greenfield')
  cy.wait(1000)
  // if (cy.get('#custom-alert--confirm').length === 1) {
  //   cy.get('#custom-alert--confirm').click()
  // }
  // cy.wait(1000)
  openAccordion('renewable-profiles')
  setInputTo('demand-solar', 3)
  duplicateCaseAtIndex(0)
  getInputAtCaseIndex('demand-solar', 1).should('have.value', 3)
  expectAccordionAtIndexToHaveOpenState('renewable-profiles', 1, true);
}

const runPathways = () => {
  interceptAnalysis('/lca/analysis')
  cy.visit('/app/build')
  setSelectTo('product', 'Electricity')
  setSelectTo('resource', 'Natural Gas')
  openAccordion('upstream')
  duplicateCaseAtIndex(0)
  // Upstream accordion should still be open in duplicated case
  expectAccordionAtIndexToHaveOpenState('upstream', 1, true);
  clickToggleAtIndex('compute-cost', 1)
  cy.wait(1000)
  getSelectForCaseIndex('leakage_param', 1).should('have.value', 'EPA 2019')
  duplicateCaseAtIndex(1)
  openAccordionAtIndex('process', 2)
  getSelectForCaseIndex('data-source', 2).select('ASPEN')
  cy.wait(1000)
  runAllCases()
  waitForAnalysis()
  cy.wait(1000)
  testBatchSaving()
  // testBatchRenaming
  const batchRenameName = 'Batch Renamed'
  clickButtonAndEnterPromptValue('.edit-savedBatches-name', batchRenameName)
  cy.get('.saved-batch-name').should('have.text', batchRenameName)
  clickButtonAndEnterPromptValue('.edit-savedBatches-name', 'Batch Test')
  cy.get('.saved-batch-name').should('have.text', 'Batch Test')


  // cy.visit('/app/saved')
  // cy.get('#select-module-lca-tea').click()
  // test rename
}

const runPower = () => {
  interceptAnalysis('/grid/analysis')
  cy.visit('/app/power')
  runCaseAtIndex(0)
  cy.wait('@runAnalysis')
  cy.get('#results .highcharts-series-group').should('have.length', 5).each(series => {
    cy.wrap(series).find('.highcharts-series path.highcharts-area').should(($paths) => {
      $paths.each((index, path) => {
        expect(path.attributes.d.nodeValue).to.have.length.greaterThan(5)
      })
    })
  })
}

const testSavedPage = () => {
  cy.visit('/app/saved')
  interceptAnalysis('/lca/analysis')

  // test "batch selected cases" button
  cy.get('#select-module-lca-tea').click()
  cy.get('#savedCases-block .select-all').click()
  // cy.get('#savedCases-block .saved-item .checkbox').click({multiple: true})
  const batchName = 'Another Batch Test'
  clickButtonAndEnterPromptValue('#savedCases-block .batch-selected', batchName)
  cy.wait(1000)
  cy.get('#savedBatches-block .saved-item').filter(`:contains(${batchName})`).should('exist').then($batchEl => {
    cy.wrap($batchEl).find('.accordion-header').click()
    cy.wrap([1,2,3]).each(num => {
      cy.wrap($batchEl).find('.saved-item').filter(`:contains(Batch Test ${num})`).should('exist')
    })
    cy.wrap($batchEl).find('.open').click()
  })
  
  // wait to go to new page and check that charts loaded properly
  expectNCharts(4)
  cy.get('#saved-batch-menu-0 .saved-batch-name').should('have.text', batchName)
  // close a case
  cy.get('#close-case-2').click()
  cy.get('#saved-batch-menu-0 .saved-batch-name').should('have.text', 'New Batch')
  // add a new case, run it, then save batch
  duplicateCaseAtIndex(1)
  runCaseAtIndex(2)
  waitForAnalysis()
  cy.wait(500)
  cy.get('#accordion--inputs').scrollIntoView().click({force: true})
  const staleFreshName = 'Batch Test Stale + Fresh';
  saveBatchWithName(staleFreshName)
  cy.get('#saved-case-menu-2 .saved-case-name').should('have.text', `${staleFreshName} 1`)
  cy.get('.saved-batch-name').should('have.text', staleFreshName)
  // back to saved page for more tests
  cy.visit('/app/saved')
  cy.get('#select-module-lca-tea').click()
  cy.wait(500) // wait for items to load from db
  // delete first saved batch from paths test
  cy.get('#savedBatches-block .saved-item').eq(0).should('have.text', 'Batch Test').find('.delete').click()
  cy.get('#custom-alert--confirm').click()
  // delete stale + fresh batch + case
  cy.wait(500)
  cy.get('#savedBatches-block .saved-item').filter(`:contains(${staleFreshName})`).find('.delete').click()
  cy.get('#custom-alert--confirm').click()
  cy.wait(500)
  cy.get('#custom-alert--confirm').click()
  // test delete new batch but keep cases
  cy.wait(500)
  cy.get('#savedBatches-block .saved-item').filter(`:contains(${batchName})`).find('.delete').click()
  cy.get('#custom-alert--confirm').click()
  cy.wait(500)
  cy.get('#custom-alert--cancel').click()
  // batch should be gone, but cases still there
  cy.get('#savedBatches-block .saved-item').should('not.exist')
  cy.wrap([1,2,3]).each(num => {
    cy.get('#savedCases-block .saved-item').filter(`:contains(Batch Test ${num})`).should('exist')
  })
  // now recreate batch
  cy.get('#savedCases-block .select-all').click()
  clickButtonAndEnterPromptValue('#savedCases-block .batch-selected', batchName)
  cy.wait(500)
  // now delete batch + member cases
  cy.get('#savedBatches-block .saved-item').filter(`:contains(${batchName})`).should('exist').find('.delete').click()
  cy.get('#custom-alert--confirm').click()
  cy.wait(500)
  cy.get('#custom-alert--confirm').click()
  // batch and member cases should no longer exist
  cy.get('#savedBatches-block .saved-item').should('not.exist')
  cy.get('#savedCases-block .saved-item').should('not.exist')
}

describe('Run Tests', () => {
  context('Pathways', () => {
    it('Runs pathway analyses', runPathways)
  })
  context('Saved', () => {
    it('Tests saved page', testSavedPage)
  })
  context('Cars', () => {
    it('Tests share table', testShareTable);
    it('Run cars analyses', runCars)
    it('Run cars multiple case analyses', runCarsMultipleCases)
  })
  context('Power Greenfield', () => {
    it('Run PPS analyses', runPowerGreenfield)
    it('Duplicate case should preserve share table value', testDuplicateCase)
  })
  context('Industry', () => {
    it('Runs cement analyses', runIndustry)
  })
  context('Power', () => {
    it('Runs power analyses', runPower)
  })
  context('Defaults', () => {
    it('Defaults should recalculate on dependent input change', testDefaults)
  });
})

