#!/usr/bin/env python3

import sys
from sz import gen_stats, FileStats
from tabulate import tabulate


class Ref:
  def __init__(self: str, files: list[FileStats]):
    self.files = files
    self.files_set = dict({f.name: f for f in files})
    self.dirs_set = dict({f.dir: f for f in files})
    self.total_lc = sum(f.lines_count for f in files)

  def file(self, name: str):
    return self.files_set.get(name, None)

  def diff(self, other: 'Ref', unchanged=False):
    return RefDiff(self, other, unchanged=unchanged)


class RefDiff:
  def __init__(self, base: Ref, other: Ref, unchanged=False):
    self.base, self.other = base, other
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

  def file_lc_diff(self, name: str):
    assert name in self.base.files_set, f"file {name} not found"
    base_lc = self.base.file(name).lines_count
    other_lc = self.other.file(name).lines_count
    return base_lc - other_lc

  def modified(self, unchanged):
    files = []
    for f in self.base.files:
      if f.name in self.other.files_set:
        lc_diff = self.file_lc_diff(f.name)
        if unchanged or lc_diff != 0:
          files.append({**f.format(), **{"diff": lc_diff}})
    return files

  def added(self):
    files = []
    for f in self.other.files:
      if f.name not in self.base.files_set:
        files.append({**f.format(), **{"diff": f.lines_count}})
    return files

  def deleted(self):
    files = []
    for f in self.base.files:
      if f.name not in self.other.files_set:
        files.append({**f.format(), **{"diff": -f.lines_count}})
    return files


if __name__ == '__main__':
  base, pr = gen_stats(sys.argv[1]), gen_stats(sys.argv[2])
  base_ref, pr_ref = Ref(base), Ref(pr)
  diff = base_ref.diff(pr_ref, unchanged=False)

  print(diff.changes_table(), "\n")
  print(f"total line count: {pr_ref.total_lc} ({pr_ref.total_lc-base_ref.total_lc:+})")
