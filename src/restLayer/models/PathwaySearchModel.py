import json

class PathwaySearchResult():
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

    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)