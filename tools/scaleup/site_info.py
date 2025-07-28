#--------------------------------------------------------------------
# Copyright (c) 2014 Raytheon BBN Technologies
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and/or hardware specification (the "Work") to
# deal in the Work without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Work, and to permit persons to whom the Work
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Work.
#
# THE WORK IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE WORK OR THE USE OR OTHER DEALINGS
# IN THE WORK.
# ----------------------------------------------------------------------

"""
List stitching InstaGENI site, and total list of InstaGENI site. 

Both stitch_site and ig_site dicts should be updated if a new stitching site is added.

@author: xliu
"""

import geni.aggregate.instageni as ig
#import geni.aggregate.exogeni as eg

stitch_site = {0: ig.GPO,
               1: ig.NYSERNet,
               2: ig.Illinois,
               3: ig.MAX,
               4: ig.Missouri,
               5: ig.Utah,
               6: ig.Wisconsin,
               7: ig.Stanford,
               8: ig.UtahDDC,
               9: ig.Kentucky,
               10: ig.GATech,
               11: ig.Kansas,
               12: ig.Rutgers,
               13: ig.CaseWestern,
               14: ig.SOX,
               15: ig.NPS,
               16: ig.CENIC,
               17: ig.Chicago,
               18: ig.NYSERNet,
               19: ig.UCLA,
               20: ig.UMKC,
               21: ig.UTC,
               22: ig.UWashington,
               }
               
               
ig_site = {0: ig.GPO,
           1: ig.NYSERNet,
           2: ig.Illinois,
           3: ig.MAX,
           4: ig.Missouri,
           5: ig.Utah,
           6: ig.Wisconsin,
           7: ig.Stanford,
           8: ig.UtahDDC,
           9: ig.Kentucky,
           10: ig.GATech,
           11: ig.Kansas,
           12: ig.Rutgers,
           13: ig.CaseWestern,
           14: ig.SOX,
           15: ig.NPS,
           16: ig.CENIC,
           17: ig.Chicago,
           18: ig.NYSERNet,
           19: ig.UCLA,
           20: ig.UMKC,
           21: ig.UTC,
           22: ig.UWashington,
           23: ig.Clemson,
           24: ig.Cornell,
           25: ig.Northwestern,
           26: ig.NYU,
           27: ig.Princeton,
           28: ig.Dublin,
           29: ig.MOXI,
           30: ig.Kettering,
           31: ig.LSU,
           32: ig.Colorado,
           33: ig.NPS,
           34: ig.UKYPKS2,}




