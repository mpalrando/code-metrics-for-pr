#!/usr/bin/env python3

import sys
from sz import gen_stats, FileStats
from tabulate import tabulate


class RefDiff:
  def __init__(self, base: list[FileStats], other: list[FileStats], unchanged=False):
    self.base_files, self.other_files = base, other

    self.base_files_set = dict({f.name: f for f in base})
    self.base_total_lc = sum(f.lines_count for f in base)

    self.other_files_set = dict({f.name: f for f in other})
    self.other_total_lc = sum(f.lines_count for f in other)

    self._modified = self.modified(unchanged)
    self._added = self.added()
    self._deleted = self.deleted()

  def format(self, files: list[dict], op: str):
    return [{**f, **{"diff": f'{f["diff"]:+}', "op": op}} for f in files]

  def changes_table(self):
    changes = (self.format(self._modified, "M")
               + self.format(self._added, "A")
               + self.format(self._deleted, "D"))
    return tabulate(changes, headers="keys", floatfmt=".1f", colalign=("left",) + ("right",) * 4)

  def files_line_count_diff(self, name: str):
    base_lc = self.base_files_set.get(name).lines_count
    other_lc = self.other_files_set.get(name).lines_count
    return base_lc - other_lc

  def modified(self, unchanged):
    files = []
    for f in self.base_files:
      if f.name in self.other_files_set:
        diff = self.files_line_count_diff(f.name)
        if unchanged or diff != 0:
          files.append({**f.format(), **{"diff": diff}})
    return files

  def added(self):
    files = []
    for f in self.other_files:
      if f.name not in self.base_files_set:
        files.append({**f.format(), **{"diff": f.lines_count}})
    return files

  def deleted(self):
    files = []
    for f in self.base_files:
      if f.name not in self.other_files_set:
        files.append({**f.format(), **{"diff": -f.lines_count}})
    return files


if __name__ == '__main__':
  base, pr = gen_stats(sys.argv[1]), gen_stats(sys.argv[2])
  diff = RefDiff(base, pr, unchanged=False)

  print(diff.changes_table(), "\n")
  print(f"total line count: {diff.base_total_lc} ({diff.other_total_lc-diff.base_total_lc:+})")
