if __name__ == '__main__':
    from analysis.system.industrial_fleet.iron_steel_projections import SteelProjection
    test = SteelProjection()
    results = test.run()
    test.plot(results)
