#!/usr/bin/env python3

import sys
from sz import gen_stats
from tabulate import tabulate

if __name__ == '__main__':
  base, pr = gen_stats(sys.argv[1]), gen_stats(sys.argv[2])

  pr_dirs = {x[0].rsplit("/", 1)[0]: x[1] for x in pr}
  base_dirs = {x[0].rsplit("/", 1)[0]: x[1] for x in base}
  base_ff, pr_ff = {x[0]: x for x in base}, {x[0]: x for x in pr}
  total_base, total_pr = sum(x[1] for x in base), sum(x[1] for x in pr)

  headers = ["File", "Lines", "Tokens/Line", "Diff", ""]
  files = []
  for x in pr:
    if x[0] in base_ff:
      diff = x[1]-base_ff[x[0]][1]
      files.append([x[0], x[1], x[2], f'{diff:+}' if diff > 0 else "", "M" if diff > 0 else ""])
    else:
      files.append([x[0], x[1], x[2], f'{x[1]:+}', "A"])
  deleted = [[x[0], x[1], x[2], f'{-x[1]:+}', "D"] for x in base if x[0] not in pr_ff]
  files += deleted

  print(tabulate([headers] + files, headers="firstrow", floatfmt=".1f", colalign=("left", "right", "right", "right", "right"))+"\n")

  dirs = []
  for dir_name, group in sorted(pr_dirs.items(), key=lambda x: -x[1]):
    dirs.append([dir_name, group, f'{group-base_dirs.get(dir_name, 0):+}'])

  print(tabulate(dirs, headers=["Dir", "Lines", "Diff"], floatfmt=".1f")+"\n")
  print(f"total line count: {total_pr} ({total_pr-total_base:+})")
