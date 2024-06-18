const randomIntInRange = (min = 0, max) => {
  return Math.floor(Math.random() * (max - min)) + min;
}

export const chooseRandomSelectOptionBySelector = (selector) => {
  cy.get(selector).children(':enabled').then((options) => {
    // get random option
    // console.log(options);
    // console.log(options[0])
    // filter out disabled options
    // console.log(options.map(option => option.disabled))
    // let enabledOptions = options.filter(option => !option.disabled);
    // console.log(enabledOptions)

    const randomIndex = randomIntInRange(0, options.length)
    const randomOptionValue = options[randomIndex].value;
    cy.get(selector).select(randomOptionValue)
  })
}

export const getSelect = (id) => {
  return getInput('select-' + id);
}

export const getSelectForCaseIndex = (id, caseIndex) => {
  return cy.get(`#inputs--case-${caseIndex} #user-inputs--select-${id}`);
}

export const getInput = (id) => {
  return cy.get('#user-inputs--' + id);
}

export const getInputAtCaseIndex = (id, comparisonIndex) => {
  return cy.get(`#inputs--case-${comparisonIndex} #user-inputs--${id}`);
}

export const setInputTo = (id, value) => {
  return getInput(id).type('{selectall}').type(value);
}

export const setSelectTo = (id, value) => {
  return getSelect(id).select(value)
}

export const clickToggle = (id) => {
  return cy.get(`#toggle--${id}`).click({force: true})
}

export const clickToggleAtIndex = (id, index) => {
  return cy.get(`#inputs--case-${index} #toggle--${id}`).click({force: true})
}

export const runCaseAtIndex = (index) => {
  cy.get('#run-' + (index)).click()
}

export const runAllCases = () => {
  cy.get('#run-all').click()
}

export const saveBatchWithName = (name, opts) => {
  cy.window().then(function(win) {
    if (win.prompt.restore) {
      win.prompt.restore()
    }
    cy.stub(win, 'prompt').returns(name);
    cy.get('#save-batch').click(opts);
    cy.wait(1000)
  });
}

export const loadCaseAtIndexWithName = (index, name) => {
  cy.get('#saved-case-menu-' + index + ' button').click();
  cy.get('#saved-case-menu-' + index + ' .saved-case-dropdown .saved-case-menu-item a').contains(name).click();
}

export const saveCaseAtIndexWithName = (index, name, opts) => {
  cy.window().then(function(win) {
    if (win.prompt.restore) {
      win.prompt.restore()
    }
    cy.stub(win, 'prompt').returns(name);
    cy.get('#save-' + index).click(opts);
  });
}

export const duplicateCaseAtIndex = (index) => {
  cy.get('#duplicate-case-' + index).click();
  cy.wait(500);
}

export const addCase = () => {
  cy.get('#add-compare-col').click();
}

export const checkYAxisLockingForNCharts = (numCharts) => {
  for (let i = 0; i < numCharts; i++) {
    // get top yAxis label, make sure its text equals the top yAxis label of the corresponding chart in the next case
    cy.get('.highcharts-container')
    .eq(i*2).find('.highcharts-yaxis-labels text')
    .last()
    .invoke('text')
    .then((yMax1) => {
      cy.get('.highcharts-container')
      .eq(i*2 + 1)
      .find('.highcharts-yaxis-labels text')
      .last()
      .invoke('text')
      .should('equal', yMax1);
    })
  }
}

export const expectNCharts = (numCharts) => {
  cy.get('.highcharts-container').should('have.length', numCharts);
}

export const stubLogin = () => {
  beforeEach(() => {
    window.localStorage.setItem("authToken", '"definitelyloggedin!"');
    // cy.visit('/app')
  })
}

export const stubUserProfile = () => {
  beforeEach(() => {
    cy.intercept(`http://127.0.0.1:5000/users/current`,
    {name: 'Luke Skywalker', institution: 'The Jedi'})
  })
}

export const clearDatabase = () => {
  indexedDB.deleteDatabase('SESAME_DB');
}

export const interceptAnalysis = (url) => {
  cy.intercept({
    method: 'POST',
    url,
  }).as('runAnalysis')
}

export const waitForAnalysis = () => {
  cy.wait('@runAnalysis')
}

export const openAccordion = (id) => {
  cy.get(`#accordion--${id}`).then($p => {
    const className = $p[0].className
    cy.log($p, className)
    if (className.includes('accordion-closed')) {
      cy.log('closed')
      cy.wrap($p).click()
    } else {
      cy.log('already open')
    }
  })
}

export const openAccordionAtIndex = (id, index) => {
  cy.get(`#inputs--case-${index} #accordion--${id}`).click()
}

export const expectAccordionAtIndexToHaveOpenState = (id, index, isOpen) => {
  cy.get(`#inputs--case-${index} #accordion--${id}`).should('have.class', `accordion-${isOpen ? 'open' : 'closed'}`)
}

export const clickButtonAndEnterPromptValue = (buttonId, value) => {
  cy.window().then(function(win) {
    if (win.prompt.restore) {
      win.prompt.restore()
    }
    cy.stub(win, 'prompt').returns(value)
    cy.get(buttonId).click()
  })
}

export const testBatchSaving = () => {
  cy.get('#accordion--inputs').scrollIntoView().click({force: true})
  const name = 'Batch Test'
  saveBatchWithName(name)
  cy.wait(2000)
  cy.get('.saved-batch-name').should('have.text', name)
  // Test auto-incrementing names
  cy.get('.saved-case-name').eq(0).should('have.text', `${name} 1`)
  cy.get('.saved-case-name').eq(1).should('have.text', `${name} 2`)
  cy.get('.saved-case-name').eq(2).should('have.text', `${name} 3`)
}