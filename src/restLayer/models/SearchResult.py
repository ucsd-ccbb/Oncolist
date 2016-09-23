__author__ = 'aarongary'

class SearchResultModel():
    def __init__(self):
        self.clusterNodeName = ''
        self.searchTab = ''
        self.geneScoreRangeMax = 100
        self.geneSuperList = []
        self.items = []
        self.geneScoreRangeStep = 0.1
        self.geneScoreRangeMin = 5
        self.searchGroupTitle = ''
        self.grouped_items = []

    def loadTestData(self):
        self.clusterNodeName = 'Test cluster node name'
        self.searchTab = 'Test search tab'
        self.geneScoreRangeMax = 99
        self.geneSuperList = []
        self.items = []
        self.geneScoreRangeStep = 0.5
        self.geneScoreRangeMin = 50
        self.searchGroupTitle = 'Test search group title'
        self.grouped_items = []

    def toJson(self):
        return_value = {
            'clusterNodeName': self.clusterNodeName,
            'searchTab': self.searchTab,
            'geneScoreRangeMax': self.geneScoreRangeMax,
            'geneSuperList': self.geneSuperList,
            'items': self.items,
            'geneScoreRangeStep': self.geneScoreRangeStep,
            'geneScoreRangeMin': self.geneScoreRangeMin,
            'searchGroupTitle': self.searchGroupTitle,
            'grouped_items': self.grouped_items
        }

        return return_value
