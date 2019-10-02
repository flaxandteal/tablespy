import sys
from .inspection import Inspection

class Printer:
    def print_inspection(self, inspection: Inspection):
        for ix, row in inspection.rows.items():
            print(ix, row['title']['text'], row['title']['loc'], row['lower-left'], row['header-boundary'], row['upper-right'])

    def print_ascii_art(self, inspection: Inspection):
        for i in range(inspection.shape[0]):
            for j in range(inspection.shape[1]):
                intable = False
                for x, region2 in inspection.rows.items():
                    if i >= region2['lower-left'][0] and i <= region2['upper-right'][0] and \
                            j >= region2['lower-left'][1] and j <= region2['upper-right'][1]:
                        if i >= region2['lower-left'][0] and i <= region2['header-boundary'][0] and \
                                j >= region2['lower-left'][1] and j <= region2['header-boundary'][1]:
                            sys.stdout.write(str(x))
                        else:
                            sys.stdout.write('.')
                        intable = True
                if not intable:
                    sys.stdout.write(' ')
            sys.stdout.write('\n')
