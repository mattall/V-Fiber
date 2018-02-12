import geni.aggregate.exogeni as EGAM

for am in EGAM.aggregates():
    print am.name
    print am.amtype
    print am.api
    print am.url
    print am.listresources
