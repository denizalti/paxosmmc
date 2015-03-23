from utils import PValue

class PValueSet:
    """PValueSet encloses a set of pvalues with the highest ballotnumber
    (always) and supports corresponding set functions.
    """
    def __init__(self):
        self.pvalues = {} # indexed by slot_number: pvalue

    def add(self, pvalue):
        """Adds given PValue to the PValueSet overwriting matching
        (commandnumber,proposal) if it exists and has a smaller ballotnumber
        """
        if self.pvalues.has_key(pvalue.slot_number):
            if self.pvalues[pvalue.slot_number].ballot_number < pvalue.ballot_number:
                self.pvalues[pvalue.slot_number] = pvalue
        else:
            self.pvalues[pvalue.slot_number] = pvalue

    def remove(self, pvalue):
        """Removes given pvalue"""
        del self.pvalues[pvalue.slot_number]

    def update(self, given_pvalueset):
        """Updates the pvalues of given_pvalueset with the pvalues of the
        pvalueset overwriting the slot_numbers with lower ballotnumber
        """
        for candidate in given_pvalueset.pvalues.itervalues():
            self.add(candidate)

    def __len__(self):
        """Returns the number of PValues in the PValueSet"""
        return len(self.pvalues)

    def __str__(self):
        """Returns PValueSet information"""
        return "\n".join(str(pvalue) for pvalue in self.pvalues.itervalues())
