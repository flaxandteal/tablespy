from .inspection import Inspection
import numpy as np
import skimage
import skimage.measure
from tabulator import Stream, exceptions
import pandas as p
import xlrd

MIN_COLS = 2
MAX_TITLE_COLS = 3
MIN_ROWS = 2
MAX_ROWS_TO_HEADINGS = 3
MAX_HEADING_GAP_TOLERANCE = 1
MIN_HEADING_CONTENT = 3

class Inspector:
    def __init__(self, infile=None):
        self.infile = infile

    def region_iter(self, **kwargs):
        for inspection, df, sheet in self.inspect_iter(return_df=True, **kwargs):
            for region in inspection.regions.values():
                region_df = df.iloc[
                    region['header-boundary'][0] + 1:region['upper-right'][0],
                    region['lower-left'][1]:region['upper-right'][1]
                ]
                region_df.columns = df.iloc[
                    region['header-boundary'][0],
                    region['lower-left'][1]:region['header-boundary'][1]
                ]
                yield region_df, region, sheet

    def inspect_iter(self, return_df=False, **kwargs) -> Inspection:
        i = 0
        while True:
            i += 1
            try:
                inspection = self.inspect(sheet=i, return_df=return_df, **kwargs)
            except exceptions.SourceError:
                break

            yield inspection

            if return_df:
                inspection, df, sheet = inspection

            if inspection.format not in ('ods', 'xls', 'xlsx'):
                break


    def inspect(self, sheet=None, return_df=False, **kwargs) -> Inspection:
        # sheet == 1 should default, as it's what we expect for non-sheet formats
        if sheet is not None and sheet != 1:
            kwargs['sheet'] = sheet
        else:
            sheet = 1

        with Stream(self.infile, **kwargs) as stream:
            data = [row for row in stream]
            fmt = stream.format

        df = p.DataFrame(data)

        inspection = self.inspect_df(df, fmt)

        if return_df:
            return inspection, df, sheet
        else:
            return inspection

    def inspect_df(self, df, fmt='df'):
        inspection = Inspection(infile=self.infile)

        df = df.replace(r'^\s*$', np.nan, regex=True).reset_index()
        df.columns = range(len(df.columns))
        df.index = range(len(df.index))

        ia, iz = df.first_valid_index(), df.last_valid_index()
        dft = df.transpose()
        ca, cz = dft.first_valid_index(), dft.last_valid_index()

        df = df.loc[ia:iz, ca:cz]

        image = df.notna().to_numpy(dtype=int)

        regions = self.region_split(image, offset=(ia, ca))

        embedded_regions = []
        for region in regions:
            for region2 in regions:
                if region == region2:
                    continue

                # Is top left of this region within the bounds of another region?
                # If so, then nested tables are a problem beyond this routine, we assume
                # that this is just a coincidentally isolated set of values in a bigger table
                if region[0][0] >= region2[0][0] and region[0][0] <= region2[2][0] and \
                        region[0][1] >= region2[0][1] and region[0][1] <= region2[2][1]:
                    embedded_regions.append(region)

        regions = set(regions) - set(embedded_regions)

        region_dict = {}
        for ix, region in enumerate(regions):
            title = region[-1]
            if title:
                title_text = '\n'.join([str(c) for c in df.loc[title[0], title[1]:title[1] + title[2] - 1]])
            else:
                title_text = None

            region_dict[ix + 1] = {
                'lower-left': region[0],
                'header-boundary': region[1],
                'upper-right': region[2],
                'title': {
                    'loc': title,
                    'text': title_text
                }
            }

        inspection.regions = region_dict
        inspection.shape = image.shape
        inspection.format = fmt

        return inspection

    def region_split(self, image, offset=(0, 0)):
        labelled_image, labels = skimage.measure.label(image, connectivity=1, return_num=True)

        regions = []
        for i in range(1, labels + 1):
            region = np.nonzero(labelled_image == i)
            lr, lc, ur, uc = min(region[0]), min(region[1]), max(region[0]), max(region[1])

            width = uc - lc + 1
            if width < MIN_COLS or ur - lr < MIN_ROWS or (width == MIN_COLS and ur - lr == MIN_ROWS):
                continue

            header_start = lr
            header_end = lr
            for i in range(ur - lr):
                row = labelled_image[lr + i]
                if np.count_nonzero(row) > width - MAX_HEADING_GAP_TOLERANCE:
                    header_end = lr + i
                    if i > MAX_ROWS_TO_HEADINGS:
                        header_start = lr + i
                        upper_regions = self.region_split(image[lr:lr+i, lc:uc], (offset[0] + lr, offset[1] + lc))
                        regions += upper_regions
                    break
                if np.count_nonzero(row) < MIN_HEADING_CONTENT:
                    header_start = lr + i + 1

            title = None
            if lr < header_start:
                in_a_row = 0
                for i in range(lc, uc):
                    if labelled_image[lr, i]:
                        if not in_a_row:
                            title = (lr + offset[0], i + offset[1], 1)
                        if in_a_row > MAX_TITLE_COLS:
                            break
                        in_a_row += 1
                    elif in_a_row:
                        title = (lr + offset[0], i - in_a_row + offset[1], in_a_row)
                        break

            regions.append((
                (header_start + offset[0], lc + offset[1]),
                (header_end + offset[0], uc + offset[1]),
                (ur + offset[0], uc + offset[1]),
                title
            ))

        return regions
