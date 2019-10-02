# Tablespy

Tablespy is a tool to find tables in [tabulator](https://pypi.org/project/tabulator/) compatible files.

Usage:

```
tablespy [--art] [--sheet=N] FILENAME

Options:
-------

  --art     Print ASCII art image of sheets
  --sheet=N Show the Nth sheet only
```

## API

Tablespy also provides a couple of handy routines to access this information programmatically.

### Inspector

```
from tablespy.inspector import Inspector

inspector = Inspector()

# Create pandas dataframe
...

inspection = inspector.inspect_df(df)

print(inspection.regions)
```
